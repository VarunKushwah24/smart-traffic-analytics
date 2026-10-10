import pytest
from src.routing.graph import RoadNetworkGraph
from src.routing.dijkstra import dijkstra_shortest_path, find_optimal_route, find_alternative_route

@pytest.fixture
def sample_graph():
    graph = RoadNetworkGraph(nodes={
        "A": {"lat": 44.0, "lon": -93.0, "name": "Node A"},
        "B": {"lat": 44.1, "lon": -93.1, "name": "Node B"},
        "C": {"lat": 44.2, "lon": -93.2, "name": "Node C"},
        "D": {"lat": 44.3, "lon": -93.3, "name": "Node D"}
    })
    # Direct edge A -> D is short (10 km) but severely congested (15 km/h)
    graph.add_edge("E1", "Direct Highway", "A", "D", distance_km=10.0, speed_limit_kmh=100.0, current_speed_kmh=15.0, congestion_level="SEVERE")
    
    # Detour A -> B -> C -> D is longer (18 km) but completely free flow (90 km/h)
    graph.add_edge("E2", "Beltway 1", "A", "B", distance_km=6.0, speed_limit_kmh=90.0, current_speed_kmh=90.0, congestion_level="LOW")
    graph.add_edge("E3", "Beltway 2", "B", "C", distance_km=6.0, speed_limit_kmh=90.0, current_speed_kmh=90.0, congestion_level="LOW")
    graph.add_edge("E4", "Beltway 3", "C", "D", distance_km=6.0, speed_limit_kmh=90.0, current_speed_kmh=90.0, congestion_level="LOW")
    return graph

def test_distance_mode_picks_shortest_distance(sample_graph):
    # In pure distance mode, direct highway should be chosen because 10 km < 18 km
    route = dijkstra_shortest_path(sample_graph, "A", "D", mode="distance")
    assert route is not None
    assert route["nodes"] == ["A", "D"]
    assert route["total_distance_km"] == 10.0

def test_dynamic_mode_diverts_around_severe_congestion(sample_graph):
    # In dynamic mode, travel time via direct = (10/15)*60 * (1 + 0.5 * 2.2) = 40 * 2.1 = 84 min
    # Travel time via detour = 3 * (6/90)*60 * 1.0 = 3 * 4 = 12 min
    # Dijkstra must pick the free-flow detour!
    route = find_optimal_route(sample_graph, "A", "D", alpha=0.50)
    assert route is not None
    assert route["nodes"] == ["A", "B", "C", "D"]
    assert route["total_distance_km"] == 18.0
    assert route["estimated_travel_time_min"] < 15.0

def test_alternative_route_generation(sample_graph):
    opt_route = find_optimal_route(sample_graph, "A", "D", alpha=0.50)
    alt_route = find_alternative_route(sample_graph, "A", "D", opt_route, alpha=0.50)
    assert alt_route is not None
    assert alt_route["nodes"] != opt_route["nodes"]

def test_same_source_and_destination(sample_graph):
    route = find_optimal_route(sample_graph, "A", "A")
    assert route is not None
    assert route["total_distance_km"] == 0.0
    assert route["nodes"] == ["A"]
