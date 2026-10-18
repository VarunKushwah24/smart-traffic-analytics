import heapq
from typing import Dict, List, Tuple, Optional
from src.routing.graph import RoadNetworkGraph
from src.utils.logger import setup_logger

logger = setup_logger("DijkstraRouting")

def dijkstra_shortest_path(
    graph: RoadNetworkGraph,
    source: str,
    destination: str,
    alpha: float = 0.50,
    mode: str = "dynamic",
    excluded_edges: Optional[set] = None
) -> Optional[Dict]:
    """
    Executes Dijkstra's algorithm with priority queue to find the least-cost path.
    
    Parameters:
      graph: RoadNetworkGraph instance
      source: Source junction node ID
      destination: Destination junction node ID
      alpha: Congestion penalty factor
      mode: 'dynamic' (congestion-aware), 'free_flow', or 'distance'
      excluded_edges: Set of segment_ids to exclude (useful for alternative routes)
      
    Returns:
      Dictionary containing path metrics and segment sequences, or None if unreachable.
    """
    if source not in graph.nodes or destination not in graph.nodes:
        raise ValueError(f"Invalid route query: {source} -> {destination}")
        
    if source == destination:
        return {
            "source": source,
            "destination": destination,
            "nodes": [source],
            "segments": [],
            "total_distance_km": 0.0,
            "estimated_travel_time_min": 0.0,
            "free_flow_travel_time_min": 0.0,
            "overall_condition": "LOW",
            "coordinates": [(graph.nodes[source]["lat"], graph.nodes[source]["lon"])]
        }

    excluded_edges = excluded_edges or set()
    
    # Priority Queue stores: (cumulative_cost, current_node)
    pq = [(0.0, source)]
    distances = {node: float("inf") for node in graph.nodes}
    distances[source] = 0.0
    predecessors = {} # node -> (prev_node, edge_dict)
    
    while pq:
        current_cost, u = heapq.heappop(pq)
        
        if u == destination:
            break
            
        if current_cost > distances[u]:
            continue
            
        for edge in graph.adjacency.get(u, []):
            if edge["segment_id"] in excluded_edges:
                continue
                
            v = edge["target"]
            edge_weight = graph.get_edge_weight(edge, alpha=alpha, mode=mode)
            new_cost = current_cost + edge_weight
            
            if new_cost < distances[v]:
                distances[v] = new_cost
                predecessors[v] = (u, edge)
                heapq.heappush(pq, (new_cost, v))
                
    if destination not in predecessors:
        logger.warning(f"No reachable route found between {source} and {destination}.")
        return None
        
    # Reconstruct path backwards
    curr = destination
    path_nodes = [curr]
    path_edges = []
    
    while curr != source:
        prev_node, edge = predecessors[curr]
        edge_copy = edge.copy()
        dist = edge_copy["distance_km"]
        curr_spd = max(5.0, edge_copy.get("current_speed_kmh", 60.0))
        edge_copy["estimated_time_min"] = round((dist / curr_spd) * 60.0, 1)
        edge_copy["free_flow_time_min"] = round((dist / edge_copy.get("speed_limit_kmh", 90.0)) * 60.0, 1)
        path_edges.append(edge_copy)
        curr = prev_node
        path_nodes.append(curr)
        
    path_nodes.reverse()
    path_edges.reverse()
    
    # Calculate route telemetry
    total_dist = sum(e["distance_km"] for e in path_edges)
    total_travel_time = sum((e["distance_km"] / max(5.0, e["current_speed_kmh"])) * 60.0 for e in path_edges)
    free_flow_time = sum((e["distance_km"] / e["speed_limit_kmh"]) * 60.0 for e in path_edges)
    
    # Determine dominant condition
    cong_levels = [e["congestion_level"] for e in path_edges]
    if "SEVERE" in cong_levels:
        overall_cond = "SEVERE"
    elif "HIGH" in cong_levels:
        overall_cond = "HIGH"
    elif "MEDIUM" in cong_levels:
        overall_cond = "MEDIUM"
    else:
        overall_cond = "LOW"
        
    coords = [(graph.nodes[n]["lat"], graph.nodes[n]["lon"]) for n in path_nodes]
    
    return {
        "source": source,
        "destination": destination,
        "nodes": path_nodes,
        "segments": path_edges,
        "segment_count": len(path_edges),
        "total_distance_km": round(total_dist, 2),
        "estimated_travel_time_min": round(total_travel_time, 2),
        "free_flow_travel_time_min": round(free_flow_time, 2),
        "delay_minutes": round(max(0.0, total_travel_time - free_flow_time), 2),
        "overall_condition": overall_cond,
        "coordinates": coords
    }

def find_optimal_route(graph: RoadNetworkGraph, source: str, destination: str, alpha: float = 0.50) -> Optional[Dict]:
    """Finds the congestion-optimized dynamic route."""
    return dijkstra_shortest_path(graph, source, destination, alpha=alpha, mode="dynamic")

def find_alternative_route(
    graph: RoadNetworkGraph,
    source: str,
    destination: str,
    primary_route: Dict,
    alpha: float = 0.50
) -> Optional[Dict]:
    """
    Computes a distinct alternative route by penalizing or excluding the primary bottleneck
    road segment of the primary path.
    """
    if not primary_route or not primary_route.get("segments"):
        return None
        
    segments = primary_route["segments"]
    
    # Strategy 1: Exclude the critical bottleneck segment (or single direct segment)
    if len(segments) == 1:
        excluded = {segments[0]["segment_id"]}
    else:
        bottleneck_seg = max(segments, key=lambda s: (s["distance_km"] / max(5.0, s["current_speed_kmh"])))
        excluded = {bottleneck_seg["segment_id"]}
        
    alt_route = dijkstra_shortest_path(graph, source, destination, alpha=alpha, mode="dynamic", excluded_edges=excluded)
    
    # Strategy 2: If not distinct, exclude all segments of the primary route
    if alt_route is None or alt_route["nodes"] == primary_route["nodes"]:
        all_excluded = {s["segment_id"] for s in segments}
        alt_route = dijkstra_shortest_path(graph, source, destination, alpha=alpha, mode="dynamic", excluded_edges=all_excluded)
        
    # Strategy 3: Try distance mode with excluded edges
    if alt_route is None or alt_route["nodes"] == primary_route["nodes"]:
        alt_route = dijkstra_shortest_path(graph, source, destination, mode="distance", excluded_edges=excluded)
        
    # If route is still identical to primary, return None so UI correctly reports no alternative corridor
    if alt_route is not None and alt_route["nodes"] == primary_route["nodes"]:
        return None
        
    return alt_route

