import os
from typing import Dict, List, Tuple, Optional
import pandas as pd
import numpy as np
import networkx as nx
from src.routing.graph import RoadNetworkGraph
from src.utils.logger import setup_logger

logger = setup_logger("GraphAnalytics")

class NetworkGraphAnalytics:
    """
    Performs distributed and topological graph analytics on the road network:
      1. PageRank Centrality: Identifies the most critical traffic flow convergence hubs.
      2. Betweenness Centrality: Identifies systemic bottleneck junctions handling highest transit load.
      3. Closeness Centrality: Measures geometric accessibility across the network.
      4. Degree Centrality: In-degree and out-degree connectivity.
      5. Edge Centrality & Bottleneck Vulnerability Index.
      6. PySpark GraphFrames DataFrames exporter (vertices and edges schemas).
    """

    def __init__(self, graph: RoadNetworkGraph):
        self.road_graph = graph
        self.nx_graph = self._build_networkx_graph()

    def _build_networkx_graph(self) -> nx.DiGraph:
        """Converts RoadNetworkGraph into a NetworkX directed weighted graph."""
        G = nx.DiGraph()
        
        # Add junction nodes
        for node_id, data in self.road_graph.nodes.items():
            G.add_node(
                node_id,
                name=data.get("name", node_id),
                lat=data.get("lat", 0.0),
                lon=data.get("lon", 0.0)
            )
            
        # Add directed road edges
        for source, edges in self.road_graph.adjacency.items():
            for edge in edges:
                speed = max(5.0, edge.get("current_speed_kmh", 60.0))
                travel_time = (edge["distance_km"] / speed) * 60.0
                G.add_edge(
                    source,
                    edge["target"],
                    segment_id=edge["segment_id"],
                    road_name=edge["road_name"],
                    distance_km=edge["distance_km"],
                    speed_limit_kmh=edge["speed_limit_kmh"],
                    current_speed_kmh=speed,
                    travel_time_min=travel_time,
                    weight=travel_time, # Edge weight is travel time
                    congestion_level=edge["congestion_level"]
                )
                
        return G

    def compute_centrality_metrics(self, alpha: float = 0.85) -> pd.DataFrame:
        """
        Computes PageRank, Betweenness, Closeness, and Degree Centrality for all junctions.
        """
        G = self.nx_graph
        
        # 1. PageRank (Transition probability damped by alpha)
        try:
            pagerank = nx.pagerank(G, alpha=alpha, weight="weight")
        except Exception as e:
            logger.warning(f"Fallback unweighted PageRank due to: {e}")
            pagerank = nx.pagerank(G, alpha=alpha)
            
        # 2. Betweenness Centrality (Shortest path bottleneck frequency)
        betweenness = nx.betweenness_centrality(G, weight="weight", normalized=True)
        
        # 3. Closeness Centrality (Reciprocal of distance sum to all other nodes)
        closeness = nx.closeness_centrality(G, distance="weight")
        
        # 4. Degree Centralities
        in_degrees = dict(G.in_degree())
        out_degrees = dict(G.out_degree())
        degree_cent = nx.degree_centrality(G)
        
        records = []
        for node_id in self.road_graph.nodes:
            node_info = self.road_graph.nodes[node_id]
            pr = pagerank.get(node_id, 0.0)
            bw = betweenness.get(node_id, 0.0)
            cl = closeness.get(node_id, 0.0)
            in_deg = in_degrees.get(node_id, 0)
            out_deg = out_degrees.get(node_id, 0)
            
            # Systemic Criticality Index (composite score)
            crit_score = (pr * 0.40) + (bw * 0.40) + (cl * 0.20)
            
            records.append({
                "junction_id": node_id,
                "junction_name": node_info.get("name", node_id),
                "lat": node_info.get("lat"),
                "lon": node_info.get("lon"),
                "in_degree": in_deg,
                "out_degree": out_deg,
                "total_degree": in_deg + out_deg,
                "pagerank": round(pr, 4),
                "betweenness_centrality": round(bw, 4),
                "closeness_centrality": round(cl, 4),
                "criticality_index": round(crit_score, 4)
            })
            
        df_centrality = pd.DataFrame(records).sort_values(by="criticality_index", ascending=False).reset_index(drop=True)
        return df_centrality

    def compute_edge_bottlenecks(self, top_k: int = 5) -> pd.DataFrame:
        """
        Computes Edge Betweenness Centrality to pinpoint road segments that act
        as systemic transit bottlenecks.
        """
        G = self.nx_graph
        edge_betweenness = nx.edge_betweenness_centrality(G, weight="weight", normalized=True)
        
        records = []
        for (u, v), score in edge_betweenness.items():
            edge_data = G[u][v]
            records.append({
                "segment_id": edge_data["segment_id"],
                "road_name": edge_data["road_name"],
                "source": u,
                "target": v,
                "distance_km": edge_data["distance_km"],
                "speed_kmh": edge_data["current_speed_kmh"],
                "congestion_level": edge_data["congestion_level"],
                "edge_betweenness": round(score, 4),
                "bottleneck_risk": "CRITICAL" if score > 0.15 else ("MODERATE" if score > 0.08 else "LOW")
            })
            
        df_edges = pd.DataFrame(records).sort_values(by="edge_betweenness", ascending=False).reset_index(drop=True)
        return df_edges.head(top_k)

    def get_spark_graphframes_schema(self, spark=None) -> Dict:
        """
        Prepares Vertex and Edge DataFrames conforming to Apache Spark GraphFrames specifications:
        Vertices: [id, name, lat, lon]
        Edges: [src, dst, relationship, distance_km, speed_limit_kmh, congestion_level]
        """
        vertex_data = [
            {"id": k, "name": v["name"], "lat": v["lat"], "lon": v["lon"]}
            for k, v in self.road_graph.nodes.items()
        ]
        
        edge_data = []
        for u, edges in self.road_graph.adjacency.items():
            for e in edges:
                edge_data.append({
                    "src": u,
                    "dst": e["target"],
                    "relationship": "CONNECTS_TO",
                    "segment_id": e["segment_id"],
                    "road_name": e["road_name"],
                    "distance_km": float(e["distance_km"]),
                    "speed_limit_kmh": float(e["speed_limit_kmh"]),
                    "current_speed_kmh": float(e["current_speed_kmh"]),
                    "congestion_level": e["congestion_level"]
                })
                
        df_vertices = pd.DataFrame(vertex_data)
        df_edges = pd.DataFrame(edge_data)
        
        if spark is not None:
            spark_vertices = spark.createDataFrame(df_vertices)
            spark_edges = spark.createDataFrame(df_edges)
            return {"vertices": spark_vertices, "edges": spark_edges}
            
        return {"vertices_df": df_vertices, "edges_df": df_edges}

    def export_metrics_to_csv(self, output_path: str = "results/metrics/graph_centrality_metrics.csv"):
        """Exports calculated centrality metrics to a persistent CSV for Power BI and reporting."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df = self.compute_centrality_metrics()
        df.to_csv(output_path, index=False)
        logger.info(f"Exported graph centrality metrics ({len(df)} nodes) to {output_path}")
        return df
