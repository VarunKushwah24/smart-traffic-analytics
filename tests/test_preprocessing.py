import os
import pytest
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType
from src.spark.spark_session import get_spark_session
from src.spark.preprocessing import clean_traffic_data
from src.spark.feature_engineering import engineer_traffic_features

@pytest.fixture(scope="session")
def spark():
    spark_session = get_spark_session("PyTest_Preprocessing")
    yield spark_session
    spark_session.stop()

def test_clean_traffic_data_duplicates_and_nulls(spark):
    data = [
        ("2023-10-01 08:00:00", "SEG_TEST_1", "Test Road", "SRC", "TGT", 44.0, -93.0, 44.1, -93.1, 10.0, 100.0, 4000.0, 2500, 85.0, 0.25, 7.0, "Clear", "clear sky", 18.0, "LOW"),
        ("2023-10-01 08:00:00", "SEG_TEST_1", "Test Road", "SRC", "TGT", 44.0, -93.0, 44.1, -93.1, 10.0, 100.0, 4000.0, 2500, 85.0, 0.25, 7.0, "Clear", "clear sky", 18.0, "LOW"), # Duplicate
        ("2023-10-01 09:00:00", "SEG_TEST_2", "Test Road 2", "SRC", "TGT", 44.0, -93.0, 44.1, -93.1, 10.0, 100.0, 4000.0, 3800, 35.0, 0.75, 17.0, None, None, None, "SEVERE"),
    ]
    schema = StructType([
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
    
    df = spark.createDataFrame(data, schema=schema)
    cleaned_df = clean_traffic_data(df, dataset_type="corridor")
    
    # Check deduplication
    assert cleaned_df.count() == 2
    
    # Check columns added
    assert "congestion_numeric" in cleaned_df.columns
    assert "is_congested" in cleaned_df.columns
    
    # Check numeric mapping
    row_severe = cleaned_df.filter(cleaned_df.segment_id == "SEG_TEST_2").first()
    assert row_severe["congestion_numeric"] == 3
    assert row_severe["is_congested"] == 1
    assert row_severe["weather_main"] == "Clear" # Default imputation

def test_feature_engineering_temporal_columns(spark):
    data = [
        ("2023-10-02 08:30:00", "SEG_1", "Road A", "SRC", "TGT", 44.0, -93.0, 44.1, -93.1, 10.0, 100.0, 4000.0, 3200, 60.0, 0.40, 10.0, "Clear", "clear sky", 15.0, "MEDIUM")
    ]
    schema = StructType([
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
    df = spark.createDataFrame(data, schema=schema)
    cleaned_df = clean_traffic_data(df, dataset_type="corridor")
    feat_df = engineer_traffic_features(cleaned_df, dataset_type="corridor")
    
    row = feat_df.first()
    assert row["hour"] == 8
    assert row["is_morning_peak"] == 1
    assert row["is_rush_hour"] == 1
    assert "vc_ratio" in feat_df.columns
    assert "speed_ratio" in feat_df.columns
