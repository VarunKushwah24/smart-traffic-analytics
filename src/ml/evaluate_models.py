import os
from pyspark.sql import DataFrame
from pyspark.ml.evaluation import MulticlassClassificationEvaluator, RegressionEvaluator
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix
from src.utils.logger import setup_logger

logger = setup_logger("ModelEvaluation")

def evaluate_classifier(predictions_df: DataFrame, label_col: str = "congestion_numeric") -> dict:
    """
    Computes rigorous evaluation metrics for PySpark classification models:
      - Accuracy
      - Weighted Precision
      - Weighted Recall
      - Weighted F1 Score
    """
    eval_acc = MulticlassClassificationEvaluator(labelCol=label_col, predictionCol="prediction", metricName="accuracy")
    eval_prec = MulticlassClassificationEvaluator(labelCol=label_col, predictionCol="prediction", metricName="weightedPrecision")
    eval_rec = MulticlassClassificationEvaluator(labelCol=label_col, predictionCol="prediction", metricName="weightedRecall")
    eval_f1 = MulticlassClassificationEvaluator(labelCol=label_col, predictionCol="prediction", metricName="f1")
    
    accuracy = float(eval_acc.evaluate(predictions_df))
    precision = float(eval_prec.evaluate(predictions_df))
    recall = float(eval_rec.evaluate(predictions_df))
    f1 = float(eval_f1.evaluate(predictions_df))
    
    metrics = {
        "accuracy": round(accuracy, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1, 4)
    }
    return metrics

def evaluate_regressor(predictions_df: DataFrame, label_col: str = "average_speed") -> dict:
    """Computes RMSE, MAE, and R2 for regression models."""
    eval_rmse = RegressionEvaluator(labelCol=label_col, predictionCol="prediction", metricName="rmse")
    eval_mae = RegressionEvaluator(labelCol=label_col, predictionCol="prediction", metricName="mae")
    eval_r2 = RegressionEvaluator(labelCol=label_col, predictionCol="prediction", metricName="r2")
    
    return {
        "rmse": round(float(eval_rmse.evaluate(predictions_df)), 3),
        "mae": round(float(eval_mae.evaluate(predictions_df)), 3),
        "r2_score": round(float(eval_r2.evaluate(predictions_df)), 4)
    }

def generate_comparison_charts(
    comparison_df: pd.DataFrame,
    best_model_name: str,
    best_preds_df: DataFrame,
    label_col: str = "congestion_numeric",
    results_dir: str = "results"
):
    """
    Renders and exports model comparison bar charts and the best model's confusion matrix.
    """
    plots_dir = os.path.join(results_dir, "plots")
    os.makedirs(plots_dir, exist_ok=True)
    
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    
    # 1. Bar Chart: Model Metrics Comparison
    fig, ax = plt.subplots(figsize=(11, 6))
    metrics_to_plot = ["accuracy", "precision", "recall", "f1_score"]
    
    x = np.arange(len(comparison_df))
    width = 0.20
    
    colors = ["#1f77b4", "#2ca02c", "#ff7f0e", "#d62728"]
    for i, metric in enumerate(metrics_to_plot):
        values = comparison_df[metric].values
        rects = ax.bar(x + (i - 1.5) * width, values, width, label=metric.replace("_", " ").title(), color=colors[i], alpha=0.9)
        for rect in rects:
            h = rect.get_height()
            ax.annotate(f"{h:.2f}",
                        xy=(rect.get_x() + rect.get_width() / 2, h),
                        xytext=(0, 3), textcoords="offset points",
                        ha='center', va='bottom', fontsize=8, fontweight='bold')

    ax.set_title("PySpark MLlib Models Performance Comparison", fontsize=14, fontweight="bold", pad=12)
    ax.set_ylabel("Score", fontsize=12, fontweight="bold")
    ax.set_xlabel("Model Architecture", fontsize=12, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(comparison_df["model"], fontsize=10, fontweight="bold")
    ax.set_ylim(0, 1.15)
    ax.legend(loc="lower right", frameon=True)
    
    fig.tight_layout()
    comp_plot_path = os.path.join(plots_dir, "model_comparison_metrics.png")
    plt.savefig(comp_plot_path, dpi=300)
    plt.close(fig)
    logger.info(f"Saved model comparison plot to: {comp_plot_path}")
    
    # 2. Confusion Matrix for Best Classifier
    sample_preds = best_preds_df.select(label_col, "prediction").toPandas()
    y_true = sample_preds[label_col].astype(int)
    y_pred = sample_preds["prediction"].astype(int)
    
    labels = [0, 1, 2, 3]
    class_names = ["LOW", "MEDIUM", "HIGH", "SEVERE"]
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    
    fig, ax = plt.subplots(figsize=(7, 6))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", cbar=True,
                xticklabels=class_names, yticklabels=class_names, ax=ax)
    ax.set_title(f"Confusion Matrix: Best Model ({best_model_name})", fontsize=13, fontweight="bold")
    ax.set_xlabel("Predicted Congestion Level", fontsize=11, fontweight="bold")
    ax.set_ylabel("Actual Congestion Level", fontsize=11, fontweight="bold")
    
    fig.tight_layout()
    cm_plot_path = os.path.join(plots_dir, "confusion_matrix_best_model.png")
    plt.savefig(cm_plot_path, dpi=300)
    plt.close(fig)
    logger.info(f"Saved confusion matrix plot to: {cm_plot_path}")
