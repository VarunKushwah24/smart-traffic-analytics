import os
import sys
import time

# Ensure project root is in python path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.utils.config import load_config
from src.utils.logger import setup_logger
from src.spark.spark_session import get_spark_session
from src.spark.data_ingestion import load_raw_traffic_data
from src.spark.preprocessing import clean_traffic_data
from src.spark.feature_engineering import engineer_traffic_features, prepare_ml_features
from src.spark.eda import run_spark_eda
from src.ml.train_models import run_ml_training_pipeline
from scripts.generate_powerbi_marts import export_powerbi_data_marts

logger = setup_logger("MainPipelineRunner")

def main():
    start_time = time.time()
    logger.info("================================================================================")
    logger.info("STARTING END-TO-END SMART TRAFFIC BIG DATA ANALYTICS & BI PIPELINE")
    logger.info("================================================================================")
    
    config = load_config()
    corridor_path = os.path.abspath(config["paths"]["raw_corridor_data"])
    processed_parquet = os.path.abspath(config["paths"]["processed_parquet"])
    processed_csv = os.path.abspath(config["paths"]["processed_csv"])
    
    # 1. Initialize SparkSession
    spark = get_spark_session(
        app_name=config["spark"]["app_name"],
        master=config["spark"]["master"]
    )
    
    try:
        # 2. PySpark Data Ingestion
        logger.info("\n--- STEP 1: PYSPARK DATA INGESTION ---")
        df_raw = load_raw_traffic_data(spark, corridor_path, dataset_type="corridor")
        
        # 3. PySpark Data Preprocessing & Cleaning
        logger.info("\n--- STEP 2: PYSPARK PREPROCESSING & DATA CLEANING ---")
        df_clean = clean_traffic_data(df_raw, dataset_type="corridor")
        
        # 4. PySpark Feature Engineering
        logger.info("\n--- STEP 3: PYSPARK FEATURE ENGINEERING ---")
        df_features = engineer_traffic_features(df_clean, dataset_type="corridor")
        
        # Save processed data sample
        logger.info("Saving engineered dataset to Parquet & CSV...")
        os.makedirs(os.path.dirname(processed_parquet), exist_ok=True)
        # Save sample as CSV for quick inspection
        df_sample_pd = df_features.limit(1000).toPandas()
        df_sample_pd.to_csv(processed_csv, index=False)
        logger.info(f"Sample processed data saved to: {processed_csv}")
        
        # 5. Exploratory Data Analysis (EDA)
        logger.info("\n--- STEP 4: DISTRIBUTED PYSPARK EXPLORATORY DATA ANALYSIS (EDA) ---")
        eda_results = run_spark_eda(df_features, results_dir=config["paths"]["metrics_dir"].split("/")[0])
        
        # 6. ML Vector Assembly & Scaling Pipeline
        logger.info("\n--- STEP 5: ML VECTOR ASSEMBLY & PIPELINE PREPARATION ---")
        df_ml, pipeline_model, feature_cols = prepare_ml_features(
            df_features, label_col="congestion_numeric", scale_features=True
        )
        
        # 7. Machine Learning Model Training & Evaluation (5 Classifiers + Regressors)
        logger.info("\n--- STEP 6: TRAINING & BENCHMARKING 5 PYSPARK MLlib MODELS ---")
        ml_summary = run_ml_training_pipeline(
            df_transformed=df_ml,
            label_col="congestion_numeric",
            speed_col="average_speed",
            models_dir=config["paths"]["models_dir"],
            results_dir="results",
            random_seed=config["app"]["random_seed"]
        )
        
        # 8. Export Power BI Data Marts
        logger.info("\n--- STEP 7: EXPORTING POWER BI DATA MARTS ---")
        export_powerbi_data_marts()
        
        elapsed = round(time.time() - start_time, 2)
        logger.info("================================================================================")
        logger.info(f"PIPELINE COMPLETED SUCCESSFULLY IN {elapsed} SECONDS!")
        logger.info(f"Best Classifier: {ml_summary['best_classifier_name']}")
        logger.info(f"Results exported to: results/metrics/, results/plots/, and powerbi/")
        logger.info("================================================================================")
        
    finally:
        spark.stop()
        logger.info("SparkSession stopped cleanly.")

if __name__ == "__main__":
    main()
