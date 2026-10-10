import os
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.types import (
    StructType, StructField, StringType, DoubleType, IntegerType, TimestampType
)
from src.utils.logger import setup_logger

logger = setup_logger("DataIngestion")

# Schema for the authentic UCI Metro Interstate Traffic Volume dataset
UCI_METRO_SCHEMA = StructType([
    StructField("holiday", StringType(), True),
    StructField("temp", DoubleType(), True),
    StructField("rain_1h", DoubleType(), True),
    StructField("snow_1h", DoubleType(), True),
    StructField("clouds_all", IntegerType(), True),
    StructField("weather_main", StringType(), True),
    StructField("weather_description", StringType(), True),
    StructField("date_time", StringType(), True),
    StructField("traffic_volume", IntegerType(), True)
])

# Schema for the multi-segment corridor network dataset
CORRIDOR_NETWORK_SCHEMA = StructType([
    StructField("timestamp", StringType(), True),
    StructField("segment_id", StringType(), True),
    StructField("road_name", StringType(), True),
    StructField("source_node", StringType(), True),
    StructField("target_node", StringType(), True),
    StructField("source_lat", DoubleType(), True),
    StructField("source_lon", DoubleType(), True),
    StructField("target_lat", DoubleType(), True),
    StructField("target_lon", DoubleType(), True),
    StructField("distance_km", DoubleType(), True),
    StructField("speed_limit_kmh", DoubleType(), True),
    StructField("capacity_vph", DoubleType(), True),
    StructField("traffic_volume", IntegerType(), True),
    StructField("average_speed", DoubleType(), True),
    StructField("occupancy", DoubleType(), True),
    StructField("travel_time_min", DoubleType(), True),
    StructField("weather_main", StringType(), True),
    StructField("weather_description", StringType(), True),
    StructField("temperature_c", DoubleType(), True),
    StructField("congestion_level", StringType(), True)
])

def load_raw_traffic_data(
    spark: SparkSession,
    dataset_path: str,
    dataset_type: str = "corridor"
) -> DataFrame:
    """
    Ingests traffic dataset using PySpark with explicit StructType schema validation.
    
    Parameters:
      spark: Active SparkSession
      dataset_path: Filepath to CSV dataset
      dataset_type: 'corridor' (multi-segment network) or 'uci' (Metro interstate)
      
    Returns:
      PySpark DataFrame with applied schema
    """
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Raw traffic dataset file not found: {dataset_path}")
        
    logger.info(f"Ingesting raw data from: {dataset_path} (Type: {dataset_type})")
    
    schema = CORRIDOR_NETWORK_SCHEMA if dataset_type == "corridor" else UCI_METRO_SCHEMA
    
    df = (
        spark.read
        .format("csv")
        .option("header", "true")
        .schema(schema)
        .load(dataset_path)
    )
    
    count = df.count()
    partitions = df.rdd.getNumPartitions()
    logger.info(f"Ingestion complete: {count:,} records loaded across {partitions} partitions.")
    logger.debug(f"DataFrame Schema:\n{df._jdf.schema().treeString()}")
    
    return df
