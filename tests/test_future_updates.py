import pytest
import os
import pandas as pd
import numpy as np

from src.routing.graph import RoadNetworkGraph
from src.routing.eco_routing import (
    calculate_segment_fuel_consumption,
    multi_objective_dijkstra,
    compute_eco_routing_comparison
)
from src.routing.graph_analytics import NetworkGraphAnalytics
from src.simulation.signal_controller import AdaptiveSignalController, simulate_junction_signal
from src.ml.drift_monitor import TrafficModelDriftMonitor
from src.utils.powerbi_streaming import PowerBIStreamingClient
from src.ml.forecasting_models import MultiHorizonTrafficForecaster

def test_eco_routing_physics_and_routing():
    """Validates CMEM fuel calculation and multi-objective Pareto optimization."""
    # Test physical emission model
    fuel, co2 = calculate_segment_fuel_consumption(distance_km=10.0, current_speed_kmh=60.0, speed_limit_kmh=90.0, congestion_level="LOW")
    assert fuel > 0.5 and fuel < 2.5
    assert co2 > 1.0 and co2 < 6.0
    
    # Test severe congestion idling penalty
    fuel_severe, co2_severe = calculate_segment_fuel_consumption(distance_km=10.0, current_speed_kmh=15.0, speed_limit_kmh=90.0, congestion_level="SEVERE")
    assert fuel_severe > fuel
    assert co2_severe > co2
    
    # Test Pareto routing comparison
    graph = RoadNetworkGraph(auto_load_default=True)
    res = compute_eco_routing_comparison(graph, "DOWNTOWN_MPLS", "AIRPORT_MSP")
    assert "fastest_route" in res
    assert "greenest_route" in res
    assert "cheapest_route" in res
    assert "impact_analytics" in res
    assert res["fastest_route"]["total_distance_km"] > 0.0

def test_graph_analytics_and_centrality():
    """Validates PageRank, Betweenness Centrality, and GraphFrames DataFrame schemas."""
    graph = RoadNetworkGraph(auto_load_default=True)
    analytics = NetworkGraphAnalytics(graph)
    
    df_centrality = analytics.compute_centrality_metrics()
    assert len(df_centrality) == len(graph.nodes)
    assert "pagerank" in df_centrality.columns
    assert "betweenness_centrality" in df_centrality.columns
    assert "criticality_index" in df_centrality.columns
    assert df_centrality["pagerank"].sum() > 0.5
    
    df_bottlenecks = analytics.compute_edge_bottlenecks(top_k=5)
    assert len(df_bottlenecks) <= 5
    assert "edge_betweenness" in df_bottlenecks.columns
    
    gf_schemas = analytics.get_spark_graphframes_schema()
    assert "vertices_df" in gf_schemas
    assert "edges_df" in gf_schemas
    assert "id" in gf_schemas["vertices_df"].columns
    assert "src" in gf_schemas["edges_df"].columns

def test_adaptive_signal_controller():
    """Validates Webster's optimal cycle equation and green phase allocation."""
    controller = AdaptiveSignalController("DOWNTOWN_MPLS", "Downtown Minneapolis")
    volumes = {"Main Arterial": 3200.0, "Cross Street": 1100.0}
    timing = controller.compute_signal_timing(volumes)
    
    assert timing["optimal_cycle_seconds"] >= 45.0
    assert timing["optimal_cycle_seconds"] <= 140.0
    assert timing["delay_reduction_pct"] > 0.0
    assert "phase_timings" in timing
    assert timing["phase_timings"]["Main Arterial"]["green_seconds"] > timing["phase_timings"]["Cross Street"]["green_seconds"]

def test_mlops_drift_monitor():
    """Validates statistical KS-test, PSI calculation, and automated self-retraining trigger."""
    monitor = TrafficModelDriftMonitor()
    
    # Test PSI with identical distributions -> ~0.0
    s1 = pd.Series(np.random.normal(50, 10, 1000))
    s2 = pd.Series(np.random.normal(50, 10, 1000))
    psi = monitor.calculate_psi(s1, s2)
    assert psi < 0.15
    
    # Test Drift Audit
    test_df = pd.DataFrame({
        "traffic_volume": np.random.randint(500, 4500, 100),
        "average_speed": np.random.uniform(20, 90, 100),
        "occupancy": np.random.uniform(0.05, 0.85, 100),
        "temperature_c": np.random.uniform(-10, 35, 100)
    })
    audit = monitor.run_full_drift_audit(test_df)
    assert "feature_drift" in audit
    assert "trigger_retraining" in audit
    assert audit["records_analyzed"] == 100

def test_powerbi_streaming_client(tmp_path):
    """Validates Power BI REST client simulation mode and circular buffer."""
    buf_file = str(tmp_path / "powerbi_test_buffer.json")
    client = PowerBIStreamingClient(push_url=None, buffer_file=buf_file)
    
    conn = client.test_connection()
    assert conn["status"] == "SIMULATION_MODE"
    assert conn["connected"] is True
    
    events = [
        {"segment_id": "TEST_SEG_1", "traffic_volume": 2800, "current_speed_kmh": 62.0},
        {"segment_id": "TEST_SEG_2", "traffic_volume": 4100, "current_speed_kmh": 28.0}
    ]
    res = client.push_events(events)
    assert res["records_pushed"] == 2
    assert os.path.exists(buf_file)

def test_multi_horizon_forecasting():
    """Validates multi-step sequence forecasting across t+15, t+30, t+60, t+120 min."""
    forecaster = MultiHorizonTrafficForecaster()
    traj = forecaster.predict_future_trajectory(current_volume=3200.0, current_speed=55.0, temperature_c=18.0, current_hour=17)
    
    assert "trajectory" in traj
    assert len(traj["trajectory"]) == 4
    horizons = [t["horizon"] for t in traj["trajectory"]]
    assert horizons == ["t+15m", "t+30m", "t+60m", "t+120m"]
    for t in traj["trajectory"]:
        assert t["predicted_volume"] > 0
        assert t["lower_bound_95"] <= t["predicted_volume"]
        assert t["upper_bound_95"] >= t["predicted_volume"]
