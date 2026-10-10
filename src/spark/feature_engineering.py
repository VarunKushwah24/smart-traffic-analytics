import os
from pyspark.sql import DataFrame
from pyspark.sql.functions import (
    col, hour, dayofweek, dayofmonth, month, when, lit, round as sp_round
)
from pyspark.ml.feature import (
    StringIndexer, OneHotEncoder, VectorAssembler, StandardScaler
)
from pyspark.ml import Pipeline
from src.utils.logger import setup_logger

logger = setup_logger("FeatureEngineering")

def engineer_traffic_features(df: DataFrame, dataset_type: str = "corridor") -> DataFrame:
    """
    Constructs domain-specific traffic and spatio-temporal features:
      1. Temporal: hour, day_of_week, day_of_month, month, is_weekend
      2. Peak Indicators: is_morning_peak (7-9), is_evening_peak (16-19), is_rush_hour
      3. Traffic Ratios: speed_ratio = avg_speed / speed_limit, vc_ratio = volume / capacity
      4. Weather categorization
    """
    logger.info("Extracting temporal and traffic dynamics features...")
    
    # 1. Temporal decomposition
    df_feat = (
        df.withColumn("hour", hour(col("timestamp")))
        .withColumn("day_of_week", dayofweek(col("timestamp"))) # 1=Sun, 7=Sat
        .withColumn("day_of_month", dayofmonth(col("timestamp")))
        .withColumn("month", month(col("timestamp")))
        .withColumn("is_weekend", when(col("day_of_week").isin(1, 7), 1).otherwise(0))
    )
    
    # 2. Peak & rush hour indicators
    df_feat = (
        df_feat.withColumn(
            "is_morning_peak",
            when((col("hour") >= 7) & (col("hour") <= 9) & (col("is_weekend") == 0), 1).otherwise(0)
        )
        .withColumn(
            "is_evening_peak",
            when((col("hour") >= 16) & (col("hour") <= 19) & (col("is_weekend") == 0), 1).otherwise(0)
        )
        .withColumn(
            "is_rush_hour",
            when((col("is_morning_peak") == 1) | (col("is_evening_peak") == 1), 1).otherwise(0)
        )
    )
    
    # 3. Traffic dynamic indicators (for corridor dataset)
    if "speed_limit_kmh" in df.columns and "capacity_vph" in df.columns:
        df_feat = (
            df_feat.withColumn(
                "speed_ratio",
                sp_round(col("average_speed") / col("speed_limit_kmh"), 4)
            )
            .withColumn(
                "vc_ratio",
                sp_round(col("traffic_volume") / col("capacity_vph"), 4)
            )
        )
    elif "traffic_volume" in df.columns:
        # For UCI dataset where capacity is approx 7200
        df_feat = (
            df_feat.withColumn("vc_ratio", sp_round(col("traffic_volume") / 7200.0, 4))
            .withColumn("speed_ratio", sp_round(1.0 / (1.0 + 0.15 * (col("vc_ratio") ** 4)), 4))
            .withColumn("average_speed", sp_round(col("speed_ratio") * 95.0, 1))
            .withColumn("occupancy", sp_round(col("vc_ratio") * 0.35, 4))
        )
        
    logger.info("Feature engineering completed successfully.")
    return df_feat

def prepare_ml_features(
    df: DataFrame,
    feature_cols=None,
    label_col: str = "congestion_numeric",
    scale_features: bool = True
):
    """
    Builds a PySpark ML Pipeline to assemble and scale feature vectors for ML models.
    Prevents data leakage: labels are excluded from feature vectors.
    """
    if feature_cols is None:
        feature_cols = [
            "hour", "day_of_week", "month", "is_weekend",
            "is_rush_hour", "is_morning_peak", "is_evening_peak",
            "traffic_volume", "average_speed", "occupancy",
            "temperature_c", "weather_idx"
        ]
        
    logger.info(f"Building ML Pipeline for label '{label_col}' with {len(feature_cols)} features...")
    
    # String Indexer for Weather
    weather_indexer = (
        StringIndexer(inputCol="weather_main", outputCol="weather_idx", handleInvalid="keep")
    )
    
    # Vector Assembler
    assembler = VectorAssembler(
        inputCols=feature_cols,
        outputCol="raw_features",
        handleInvalid="skip"
    )
    
    stages = [weather_indexer, assembler]
    
    if scale_features:
        scaler = StandardScaler(
            inputCol="raw_features",
            outputCol="features",
            withStd=True,
            withMean=False
        )
        stages.append(scaler)
    else:
        # If no scaler, rename raw_features
        pass
        
    pipeline = Pipeline(stages=stages)
    pipeline_model = pipeline.fit(df)
    transformed_df = pipeline_model.transform(df)
    
    # If not scaled, alias raw_features to features
    if not scale_features:
        transformed_df = transformed_df.withColumnRenamed("raw_features", "features")
        
    logger.info("ML vector assembly and scaling pipeline fitted.")
    return transformed_df, pipeline_model, feature_cols
