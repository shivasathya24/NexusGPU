import time
from typing import Dict, List, Any
from datetime import datetime
from app.config import (
    GRID_BASE_PRICE, GRID_PEAK_PRICE, PEAK_HOURS_START, PEAK_HOURS_END
)

class PowerManager:
    def __init__(self):
        # Accumulators for energy usage and savings
        self.start_time = time.time()
        self.cumulative_energy_kwh = 1240.5  # Pre-populated baseline
        self.cumulative_cost_usd = 186.2     # Pre-populated baseline
        self.saved_energy_kwh = 185.4
        self.saved_cost_usd = 41.5
        
        # Training state
        self.paused_training = False
        self.active_jobs = [
            {"id": "job_983", "name": "LLama-3-70B Fine-Tuning", "status": "Running", "gpu_ids": [0, 1, 2, 3], "priority": "Critical"},
            {"id": "job_1042", "name": "ResNet-101 Video Ingestion", "status": "Running", "gpu_ids": [4, 5], "priority": "Medium"},
            {"id": "job_1109", "name": "Stable-Diffusion-XL Pre-train", "status": "Paused", "gpu_ids": [6, 7], "priority": "Low"}
        ]
        
    def get_current_electricity_price(self) -> Dict[str, Any]:
        """
        Gets current mock electricity rate. Checks current local hour, or uses simulation hour.
        """
        current_hour = datetime.now().hour
        is_peak = PEAK_HOURS_START <= current_hour < PEAK_HOURS_END
        price = GRID_PEAK_PRICE if is_peak else GRID_BASE_PRICE
        
        return {
            "price_per_kwh": price,
            "is_peak_hour": is_peak,
            "peak_start": PEAK_HOURS_START,
            "peak_end": PEAK_HOURS_END,
            "current_hour": current_hour
        }

    def update_energy_metrics(self, current_cluster_power_w: float, power_saving_mode: bool) -> Dict[str, Any]:
        """
        Updates cumulative stats since last call. We assume a tick duration of 5 seconds (0.00138 hours).
        """
        tick_hours = 5.0 / 3600.0
        price_info = self.get_current_electricity_price()
        price = price_info["price_per_kwh"]
        
        # Standard power (without limits) would have been around 2200W for the whole cluster
        standard_power_w = 2200.0 if not self.paused_training else 500.0
        
        # Compute current consumption
        current_kwh = (current_cluster_power_w / 1000.0) * tick_hours
        current_cost = current_kwh * price
        
        # Compute baseline standard consumption (to see savings)
        std_kwh = (standard_power_w / 1000.0) * tick_hours
        std_cost = std_kwh * price
        
        # Add to accumulators
        self.cumulative_energy_kwh += current_kwh
        self.cumulative_cost_usd += current_cost
        
        # Savings accumulation (if current power is lower than standard due to eco mode/caps)
        if current_cluster_power_w < standard_power_w:
            saved_k = std_kwh - current_kwh
            saved_c = std_cost - current_cost
            self.saved_energy_kwh += saved_k
            self.saved_cost_usd += saved_c
            
        # CO2 saved factor (0.4 kg CO2 per kWh of grid energy)
        co2_saved_kg = self.saved_energy_kwh * 0.4
        
        return {
            "cumulative_energy_kwh": round(self.cumulative_energy_kwh, 2),
            "cumulative_cost_usd": round(self.cumulative_cost_usd, 2),
            "saved_energy_kwh": round(self.saved_energy_kwh, 2),
            "saved_cost_usd": round(self.saved_cost_usd, 2),
            "co2_saved_kg": round(co2_saved_kg, 2)
        }

    def get_power_recommendations(self, is_peak: bool, cluster_util: float) -> List[Dict[str, Any]]:
        recommendations = []
        
        if is_peak:
            recommendations.append({
                "id": "rec_peak_hours",
                "title": "Peak-Hour Grid Charge Active",
                "recommendation": "Pause priority 'Low' / 'Medium' training jobs until 8:00 PM to save on electricity.",
                "potential_saving": "Save up to 60% in utility cost ($0.28 -> $0.12/kWh).",
                "impact": "Low performance impact (rescheduled background workloads).",
                "action_type": "pause_training"
            })
            
        if cluster_util > 70.0 and not is_peak:
            recommendations.append({
                "id": "rec_cap_gpus",
                "title": "Activate GPU Power Caps",
                "recommendation": "Set H100 cluster power cap to 280W (default: 350W). Dynamic voltage scaling will drop power draw by 20% while only losing ~4% in deep learning throughput.",
                "potential_saving": "Estimated 400W cluster power reduction (~$15.50/day saved).",
                "impact": "Very Low (minimal processing slowdown).",
                "action_type": "cap_power"
            })
            
        if cluster_util < 15.0:
            recommendations.append({
                "id": "rec_suspend_nodes",
                "title": "Idle Compute Detected",
                "recommendation": "Consolidate VRAM checkpoints and spin down 4 cluster nodes (GPU 4 to 7) to standby power state (15W per GPU).",
                "potential_saving": "Estimated 240W continuous power savings.",
                "impact": "Medium (requires 30-second wake-up time on restart).",
                "action_type": "suspend_nodes"
            })
            
        # Default safety fallback recommendation
        if not recommendations:
            recommendations.append({
                "id": "rec_nominal",
                "title": "Energy Consumed Within Budget",
                "recommendation": "Cluster operating at optimal cost efficiency. Keep scheduled training runs active.",
                "potential_saving": "N/A",
                "impact": "None",
                "action_type": "none"
            })
            
        return recommendations

    def trigger_action(self, action_type: str) -> Dict[str, Any]:
        if action_type == "pause_training":
            self.paused_training = True
            for job in self.active_jobs:
                if job["priority"] in ["Medium", "Low"]:
                    job["status"] = "Paused"
            return {"status": "success", "message": "Low-priority training jobs paused.", "paused_training": True}
        elif action_type == "resume_training":
            self.paused_training = False
            for job in self.active_jobs:
                if job["priority"] in ["Medium", "Low"]:
                    job["status"] = "Running"
            return {"status": "success", "message": "All training jobs resumed.", "paused_training": False}
        elif action_type == "cap_power":
            # Set all GPU limits to 280W
            return {"status": "success", "message": "GPU Power Caps updated to 280W."}
        elif action_type == "suspend_nodes":
            return {"status": "success", "message": "Nodes 4-7 suspended successfully."}
        return {"status": "error", "message": "Unknown action type"}

power_manager = PowerManager()
