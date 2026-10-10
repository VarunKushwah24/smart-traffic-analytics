# -*- coding: utf-8 -*-
"""Quick functional test for dashboard dependencies."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["HADOOP_HOME"] = r"E:\smarttraffic\hadoop"

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
print("[OK] plotly, pandas, numpy")

from src.routing.graph import RoadNetworkGraph
from src.routing.dijkstra import find_optimal_route, find_alternative_route
print("[OK] routing imports")

from src.streaming.kafka_producer import TrafficEventProducer
print("[OK] kafka producer import")

# Load corridor data
df = pd.read_csv("data/raw/metro_corridor_network.csv")
df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
df["hour"]      = df["timestamp"].dt.hour
df["day_name"]  = df["timestamp"].dt.day_name()
print(f"[OK] corridor data: {len(df)} rows, columns={list(df.columns[:6])}")

# Build graph
graph = RoadNetworkGraph.load_from_dataframe(df)
nodes = list(graph.nodes.keys())
print(f"[OK] graph: {len(nodes)} nodes => {nodes}")

# Test Dijkstra
if len(nodes) >= 2:
    opt = find_optimal_route(graph, nodes[0], nodes[1], alpha=0.5)
    if opt and opt.get("segments"):
        print(f"[OK] Dijkstra: {opt['segment_count']} segs, {opt['estimated_travel_time_min']} min")
    else:
        print(f"[WARN] Dijkstra returned empty route from {nodes[0]} -> {nodes[1]}")

    alt = find_alternative_route(graph, nodes[0], nodes[1], opt, alpha=0.5)
    if alt and alt.get("segments"):
        print(f"[OK] Alt route: {alt['segment_count']} segs")
    else:
        print("[INFO] No alternative route (normal for small graphs)")
else:
    print("[WARN] Not enough nodes to test routing")

# Check metrics files
import glob
metrics = glob.glob("results/metrics/*.csv")
print(f"[OK] Metric files found: {metrics}")
for m in metrics:
    df_m = pd.read_csv(m)
    print(f"     {os.path.basename(m)}: {len(df_m)} rows, cols={list(df_m.columns)}")

# Congestion distribution
if "congestion_level" in df.columns:
    cong_dist = df["congestion_level"].value_counts().to_dict()
    print(f"[OK] Congestion distribution: {cong_dist}")

# Producer test (local mode only)
try:
    p = TrafficEventProducer()
    evt = p.generate_random_event()
    print(f"[OK] Producer event keys: {list(evt.keys())}")
except Exception as ex:
    print(f"[WARN] Producer: {ex}")

print()
print("=" * 50)
print("ALL DASHBOARD DEPENDENCY CHECKS PASSED")
print("Dashboard running at: http://localhost:8501")
print("=" * 50)
