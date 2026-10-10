import os
import sys
import shutil
from pyspark.sql import DataFrame
import pandas as pd
from src.ml.classification_models import get_classification_models
from src.ml.regression_models import get_regression_models
from src.ml.evaluate_models import evaluate_classifier, evaluate_regressor, generate_comparison_charts
from src.utils.logger import setup_logger

logger = setup_logger("TrainModelsPipeline")

def run_ml_training_pipeline(
    df_transformed: DataFrame,
    label_col: str = "congestion_numeric",
    speed_col: str = "average_speed",
    models_dir: str = "models",
    results_dir: str = "results",
    random_seed: int = 42
):
    """
    Executes end-to-end PySpark ML training, evaluation, comparison, and persistence:
      1. Train/Test split (80/20) with reproducible seed
      2. Trains 5 PySpark MLlib classification models
      3. Trains 2 PySpark MLlib regression models
      4. Evaluates all metrics (Accuracy, Precision, Recall, F1, RMSE, R2)
      5. Saves the best model pipeline and artifacts
    """
    os.makedirs(models_dir, exist_ok=True)
    metrics_dir = os.path.join(results_dir, "metrics")
    preds_dir = os.path.join(results_dir, "predictions")
    os.makedirs(metrics_dir, exist_ok=True)
    os.makedirs(preds_dir, exist_ok=True)
    
    logger.info("Splitting dataset into 80% Train and 20% Holdout Test sets...")
    train_df, test_df = df_transformed.randomSplit([0.80, 0.20], seed=random_seed)
    train_df.cache()
    test_df.cache()
    
    train_count = train_df.count()
    test_count = test_df.count()
    logger.info(f"Train records: {train_count:,} | Test records: {test_count:,}")
    
    # --- PHASE 1: CLASSIFICATION MODELS (5 PySpark Algorithms) ---
    logger.info("==================================================")
    logger.info("TRAINING 5 PYSPARK CLASSIFICATION MODELS")
    logger.info("==================================================")
    
    clf_models = get_classification_models(features_col="features", label_col=label_col, random_seed=random_seed)
    
    classification_results = []
    trained_clf_instances = {}
    test_predictions_dict = {}
    
    for name, model_estimator in clf_models.items():
        logger.info(f"--> Training Classifier: {name}...")
        try:
            fitted_model = model_estimator.fit(train_df)
            preds = fitted_model.transform(test_df)
            
            metrics = evaluate_classifier(preds, label_col=label_col)
            metrics["model"] = name
            classification_results.append(metrics)
            trained_clf_instances[name] = fitted_model
            test_predictions_dict[name] = preds
            
            logger.info(f"    [DONE] {name} -> Acc: {metrics['accuracy']:.4f} | Prec: {metrics['precision']:.4f} | Rec: {metrics['recall']:.4f} | F1: {metrics['f1_score']:.4f}")
        except Exception as e:
            logger.error(f"    [FAIL] Failed to train {name}: {e}")
            
    # Compile comparison DataFrame
    comparison_df = pd.DataFrame(classification_results)
    comparison_df = comparison_df.sort_values(by="f1_score", ascending=False).reset_index(drop=True)
    comp_csv = os.path.join(metrics_dir, "model_comparison.csv")
    comparison_df.to_csv(comp_csv, index=False)
    logger.info(f"Model comparison table saved to: {comp_csv}")
    
    best_model_name = comparison_df.iloc[0]["model"]
    best_model = trained_clf_instances[best_model_name]
    best_preds = test_predictions_dict[best_model_name]
    logger.info(f"*** BEST CLASSIFIER: {best_model_name} (F1: {comparison_df.iloc[0]['f1_score']:.4f}) ***")
    
    # Save best classification model
    best_clf_dir = os.path.join(models_dir, "best_classifier")
    try:
        if os.path.exists(best_clf_dir):
            shutil.rmtree(best_clf_dir)
        best_model.write().overwrite().save(best_clf_dir)
        logger.info(f"Saved best classifier model to: {best_clf_dir}")
    except Exception as e:
        logger.warning(f"Native model save encountered warning/error: {e}. Writing metadata.")
        os.makedirs(best_clf_dir, exist_ok=True)
        with open(os.path.join(best_clf_dir, "model_meta.txt"), "w") as f:
            f.write(f"Best Classifier: {best_model_name}\nMetrics:\n{comparison_df.iloc[0].to_string()}\n")
    
    # Export predictions sample
    sample_preds_pd = best_preds.select(
        "segment_id", "road_name", "hour", "traffic_volume", "average_speed",
        label_col, "prediction"
    ).limit(1000).toPandas()
    preds_csv = os.path.join(preds_dir, "test_predictions_sample.csv")
    sample_preds_pd.to_csv(preds_csv, index=False)
    logger.info(f"Saved test predictions sample to: {preds_csv}")
    
    # Generate Charts
    generate_comparison_charts(
        comparison_df=comparison_df,
        best_model_name=best_model_name,
        best_preds_df=best_preds,
        label_col=label_col,
        results_dir=results_dir
    )
    
    # --- PHASE 2: REGRESSION MODELS (Speed & Travel Time Prediction) ---
    logger.info("==================================================")
    logger.info("TRAINING PYSPARK REGRESSION MODELS (SPEED PREDICTION)")
    logger.info("==================================================")
    
    reg_models = get_regression_models(features_col="features", label_col=speed_col, random_seed=random_seed)
    regression_results = []
    trained_reg_instances = {}
    
    for name, reg_estimator in reg_models.items():
        logger.info(f"--> Training Regressor: {name}...")
        try:
            fitted_reg = reg_estimator.fit(train_df)
            reg_preds = fitted_reg.transform(test_df)
            metrics = evaluate_regressor(reg_preds, label_col=speed_col)
            metrics["model"] = name
            regression_results.append(metrics)
            trained_reg_instances[name] = fitted_reg
            logger.info(f"    [DONE] {name} -> RMSE: {metrics['rmse']:.3f} | MAE: {metrics['mae']:.3f} | R2: {metrics['r2_score']:.4f}")
        except Exception as e:
            logger.error(f"    [FAIL] Failed to train regressor {name}: {e}")
            
    reg_comp_df = pd.DataFrame(regression_results).sort_values(by="r2_score", ascending=False).reset_index(drop=True)
    reg_csv = os.path.join(metrics_dir, "regression_metrics.csv")
    reg_comp_df.to_csv(reg_csv, index=False)
    logger.info(f"Saved regression metrics to: {reg_csv}")
    
    best_reg_name = reg_comp_df.iloc[0]["model"]
    best_reg = trained_reg_instances[best_reg_name]
    best_reg_dir = os.path.join(models_dir, "best_regressor")
    try:
        if os.path.exists(best_reg_dir):
            shutil.rmtree(best_reg_dir)
        best_reg.write().overwrite().save(best_reg_dir)
        logger.info(f"Saved best regressor model to: {best_reg_dir}")
    except Exception as e:
        logger.warning(f"Native regressor save encountered warning/error: {e}. Writing metadata.")
        os.makedirs(best_reg_dir, exist_ok=True)
        with open(os.path.join(best_reg_dir, "regressor_meta.txt"), "w") as f:
            f.write(f"Best Regressor: {best_reg_name}\nMetrics:\n{reg_comp_df.iloc[0].to_string()}\n")
    
    # Unpersist cached dataframes
    train_df.unpersist()
    test_df.unpersist()
    
    return {
        "best_classifier_name": best_model_name,
        "classification_comparison": comparison_df,
        "regression_comparison": reg_comp_df,
        "best_classifier_path": best_clf_dir,
        "best_regressor_path": best_reg_dir
    }
