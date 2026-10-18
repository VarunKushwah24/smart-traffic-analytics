import os
import math
import heapq
from typing import Dict, List, Tuple, Optional
from src.routing.graph import RoadNetworkGraph
from src.utils.logger import setup_logger

logger = setup_logger("EcoRouting")

# Environmental & Fuel Parameters (EPA / CMEM Model Standards)
CO2_KG_PER_LITER_GASOLINE = 2.31
FUEL_PRICE_PER_LITER = 1.45  # USD / standard fuel rate
TIME_VALUE_PER_HOUR = 22.0   # USD / hour for delay economic cost

# Congestion Acceleration & Idle Penalty Multipliers
CONGESTION_FUEL_MULTIPLIER = {
    "LOW": 1.00,
    "MEDIUM": 1.22,
    "HIGH": 1.58,
    "SEVERE": 2.25
}

def calculate_segment_fuel_consumption(
    distance_km: float,
    current_speed_kmh: float,
    speed_limit_kmh: float,
    congestion_level: str = "LOW"
) -> Tuple[float, float]:
    """
    Computes estimated fuel consumption (Liters) and CO2 emissions (kg)
    for a road segment using a physics-based Comprehensive Modal Emission Model (CMEM).
    
    Returns:
        (fuel_liters, co2_emissions_kg)
    """
    speed = max(5.0, min(current_speed_kmh, 140.0))
    
    # Physics parameters: Rolling resistance + Engine friction + Aerodynamic drag
    # VT-Micro model empirical coefficients for standard light-duty vehicle
    c_idle = 0.042   # L/km base idling and internal resistance
    c_speed = 1.15   # L*km/h low speed penalty
    c_aero = 0.0000078 # Aerodynamic drag coefficient at higher velocity
    
    base_fuel_rate_l_per_km = c_idle + (c_speed / speed) + (c_aero * (speed ** 2))
    
    # Apply congestion acceleration/deceleration idling penalty
    cong_factor = CONGESTION_FUEL_MULTIPLIER.get(congestion_level.upper(), 1.0)
    effective_fuel_rate = base_fuel_rate_l_per_km * cong_factor
    
    total_fuel_liters = effective_fuel_rate * distance_km
    total_co2_kg = total_fuel_liters * CO2_KG_PER_LITER_GASOLINE
    
    return round(total_fuel_liters, 4), round(total_co2_kg, 4)

def evaluate_path_metrics(graph: RoadNetworkGraph, path_nodes: List[str], path_edges: List[Dict]) -> Dict:
    """
    Evaluates comprehensive metrics (Time, Fuel, CO2, Cost, Delay) for a reconstructed path.
    """
    total_dist = sum(e["distance_km"] for e in path_edges)
    total_travel_time = sum((e["distance_km"] / max(5.0, e["current_speed_kmh"])) * 60.0 for e in path_edges)
    free_flow_time = sum((e["distance_km"] / e["speed_limit_kmh"]) * 60.0 for e in path_edges)
    delay_min = max(0.0, total_travel_time - free_flow_time)
    
    total_fuel = 0.0
    total_co2 = 0.0
    
    for e in path_edges:
        f, co2 = calculate_segment_fuel_consumption(
            distance_km=e["distance_km"],
            current_speed_kmh=e["current_speed_kmh"],
            speed_limit_kmh=e["speed_limit_kmh"],
            congestion_level=e["congestion_level"]
        )
        total_fuel += f
        total_co2 += co2
        
    fuel_cost = total_fuel * FUEL_PRICE_PER_LITER
    time_cost = (delay_min / 60.0) * TIME_VALUE_PER_HOUR
    total_monetary_cost = fuel_cost + time_cost
    
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
        "nodes": path_nodes,
        "segments": path_edges,
        "segment_count": len(path_edges),
        "total_distance_km": round(total_dist, 2),
        "estimated_travel_time_min": round(total_travel_time, 2),
        "free_flow_travel_time_min": round(free_flow_time, 2),
        "delay_minutes": round(delay_min, 2),
        "fuel_consumption_liters": round(total_fuel, 3),
        "co2_emissions_kg": round(total_co2, 3),
        "monetary_cost_usd": round(total_monetary_cost, 2),
        "overall_condition": overall_cond,
        "coordinates": coords
    }

def multi_objective_dijkstra(
    graph: RoadNetworkGraph,
    source: str,
    destination: str,
    objective: str = "fastest",
    weights: Optional[Dict[str, float]] = None,
    excluded_edges: Optional[set] = None
) -> Optional[Dict]:
    """
    Computes optimal path according to multi-objective criterion:
      - 'fastest': Minimizes dynamic travel time
      - 'greenest': Minimizes CO2 emissions and fuel consumption
      - 'cheapest': Minimizes combined monetary fuel + delay cost
      - 'balanced': Multi-criteria Pareto trade-off
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
            "delay_minutes": 0.0,
            "fuel_consumption_liters": 0.0,
            "co2_emissions_kg": 0.0,
            "monetary_cost_usd": 0.0,
            "overall_condition": "LOW",
            "coordinates": [(graph.nodes[source]["lat"], graph.nodes[source]["lon"])]
        }
        
    excluded_edges = excluded_edges or set()
    weights = weights or {"time": 0.45, "co2": 0.40, "cost": 0.15}
    
    pq = [(0.0, source)]
    costs = {node: float("inf") for node in graph.nodes}
    costs[source] = 0.0
    predecessors = {}
    
    while pq:
        curr_cost, u = heapq.heappop(pq)
        
        if u == destination:
            break
            
        if curr_cost > costs[u]:
            continue
            
        for edge in graph.adjacency.get(u, []):
            if edge["segment_id"] in excluded_edges:
                continue
                
            v = edge["target"]
            dist = edge["distance_km"]
            speed = max(5.0, edge["current_speed_kmh"])
            travel_time_min = (dist / speed) * 60.0
            
            fuel, co2 = calculate_segment_fuel_consumption(
                dist, speed, edge["speed_limit_kmh"], edge["congestion_level"]
            )
            
            # Formulate edge cost based on selected objective
            if objective == "fastest":
                # Congestion-weighted travel time
                cong_mult = CONGESTION_FUEL_MULTIPLIER.get(edge["congestion_level"], 1.0)
                edge_cost = travel_time_min * cong_mult
            elif objective == "greenest":
                # Primary minimization: CO2 emissions
                edge_cost = co2
            elif objective == "cheapest":
                # Combined fuel cost + delay value
                free_time = (dist / edge["speed_limit_kmh"]) * 60.0
                delay = max(0.0, travel_time_min - free_time)
                edge_cost = (fuel * FUEL_PRICE_PER_LITER) + ((delay / 60.0) * TIME_VALUE_PER_HOUR)
            elif objective == "balanced":
                # Normalized composite cost
                norm_time = travel_time_min / 10.0
                norm_co2 = co2 / 1.5
                norm_cost = ((fuel * FUEL_PRICE_PER_LITER) + 0.5) / 2.0
                edge_cost = (
                    weights.get("time", 0.45) * norm_time +
                    weights.get("co2", 0.40) * norm_co2 +
                    weights.get("cost", 0.15) * norm_cost
                )
            else:
                edge_cost = dist
                
            new_cost = curr_cost + edge_cost
            if new_cost < costs[v]:
                costs[v] = new_cost
                predecessors[v] = (u, edge)
                heapq.heappush(pq, (new_cost, v))
                
    if destination not in predecessors:
        logger.warning(f"No reachable eco-route between {source} and {destination}.")
        return None
        
    curr = destination
    path_nodes = [curr]
    path_edges = []
    
    while curr != source:
        prev_node, edge = predecessors[curr]
        path_edges.append(edge)
        curr = prev_node
        path_nodes.append(curr)
        
    path_nodes.reverse()
    path_edges.reverse()
    
    res = evaluate_path_metrics(graph, path_nodes, path_edges)
    res["source"] = source
    res["destination"] = destination
    res["objective"] = objective
    return res

def compute_eco_routing_comparison(
    graph: RoadNetworkGraph,
    source: str,
    destination: str
) -> Dict:
    """
    Computes and compares Pareto routes across all three optimization objectives:
      1. Fastest Route (Traditional dynamic Dijkstra)
      2. Greenest / Eco Route (CMEM CO2 minimization)
      3. Cheapest / Economic Route (Financial cost minimization)
    
    Returns a unified comparative dictionary with SDG 13 impact analytics.
    """
    fastest = multi_objective_dijkstra(graph, source, destination, objective="fastest")
    greenest = multi_objective_dijkstra(graph, source, destination, objective="greenest")
    cheapest = multi_objective_dijkstra(graph, source, destination, objective="cheapest")
    
    if not fastest or not greenest:
        return {"error": "Path unreachable"}
        
    # Calculate CO2 and Fuel savings achieved by Greenest vs Fastest
    co2_saved_kg = round(max(0.0, fastest["co2_emissions_kg"] - greenest["co2_emissions_kg"]), 3)
    co2_saved_pct = round((co2_saved_kg / max(0.001, fastest["co2_emissions_kg"])) * 100.0, 1)
    
    fuel_saved_liters = round(max(0.0, fastest["fuel_consumption_liters"] - greenest["fuel_consumption_liters"]), 3)
    fuel_saved_pct = round((fuel_saved_liters / max(0.001, fastest["fuel_consumption_liters"])) * 100.0, 1)
    
    time_penalty_min = round(max(0.0, greenest["estimated_travel_time_min"] - fastest["estimated_travel_time_min"]), 2)
    
    return {
        "source": source,
        "destination": destination,
        "fastest_route": fastest,
        "greenest_route": greenest,
        "cheapest_route": cheapest,
        "impact_analytics": {
            "co2_saved_kg": co2_saved_kg,
            "co2_saved_pct": co2_saved_pct,
            "fuel_saved_liters": fuel_saved_liters,
            "fuel_saved_pct": fuel_saved_pct,
            "time_penalty_min": time_penalty_min,
            "sdg_13_trees_equivalent": round(co2_saved_kg * 0.045, 3), # ~22kg CO2 per mature tree/yr
            "sdg_alignment": "SDG 11 (Sustainable Cities) & SDG 13 (Climate Action)"
        }
    }
