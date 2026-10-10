import os
from pyspark.sql import DataFrame
from pyspark.sql.functions import (
    col, to_timestamp, when, lit, count, isnan, isnull, trim, upper, round as sp_round
)
from src.utils.logger import setup_logger

logger = setup_logger("Preprocessing")

def clean_traffic_data(df: DataFrame, dataset_type: str = "corridor") -> DataFrame:
    """
    Executes distributed data preprocessing and cleaning using PySpark:
      1. Duplicate record removal
      2. Timestamp conversion to Spark TimestampType
      3. Missing / Null value detection and imputation
      4. Physical sanity checks & outlier filtering (speed > 0, volume >= 0)
      5. Congestion category standardisation / creation
      
    Returns:
      Cleaned PySpark DataFrame
    """
    initial_count = df.count()
    logger.info(f"Starting data preprocessing on {initial_count:,} records...")
    
    # 1. Deduplication
    df_dedup = df.dropDuplicates()
    dedup_count = df_dedup.count()
    duplicates_removed = initial_count - dedup_count
    if duplicates_removed > 0:
        logger.info(f"Removed {duplicates_removed:,} duplicate rows.")

    if dataset_type == "corridor":
        # 2. Timestamp conversion
        df_clean = df_dedup.withColumn(
            "timestamp",
            to_timestamp(col("timestamp"), "yyyy-MM-dd HH:mm:ss")
        )
        
        # 3. Handle nulls and default values
        df_clean = df_clean.fillna({
            "weather_main": "Clear",
            "weather_description": "clear sky",
            "temperature_c": 15.0,
            "occupancy": 0.05,
            "traffic_volume": 0
        })
        
        # 4. Outlier & Sanity Filtering
        # Speeds must be positive and bounded by 160 km/h; volume >= 0
        df_clean = df_clean.filter(
            (col("average_speed") > 5.0) &
            (col("average_speed") < 160.0) &
            (col("traffic_volume") >= 0) &
            (col("distance_km") > 0.0)
        )
        
        # 5. Standardize congestion labels to uppercase
        df_clean = df_clean.withColumn("congestion_level", upper(trim(col("congestion_level"))))
        
        # Add numeric congestion index: LOW=0, MEDIUM=1, HIGH=2, SEVERE=3
        df_clean = df_clean.withColumn(
            "congestion_numeric",
            when(col("congestion_level") == "LOW", 0)
            .when(col("congestion_level") == "MEDIUM", 1)
            .when(col("congestion_level") == "HIGH", 2)
            .when(col("congestion_level") == "SEVERE", 3)
            .otherwise(0)
        )
        
        # Add binary congestion flag: 0 = Normal (LOW/MEDIUM), 1 = Congested (HIGH/SEVERE)
        df_clean = df_clean.withColumn(
            "is_congested",
            when(col("congestion_numeric") >= 2, 1).otherwise(0)
        )
        
    else:
        # Handling for UCI Metro Interstate dataset
        df_clean = df_dedup.withColumn(
            "timestamp",
            to_timestamp(col("date_time"), "yyyy-MM-dd HH:mm:ss")
        ).drop("date_time")
        
        # Temperature conversion from Kelvin to Celsius and outlier clipping (0 K is invalid sensor reading)
        df_clean = df_clean.filter((col("temp") > 200.0) & (col("temp") < 340.0))
        df_clean = df_clean.withColumn("temperature_c", sp_round(col("temp") - 273.15, 2))
        
        # Cap anomalous rain values (sensor errors in UCI dataset where rain > 9000 mm)
        df_clean = df_clean.withColumn(
            "rain_1h",
            when(col("rain_1h") > 100.0, 0.0).otherwise(col("rain_1h"))
        )
        
        df_clean = df_clean.fillna({
            "holiday": "None",
            "weather_main": "Clear",
            "weather_description": "clear sky"
        })
        
        # Derive congestion level using traffic volume thresholds for I-94 (Capacity ~ 7200 vph)
        # Low: < 2000, Medium: 2000-4500, High: 4500-6000, Severe: > 6000
        df_clean = df_clean.withColumn(
            "congestion_level",
            when(col("traffic_volume") < 2000, lit("LOW"))
            .when(col("traffic_volume") < 4500, lit("MEDIUM"))
            .when(col("traffic_volume") < 6000, lit("HIGH"))
            .otherwise(lit("SEVERE"))
        )
        
        df_clean = df_clean.withColumn(
            "congestion_numeric",
            when(col("congestion_level") == "LOW", 0)
            .when(col("congestion_level") == "MEDIUM", 1)
            .when(col("congestion_level") == "HIGH", 2)
            .when(col("congestion_level") == "SEVERE", 3)
            .otherwise(0)
        )
        
        df_clean = df_clean.withColumn(
            "is_congested",
            when(col("congestion_numeric") >= 2, 1).otherwise(0)
        )

    final_count = df_clean.count()
    logger.info(f"Preprocessing completed. Valid records retained: {final_count:,} (Removed: {initial_count - final_count:,})")
    return df_clean
