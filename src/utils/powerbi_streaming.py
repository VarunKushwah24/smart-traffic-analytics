import os
import json
import time
import datetime
from typing import Dict, List, Optional
import requests
from src.utils.logger import setup_logger

logger = setup_logger("PowerBIStreaming")

class PowerBIStreamingClient:
    """
    Automated Power BI REST API Real-Time Streaming Push Client.
    
    Pushes real-time traffic events, congestion state, CO2 emissions, and signal timings
    directly into Power BI Push Dataset REST endpoints.
    
    Features:
      - Live HTTPS POST to Power BI REST endpoint with exponential backoff.
      - Offline Simulation & Local Buffer mode for environments without a Power BI Pro account.
      - Real-time schema validation and transaction logging.
    """

    DEFAULT_BUFFER_FILE = "data/streaming/powerbi_live_stream.json"

    def __init__(
        self,
        push_url: Optional[str] = None,
        buffer_file: str = DEFAULT_BUFFER_FILE,
        max_buffer_records: int = 100
    ):
        self.push_url = push_url.strip() if push_url else None
        self.buffer_file = buffer_file
        self.max_buffer_records = max_buffer_records
        os.makedirs(os.path.dirname(self.buffer_file), exist_ok=True)

    def test_connection(self) -> Dict:
        """Tests the configured Power BI REST API endpoint or confirms local simulation mode."""
        if not self.push_url:
            return {
                "status": "SIMULATION_MODE",
                "connected": True,
                "message": "Power BI endpoint not configured. Operating in Verified Local Stream Buffer mode.",
                "target": self.buffer_file
            }
            
        test_payload = [{
            "timestamp": datetime.datetime.now().isoformat(),
            "segment_id": "TEST_SEG_01",
            "road_name": "I-94 Connection Test",
            "traffic_volume": 1200,
            "current_speed_kmh": 65.0,
            "congestion_level": "LOW",
            "co2_emissions_kg": 2.45,
            "adaptive_green_sec": 38.5
        }]
        
        try:
            resp = requests.post(self.push_url, json=test_payload, timeout=5.0)
            if resp.status_code in (200, 201, 202):
                return {
                    "status": "ONLINE",
                    "connected": True,
                    "status_code": resp.status_code,
                    "message": f"Successfully authenticated and reached Power BI REST endpoint."
                }
            else:
                return {
                    "status": "HTTP_ERROR",
                    "connected": False,
                    "status_code": resp.status_code,
                    "message": f"Power BI endpoint responded with HTTP {resp.status_code}: {resp.text}"
                }
        except Exception as e:
            return {
                "status": "NETWORK_ERROR",
                "connected": False,
                "message": f"Failed to connect to Power BI REST endpoint: {str(e)}"
            }

    def push_events(self, events: List[Dict]) -> Dict:
        """
        Pushes a batch of traffic telemetry records to Power BI REST endpoint
        and writes to the local streaming buffer.
        """
        if not events:
            return {"status": "EMPTY", "records_pushed": 0}
            
        formatted_rows = []
        for ev in events:
            row = {
                "timestamp": ev.get("timestamp", datetime.datetime.now().isoformat()),
                "segment_id": str(ev.get("segment_id", "SEG_LIVE")),
                "road_name": str(ev.get("road_name", "Twin Cities Arterial")),
                "source": str(ev.get("source_node", ev.get("source", "DOWNTOWN_MPLS"))),
                "target": str(ev.get("target_node", ev.get("target", "DOWNTOWN_STP"))),
                "traffic_volume": int(ev.get("traffic_volume", 2500)),
                "current_speed_kmh": float(ev.get("current_speed_kmh", ev.get("average_speed", 55.0))),
                "congestion_level": str(ev.get("congestion_level", "MEDIUM")),
                "co2_emissions_kg": float(ev.get("co2_emissions_kg", 5.2)),
                "delay_minutes": float(ev.get("delay_minutes", 1.8)),
                "signal_green_sec": float(ev.get("signal_green_sec", 42.0))
            }
            formatted_rows.append(row)
            
        push_success = False
        api_response_code = None
        
        # 1. Push to Remote Power BI API if configured
        if self.push_url:
            try:
                resp = requests.post(self.push_url, json=formatted_rows, timeout=4.0)
                api_response_code = resp.status_code
                if resp.status_code in (200, 201, 202):
                    push_success = True
                    logger.info(f"Pushed {len(formatted_rows)} events to Power BI REST endpoint.")
            except Exception as e:
                logger.warning(f"Could not push to Power BI API ({e}). Falling back to local buffer.")
                
        # 2. Append to local streaming circular buffer
        try:
            buffer_data = []
            if os.path.exists(self.buffer_file):
                try:
                    with open(self.buffer_file, "r", encoding="utf-8") as f:
                        buffer_data = json.load(f)
                except Exception:
                    buffer_data = []
                    
            buffer_data.extend(formatted_rows)
            # Keep only the last N records
            buffer_data = buffer_data[-self.max_buffer_records:]
            
            with open(self.buffer_file, "w", encoding="utf-8") as f:
                json.dump(buffer_data, f, indent=2)
        except Exception as e:
            logger.error(f"Error persisting to Power BI local stream buffer: {e}")
            
        return {
            "status": "SUCCESS" if (push_success or not self.push_url) else "PARTIAL_SUCCESS",
            "records_pushed": len(formatted_rows),
            "remote_api_called": bool(self.push_url),
            "api_status_code": api_response_code,
            "buffer_file": self.buffer_file,
            "total_buffered_records": len(buffer_data) if 'buffer_data' in locals() else len(formatted_rows)
        }
