import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.utils.config import load_config
from src.utils.logger import setup_logger
from src.spark.spark_session import get_spark_session
from src.spark.data_ingestion import load_raw_traffic_data
from src.spark.preprocessing import clean_traffic_data
from src.spark.feature_engineering import engineer_traffic_features, prepare_ml_features
from src.ml.train_models import run_ml_training_pipeline

logger = setup_logger("TrainModelsRunner")

def main():
    config = load_config()
    spark = get_spark_session("ModelTrainingRunner")
    try:
        corridor_path = os.path.abspath(config["paths"]["raw_corridor_data"])
        df_raw = load_raw_traffic_data(spark, corridor_path, dataset_type="corridor")
        df_clean = clean_traffic_data(df_raw, dataset_type="corridor")
        df_features = engineer_traffic_features(df_clean, dataset_type="corridor")
        df_ml, _, _ = prepare_ml_features(df_features, label_col="congestion_numeric")
        
        ml_summary = run_ml_training_pipeline(
            df_transformed=df_ml,
            label_col="congestion_numeric",
            speed_col="average_speed",
            models_dir=config["paths"]["models_dir"],
            results_dir="results",
            random_seed=config["app"]["random_seed"]
        )
        print("\n" + "="*60)
        print("PYSPARK CLASSIFICATION MODEL COMPARISON")
        print("="*60)
        print(ml_summary["classification_comparison"].to_string(index=False))
        print("\n" + "="*60)
        print("PYSPARK REGRESSION MODEL COMPARISON")
        print("="*60)
        print(ml_summary["regression_comparison"].to_string(index=False))
        print("="*60 + "\n")
    finally:
        spark.stop()

if __name__ == "__main__":
    main()
