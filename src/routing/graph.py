import os
from typing import Dict, List, Tuple, Optional
import pandas as pd
from src.utils.logger import setup_logger

logger = setup_logger("RoadNetworkGraph")

class RoadNetworkGraph:
    """
    Represents the urban road network topology as a directed weighted graph.
    Nodes: Highway junctions and city transit hubs with GPS coordinates.
    Edges: Directed road segments with distance, speed limits, live speed, and congestion state.
    """
    
    # Minneapolis - St. Paul Twin Cities Junction Nodes (Lat, Lon, Description)
    DEFAULT_NODES = {
        "DOWNTOWN_MPLS": {"lat": 44.9778, "lon": -93.2650, "name": "Downtown Minneapolis"},
        "DOWNTOWN_STP":  {"lat": 44.9537, "lon": -93.0900, "name": "Downtown St. Paul"},
        "AIRPORT_MSP":   {"lat": 44.8848, "lon": -93.2223, "name": "MSP International Airport"},
        "BLOOMINGTON":   {"lat": 44.8408, "lon": -93.2983, "name": "Bloomington / MOA"},
        "ROSEVILLE":     {"lat": 45.0061, "lon": -93.1566, "name": "Roseville Junction"},
        "PLYMOUTH":      {"lat": 44.9939, "lon": -93.4566, "name": "Plymouth West"},
        "EDINA":         {"lat": 44.8897, "lon": -93.3501, "name": "Edina South"},
        "WOODBURY":      {"lat": 44.9239, "lon": -92.9594, "name": "Woodbury East"},
        "BROOKLYN_CTR":  {"lat": 45.0741, "lon": -93.2922, "name": "Brooklyn Center North"},
        "EAGAN":         {"lat": 44.8041, "lon": -93.1669, "name": "Eagan South"}
    }

    def __init__(self, nodes: Optional[Dict] = None, auto_load_default: bool = False):
        self.nodes = nodes if nodes else self.DEFAULT_NODES.copy()
        # Adjacency list: node -> list of outgoing edges
        self.adjacency: Dict[str, List[Dict]] = {node: [] for node in self.nodes}
        self.edge_map: Dict[str, Dict] = {} # segment_id -> edge details
        
        if auto_load_default:
            corridor_file = os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw", "metro_corridor_network.csv")
            if os.path.exists(corridor_file):
                try:
                    df = pd.read_csv(corridor_file)
                    latest_df = df.sort_values(by="timestamp").groupby("segment_id").last().reset_index()
                    for _, row in latest_df.iterrows():
                        if row["source_node"] in self.nodes and row["target_node"] in self.nodes:
                            self.add_edge(
                                segment_id=row["segment_id"],
                                road_name=row["road_name"],
                                source=row["source_node"],
                                target=row["target_node"],
                                distance_km=row["distance_km"],
                                speed_limit_kmh=row["speed_limit_kmh"],
                                current_speed_kmh=row.get("average_speed", row["speed_limit_kmh"]),
                                congestion_level=row.get("congestion_level", "LOW")
                            )
                except Exception as e:
                    logger.warning(f"Could not auto-load default corridor edges: {e}")

    def add_edge(
        self,
        segment_id: str,
        road_name: str,
        source: str,
        target: str,
        distance_km: float,
        speed_limit_kmh: float,
        current_speed_kmh: Optional[float] = None,
        congestion_level: str = "LOW"
    ):
        """Adds a directed road segment to the network graph."""
        if source not in self.nodes or target not in self.nodes:
            raise ValueError(f"Source '{source}' or Target '{target}' not present in node set.")
            
        speed = current_speed_kmh if current_speed_kmh else speed_limit_kmh
        edge = {
            "segment_id": segment_id,
            "road_name": road_name,
            "source": source,
            "target": target,
            "distance_km": float(distance_km),
            "speed_limit_kmh": float(speed_limit_kmh),
            "current_speed_kmh": float(speed),
            "congestion_level": congestion_level.upper()
        }
        
        self.adjacency[source].append(edge)
        self.edge_map[segment_id] = edge

    def update_edge_traffic(self, segment_id: str, current_speed_kmh: float, congestion_level: str):
        """Dynamically updates the live traffic speed and congestion state of a road segment."""
        if segment_id in self.edge_map:
            self.edge_map[segment_id]["current_speed_kmh"] = max(5.0, float(current_speed_kmh))
            self.edge_map[segment_id]["congestion_level"] = congestion_level.upper()

    def get_edge_weight(self, edge: Dict, alpha: float = 0.50, mode: str = "dynamic") -> float:
        """
        Calculates edge traversal cost:
          - 'distance': Raw physical distance in kilometers
          - 'free_flow': Travel time at speed limit in minutes: (dist / speed_limit) * 60
          - 'dynamic': Dynamic travel time penalizing congestion:
              travel_time = (dist / current_speed) * 60
              cost = travel_time * (1.0 + alpha * congestion_multiplier)
        """
        dist = edge["distance_km"]
        if mode == "distance":
            return dist
            
        if mode == "free_flow":
            return (dist / max(10.0, edge["speed_limit_kmh"])) * 60.0
            
        # Dynamic mode
        speed = max(5.0, edge["current_speed_kmh"])
        travel_time_min = (dist / speed) * 60.0
        
        cong_multipliers = {
            "LOW": 0.0,
            "MEDIUM": 0.35,
            "HIGH": 0.90,
            "SEVERE": 2.20
        }
        multiplier = cong_multipliers.get(edge["congestion_level"], 0.0)
        return travel_time_min * (1.0 + alpha * multiplier)

    @classmethod
    def load_from_dataframe(cls, df: pd.DataFrame) -> "RoadNetworkGraph":
        """Instantiates and populates the graph from a corridor dataset."""
        graph = cls()
        
        # Take latest record per segment to represent current road conditions
        latest_df = df.sort_values(by="timestamp").groupby("segment_id").last().reset_index()
        
        for _, row in latest_df.iterrows():
            graph.add_edge(
                segment_id=row["segment_id"],
                road_name=row["road_name"],
                source=row["source_node"],
                target=row["target_node"],
                distance_km=row["distance_km"],
                speed_limit_kmh=row["speed_limit_kmh"],
                current_speed_kmh=row.get("average_speed", row["speed_limit_kmh"]),
                congestion_level=row.get("congestion_level", "LOW")
            )
        logger.info(f"Loaded road network with {len(graph.nodes)} junctions and {len(graph.edge_map)} road segments.")
        return graph
