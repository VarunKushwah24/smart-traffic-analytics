import math
from typing import Dict, List, Optional
from src.utils.logger import setup_logger

logger = setup_logger("SignalController")

class AdaptiveSignalController:
    """
    Closed-loop adaptive traffic signal controller implementing Webster's
    Optimal Cycle Length and Dynamic Green Phase Allocation formula.
    
    Equations:
      1. Flow Ratio: y_i = q_i / s_i
      2. Total Intersection Flow Ratio: Y = sum(y_i)
      3. Webster's Minimum Delay Cycle Length: C_0 = (1.5 * L + 5) / (1 - Y)
      4. Dynamic Green Time per phase: g_i = (y_i / Y) * (C_0 - L)
      5. Webster Vehicle Delay Formula:
         d = [C*(1 - lambda)^2] / [2*(1 - lambda*x)] + [x^2] / [2*q*(1 - x)]
    """

    DEFAULT_SATURATION_FLOW = 1900.0  # vehicles per hour of green per lane
    DEFAULT_LOST_TIME_PER_PHASE = 4.0 # seconds (amber clearance + startup delay)
    DEFAULT_YELLOW_TIME = 3.5         # seconds
    DEFAULT_ALL_RED_TIME = 1.5        # seconds

    def __init__(
        self,
        junction_id: str,
        junction_name: str,
        num_phases: int = 2,
        min_cycle_sec: float = 45.0,
        max_cycle_sec: float = 140.0,
        min_green_sec: float = 12.0
    ):
        self.junction_id = junction_id
        self.junction_name = junction_name
        self.num_phases = num_phases
        self.min_cycle_sec = min_cycle_sec
        self.max_cycle_sec = max_cycle_sec
        self.min_green_sec = min_green_sec
        self.total_lost_time = num_phases * self.DEFAULT_LOST_TIME_PER_PHASE

    def compute_signal_timing(
        self,
        phase_volumes: Dict[str, float],
        lanes_per_phase: Optional[Dict[str, int]] = None,
        fixed_cycle_compare_sec: float = 90.0
    ) -> Dict:
        """
        Calculates optimal adaptive cycle timing and phase splits based on real-time traffic volumes.
        
        Args:
          phase_volumes: Dict mapping phase name (e.g. 'North-South Corridor', 'East-West Cross') to volume in vehicles/hour.
          lanes_per_phase: Dict mapping phase name to number of active approach lanes (default 2).
          fixed_cycle_compare_sec: Static pre-timed cycle benchmark for comparison.
        """
        lanes_per_phase = lanes_per_phase or {p: 2 for p in phase_volumes}
        
        flow_ratios = {}
        saturation_flows = {}
        
        for phase, vol in phase_volumes.items():
            num_lanes = lanes_per_phase.get(phase, 2)
            sat_flow = num_lanes * self.DEFAULT_SATURATION_FLOW
            saturation_flows[phase] = sat_flow
            flow_ratio = max(0.05, min(0.92, vol / sat_flow))
            flow_ratios[phase] = flow_ratio
            
        Y = sum(flow_ratios.values())
        is_oversaturated = False
        
        if Y >= 0.95:
            is_oversaturated = True
            effective_Y = 0.90  # Cap flow ratio to prevent mathematical singularity
        else:
            effective_Y = Y
            
        # Webster's Optimal Cycle Equation
        raw_C0 = (1.5 * self.total_lost_time + 5.0) / (1.0 - effective_Y)
        optimal_cycle = max(self.min_cycle_sec, min(self.max_cycle_sec, raw_C0))
        available_green_time = max(10.0, optimal_cycle - self.total_lost_time)
        
        # Calculate dynamic green splits
        phase_timings = {}
        phase_delays_adaptive = {}
        phase_delays_fixed = {}
        
        fixed_green_per_phase = (fixed_cycle_compare_sec - self.total_lost_time) / len(phase_volumes)
        
        for phase, y_i in flow_ratios.items():
            # Adaptive green time proportional to demand
            green_i = max(self.min_green_sec, (y_i / effective_Y) * available_green_time)
            yellow_i = self.DEFAULT_YELLOW_TIME
            red_i = optimal_cycle - green_i - yellow_i
            
            phase_timings[phase] = {
                "volume_vph": round(phase_volumes[phase], 1),
                "green_seconds": round(green_i, 1),
                "yellow_seconds": round(yellow_i, 1),
                "red_seconds": round(red_i, 1),
                "green_ratio_pct": round((green_i / optimal_cycle) * 100.0, 1)
            }
            
            # Webster Delay calculation (Adaptive)
            q_sec = max(0.01, phase_volumes[phase] / 3600.0)
            s_sec = max(0.1, saturation_flows[phase] / 3600.0)
            lam_adapt = green_i / optimal_cycle
            x_adapt = min(0.98, q_sec / max(0.001, lam_adapt * s_sec))
            
            delay_adapt = (optimal_cycle * ((1.0 - lam_adapt) ** 2)) / (2.0 * max(0.01, (1.0 - lam_adapt * x_adapt)))
            delay_adapt += (x_adapt ** 2) / (2.0 * q_sec * max(0.01, (1.0 - x_adapt)))
            phase_delays_adaptive[phase] = round(max(2.0, delay_adapt), 1)
            
            # Webster Delay calculation (Static Fixed Time)
            lam_fix = fixed_green_per_phase / fixed_cycle_compare_sec
            x_fix = min(0.99, q_sec / max(0.001, lam_fix * s_sec))
            delay_fix = (fixed_cycle_compare_sec * ((1.0 - lam_fix) ** 2)) / (2.0 * max(0.01, (1.0 - lam_fix * x_fix)))
            delay_fix += (x_fix ** 2) / (2.0 * q_sec * max(0.01, (1.0 - x_fix)))
            phase_delays_fixed[phase] = round(max(2.0, delay_fix), 1)
            
        avg_adaptive_delay = sum(phase_delays_adaptive.values()) / len(phase_delays_adaptive)
        avg_fixed_delay = sum(phase_delays_fixed.values()) / len(phase_delays_fixed)
        delay_reduction_pct = round(((avg_fixed_delay - avg_adaptive_delay) / max(0.1, avg_fixed_delay)) * 100.0, 1)
        
        # Environmental impact of reduced idling delay
        total_hourly_veh = sum(phase_volumes.values())
        idling_saved_veh_hours = (max(0.0, avg_fixed_delay - avg_adaptive_delay) * total_hourly_veh) / 3600.0
        fuel_saved_liters_per_hour = round(idling_saved_veh_hours * 0.95, 2)  # ~0.95 L/hr idle consumption
        co2_saved_kg_per_hour = round(fuel_saved_liters_per_hour * 2.31, 2)
        
        return {
            "junction_id": self.junction_id,
            "junction_name": self.junction_name,
            "optimal_cycle_seconds": round(optimal_cycle, 1),
            "fixed_benchmark_cycle_seconds": fixed_cycle_compare_sec,
            "flow_ratio_sum_Y": round(Y, 3),
            "is_oversaturated": is_oversaturated,
            "phase_timings": phase_timings,
            "average_delay_adaptive_sec": round(avg_adaptive_delay, 1),
            "average_delay_fixed_sec": round(avg_fixed_delay, 1),
            "delay_reduction_pct": delay_reduction_pct,
            "environmental_savings": {
                "idling_saved_veh_hours_per_hr": round(idling_saved_veh_hours, 2),
                "fuel_saved_liters_per_hr": fuel_saved_liters_per_hour,
                "co2_saved_kg_per_hr": co2_saved_kg_per_hour
            }
        }

def simulate_junction_signal(
    junction_id: str = "DOWNTOWN_MPLS",
    junction_name: str = "Downtown Minneapolis (I-94 & I-35W)",
    corridor_volume: float = 3850.0,
    cross_street_volume: float = 1450.0
) -> Dict:
    """Convenience simulation runner for dashboard and streaming controller integration."""
    controller = AdaptiveSignalController(junction_id=junction_id, junction_name=junction_name)
    phase_volumes = {
        "Main Arterial (I-94 / I-35W)": corridor_volume,
        "Connecting Collector / Arterial": cross_street_volume
    }
    return controller.compute_signal_timing(phase_volumes)
