import os
import sys
import threading
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.utils.config import load_config
from src.utils.logger import setup_logger
from src.spark.spark_session import get_spark_session
from src.streaming.kafka_producer import TrafficEventProducer
from src.streaming.spark_streaming import start_traffic_streaming_pipeline

logger = setup_logger("StreamingRunner")

def produce_events_worker(num_events: int = 15, interval: float = 1.0):
    time.sleep(2) # Give Spark streaming query time to start
    producer = TrafficEventProducer()
    producer.start_streaming(num_events=num_events, interval_sec=interval)

def main():
    config = load_config()
    spark = get_spark_session("TrafficStreamingApp")
    
    logger.info("Starting background event producer thread...")
    producer_thread = threading.Thread(target=produce_events_worker, args=(15, 1.0), daemon=True)
    producer_thread.start()
    
    try:
        start_traffic_streaming_pipeline(
            spark=spark,
            input_dir=config["paths"]["streaming_input"],
            output_dir=config["paths"]["streaming_output"],
            checkpoint_dir=config["paths"]["streaming_checkpoint"],
            use_kafka=False, # Local simulation mode
            duration_sec=25
        )
    finally:
        spark.stop()
        logger.info("Streaming demonstration finished successfully.")

if __name__ == "__main__":
    main()
