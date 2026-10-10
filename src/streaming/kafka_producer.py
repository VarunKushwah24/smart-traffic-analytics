import os
import sys
import time
import json
import random
from datetime import datetime
import pandas as pd
from src.utils.logger import setup_logger

logger = setup_logger("KafkaProducer")

class TrafficEventProducer:
    """
    Simulates real-time IoT road sensor telemetry streams.
    Publishes events to an Apache Kafka topic ('traffic-events'), and automatically
    falls back to a local directory streaming mode ('data/streaming/input') if Kafka
    is not running locally.
    """

    def __init__(
        self,
        bootstrap_servers: str = "localhost:9092",
        topic: str = "traffic-events",
        local_stream_dir: str = "data/streaming/input"
    ):
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.local_stream_dir = os.path.abspath(local_stream_dir)
        os.makedirs(self.local_stream_dir, exist_ok=True)
        
        self.kafka_available = False
        self.producer = None
        self._init_kafka()

    def _init_kafka(self):
        """Attempts to connect to live Kafka cluster."""
        try:
            from kafka import KafkaProducer
            self.producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                request_timeout_ms=3000
            )
            self.kafka_available = True
            logger.info(f"Connected to Apache Kafka broker at: {self.bootstrap_servers}")
        except Exception as e:
            self.kafka_available = False
            logger.warning(
                f"Kafka broker unavailable at {self.bootstrap_servers} ({e}). "
                f"Using Local Streaming Demo Mode via: {self.local_stream_dir}"
            )

    def generate_random_event(self) -> dict:
        """Generates a realistic traffic telemetry sensor reading."""
        segments = [
            ("SEG_I94_EB", "I-94 Eastbound", "DOWNTOWN_MPLS", "DOWNTOWN_STP", 90, 4800),
            ("SEG_I94_WB", "I-94 Westbound", "DOWNTOWN_STP", "DOWNTOWN_MPLS", 90, 4800),
            ("SEG_I35W_SB", "I-35W Southbound", "DOWNTOWN_MPLS", "AIRPORT_MSP", 95, 4200),
            ("SEG_I35W_NB", "I-35W Northbound", "AIRPORT_MSP", "DOWNTOWN_MPLS", 95, 4200),
            ("SEG_MN62_EB", "MN-62 Crosstown EB", "EDINA", "AIRPORT_MSP", 85, 3600),
            ("SEG_I494_EB", "I-494 Beltway EB", "BLOOMINGTON", "EAGAN", 100, 4500)
        ]
        
        seg_id, road_name, src, tgt, speed_limit, capacity = random.choice(segments)
        
        now = datetime.now()
        hr = now.hour
        is_rush = (7 <= hr <= 9) or (16 <= hr <= 19)
        
        base_flow = random.uniform(0.65, 1.10) if is_rush else random.uniform(0.15, 0.60)
        volume = int(base_flow * capacity)
        vc_ratio = volume / capacity
        
        speed_factor = 1.0 / (1.0 + 0.25 * (vc_ratio ** 3.5))
        avg_speed = max(18.0, round(speed_limit * speed_factor + random.gauss(0, 3), 1))
        occupancy = round(min(0.95, max(0.04, (volume / capacity) * 0.40)), 3)
        
        weathers = [("Clear", 18.5), ("Clouds", 16.0), ("Rain", 12.0)]
        weather_main, temp_c = random.choices(weathers, weights=[0.6, 0.3, 0.1])[0]

        event = {
            "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
            "segment_id": seg_id,
            "road_name": road_name,
            "source_node": src,
            "target_node": tgt,
            "speed_limit_kmh": float(speed_limit),
            "capacity_vph": float(capacity),
            "traffic_volume": volume,
            "average_speed": avg_speed,
            "occupancy": occupancy,
            "temperature_c": temp_c,
            "weather_main": weather_main,
            "event_id": f"evt_{int(time.time() * 1000)}"
        }
        return event

    def send_event(self, event: dict):
        """Sends event to Kafka or writes to local directory stream."""
        if self.kafka_available and self.producer:
            try:
                self.producer.send(self.topic, value=event)
                logger.info(f"[KAFKA STREAM] Sent event for {event['road_name']}: Vol={event['traffic_volume']}, Speed={event['average_speed']}")
            except Exception as e:
                logger.error(f"Kafka send failed: {e}. Falling back to file stream.")
                self._write_local_stream(event)
        else:
            self._write_local_stream(event)

    def _write_local_stream(self, event: dict):
        """Writes JSON event file to local directory stream for Spark Structured Streaming."""
        filename = f"event_{event['event_id']}.json"
        filepath = os.path.join(self.local_stream_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(event, f)
        logger.info(f"[LOCAL STREAM] Produced event file: {filename} ({event['road_name']}, Speed={event['average_speed']} km/h)")

    def start_streaming(self, num_events: int = 100, interval_sec: float = 1.0):
        """Runs continuous event production loop."""
        logger.info(f"Starting Traffic Event Producer (Target: {num_events} events, Interval: {interval_sec}s)...")
        count = 0
        try:
            while count < num_events:
                event = self.generate_random_event()
                self.send_event(event)
                count += 1
                time.sleep(interval_sec)
        except KeyboardInterrupt:
            logger.info("Streaming producer interrupted by user.")
        finally:
            if self.producer:
                self.producer.flush()
                self.producer.close()
            logger.info(f"Event streaming finished. Total events produced: {count}")

if __name__ == "__main__":
    producer = TrafficEventProducer()
    producer.start_streaming(num_events=10, interval_sec=1.0)
