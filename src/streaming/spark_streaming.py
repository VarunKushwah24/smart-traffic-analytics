import os
import sys
import time
from pyspark.sql import SparkSession
from pyspark.sql.types import (
    StructType, StructField, StringType, DoubleType, IntegerType
)
from pyspark.sql.functions import (
    col, from_json, to_timestamp, hour, dayofweek, month, when, lit, current_timestamp
)
from src.spark.spark_session import get_spark_session
from src.utils.logger import setup_logger

logger = setup_logger("SparkStructuredStreaming")

STREAMING_EVENT_SCHEMA = StructType([
    StructField("timestamp", StringType(), True),
    StructField("segment_id", StringType(), True),
    StructField("road_name", StringType(), True),
    StructField("source_node", StringType(), True),
    StructField("target_node", StringType(), True),
    StructField("speed_limit_kmh", DoubleType(), True),
    StructField("capacity_vph", DoubleType(), True),
    StructField("traffic_volume", IntegerType(), True),
    StructField("average_speed", DoubleType(), True),
    StructField("occupancy", DoubleType(), True),
    StructField("temperature_c", DoubleType(), True),
    StructField("weather_main", StringType(), True),
    StructField("event_id", StringType(), True)
])

def start_traffic_streaming_pipeline(
    spark: SparkSession,
    input_dir: str = "data/streaming/input",
    output_dir: str = "data/streaming/output",
    checkpoint_dir: str = "data/streaming/checkpoint",
    use_kafka: bool = False,
    kafka_servers: str = "localhost:9092",
    kafka_topic: str = "traffic-events",
    duration_sec: int = 30
):
    """
    Launches Spark Structured Streaming real-time ingestion and inference pipeline.
    
    Reads incoming JSON traffic telemetry streams, computes real-time spatio-temporal
    features, applies congestion classification rules/models, and outputs live stream
    records to console and dashboard storage.
    """
    abs_input_dir = os.path.abspath(input_dir)
    abs_output_dir = os.path.abspath(output_dir)
    abs_checkpoint_dir = os.path.abspath(checkpoint_dir)
    os.makedirs(abs_input_dir, exist_ok=True)
    os.makedirs(abs_output_dir, exist_ok=True)
    os.makedirs(abs_checkpoint_dir, exist_ok=True)
    
    logger.info("Initializing Spark Structured Streaming consumer...")
    
    if use_kafka:
        logger.info(f"Connecting to Kafka stream at {kafka_servers} (Topic: {kafka_topic})...")
        raw_stream = (
            spark.readStream
            .format("kafka")
            .option("kafka.bootstrap.servers", kafka_servers)
            .option("subscribe", kafka_topic)
            .option("startingOffsets", "latest")
            .load()
        )
        parsed_stream = (
            raw_stream.select(from_json(col("value").cast("string"), STREAMING_EVENT_SCHEMA).alias("data"))
            .select("data.*")
        )
    else:
        logger.info(f"Reading streaming events from local directory: {abs_input_dir}")
        parsed_stream = (
            spark.readStream
            .schema(STREAMING_EVENT_SCHEMA)
            .option("maxFilesPerTrigger", 1)
            .json(abs_input_dir)
        )
        
    # Real-time Feature Engineering
    stream_features = (
        parsed_stream
        .withColumn("event_time", to_timestamp(col("timestamp"), "yyyy-MM-dd HH:mm:ss"))
        .withColumn("hour", hour(col("event_time")))
        .withColumn("day_of_week", dayofweek(col("event_time")))
        .withColumn("is_rush_hour", when((col("hour").isin(7, 8, 9, 16, 17, 18, 19)), 1).otherwise(0))
        .withColumn("speed_ratio", col("average_speed") / col("speed_limit_kmh"))
        .withColumn("vc_ratio", col("traffic_volume") / col("capacity_vph"))
    )
    
    # Real-time Congestion Prediction Logic
    stream_predictions = (
        stream_features
        .withColumn(
            "predicted_congestion",
            when((col("speed_ratio") >= 0.80) & (col("vc_ratio") < 0.60), lit("LOW"))
            .when((col("speed_ratio") >= 0.60) & (col("vc_ratio") < 0.85), lit("MEDIUM"))
            .when((col("speed_ratio") >= 0.35) & (col("vc_ratio") < 1.05), lit("HIGH"))
            .otherwise(lit("SEVERE"))
        )
        .withColumn(
            "alert_status",
            when(col("predicted_congestion") == "SEVERE", lit("CRITICAL_GRIDLOCK"))
            .when(col("predicted_congestion") == "HIGH", lit("CONGESTION_WARNING"))
            .otherwise(lit("NORMAL_FLOW"))
        )
        .withColumn("processed_time", current_timestamp())
    )
    
    # Output to Console & Append to CSV for Streamlit Dashboard
    logger.info("Starting streaming queries...")
    
    query_console = (
        stream_predictions.writeStream
        .format("console")
        .outputMode("append")
        .option("truncate", "false")
        .start()
    )
    
    query_csv = (
        stream_predictions.writeStream
        .format("csv")
        .outputMode("append")
        .option("path", abs_output_dir)
        .option("checkpointLocation", abs_checkpoint_dir)
        .option("header", "true")
        .start()
    )
    
    logger.info(f"Structured Streaming active. Running for {duration_sec} seconds...")
    try:
        query_csv.awaitTermination(timeout=duration_sec)
    except Exception as e:
        logger.error(f"Streaming error: {e}")
    finally:
        query_console.stop()
        query_csv.stop()
        logger.info("Spark Structured Streaming queries stopped.")

if __name__ == "__main__":
    spark = get_spark_session("StreamingTest")
    start_traffic_streaming_pipeline(spark, duration_sec=10)
    spark.stop()
