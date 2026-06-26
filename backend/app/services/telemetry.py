import random
import time
from typing import Dict, List, Any
import numpy as np
from app.config import (
    NUM_GPUS, GPU_MODEL, VRAM_CAPACITY_GB, 
    DEFAULT_POWER_LIMIT_W, TEMP_WARNING_LIMIT, TEMP_CRITICAL_LIMIT
)

class GPUSimulator:
    def __init__(self):
        self.num_gpus = NUM_GPUS
        # Initialize metrics for 8 GPUs
        self.gpus = []
        for i in range(self.num_gpus):
            self.gpus.append({
                "id": i,
                "name": f"GPU {i}: {GPU_MODEL}",
                "temp": 45.0,  # Base idle temp
                "util": 10.0,  # Base idle util
                "vram_util": 15.0, # Base VRAM
                "power_draw": 65.0, # Idle power
                "power_limit": DEFAULT_POWER_LIMIT_W,
                "fan_speed": 30.0,
                "clock_speed": 1200.0, # Idle MHz
                "health_score": 100.0,
                "throttling": False,
                "status": "Healthy",
                "nvlink_in": 0.0,
                "nvlink_out": 0.0
            })
        
        # History queue: stores lists of snapshots
        self.history: List[List[Dict[str, Any]]] = []
        self.max_history_len = 60
        self.power_saving_mode = False
        self.paused_training = False
        
        # Pre-populate some history
        for _ in range(self.max_history_len):
            self._update_metrics(tick=False)

    def _update_metrics(self, tick=True):
        # Update simulation logic
        timestamp = time.time()
        
        # NVLink topology simulation (GPUs connected in a ring or fully connected mesh)
        # We can simulate communications. GPU 0 and 1, 2 and 3, etc., are peers.
        for i in range(self.num_gpus):
            gpu = self.gpus[i]
            
            # If training is paused, utilization goes to minimum
            if self.paused_training:
                target_util = random.uniform(2.0, 5.0)
                gpu["vram_util"] = max(gpu["vram_util"] - random.uniform(0.5, 1.5), 10.0)
            elif self.power_saving_mode:
                # Limit max utilization and power draw
                target_util = random.uniform(30.0, 50.0)
                gpu["vram_util"] = min(max(gpu["vram_util"] + random.uniform(-2, 2), 40.0), 75.0)
            else:
                # Normal behavior: high load with fluctuations
                # Some GPUs are busier (e.g. Master nodes, nodes 0, 1, 4, 5)
                if i in [0, 1, 4, 5]:
                    target_util = random.uniform(70.0, 95.0)
                else:
                    target_util = random.uniform(40.0, 80.0)
                
                # Slowly drift VRAM utilization
                gpu["vram_util"] = min(max(gpu["vram_util"] + random.uniform(-1, 1), 25.0), 98.0)
                
            # Intertia on utilization
            gpu["util"] = gpu["util"] * 0.7 + target_util * 0.3
            
            # Power Limit capping
            current_max_pwr = gpu["power_limit"]
            if self.power_saving_mode:
                current_max_pwr = min(current_max_pwr, 200.0) # Cap at 200W
            
            # Power draw correlates with utilization
            base_power = 60.0
            pwr_util_factor = (gpu["util"] / 100.0) * (current_max_pwr - base_power)
            target_power = base_power + pwr_util_factor + random.uniform(-5.0, 5.0)
            gpu["power_draw"] = min(max(target_power, 55.0), current_max_pwr)
            
            # Temperature increases with power draw & utilization, cooled by fan speed
            # Heat generation factor
            heat_gen = (gpu["power_draw"] / DEFAULT_POWER_LIMIT_W) * 0.8
            # Cool factor
            cool_factor = (gpu["fan_speed"] / 100.0) * 0.65
            # Temp drift
            temp_delta = (heat_gen - cool_factor) * 2.0
            
            gpu["temp"] = min(max(gpu["temp"] + temp_delta + random.uniform(-0.2, 0.2), 38.0), 92.0)
            
            # Fan speed reacts to temperature (closed loop PID control mock)
            if gpu["temp"] < 50.0:
                target_fan = 30.0
            elif gpu["temp"] < 70.0:
                target_fan = 30.0 + (gpu["temp"] - 50.0) * 2.0  # 30% to 70%
            else:
                target_fan = 70.0 + (gpu["temp"] - 70.0) * 2.5  # 70% to 100%
            gpu["fan_speed"] = min(max(gpu["fan_speed"] * 0.85 + target_fan * 0.15, 20.0), 100.0)
            
            # Clock speed drops (thermal throttling) if temperature exceeds critical threshold
            base_clock = 1750.0  # MHz nominal
            if gpu["temp"] >= TEMP_CRITICAL_LIMIT:
                gpu["throttling"] = True
                throttle_ratio = 1.0 - ((gpu["temp"] - TEMP_CRITICAL_LIMIT) / 15.0) # throttle down to 50%
                gpu["clock_speed"] = max(base_clock * throttle_ratio, 900.0)
                gpu["status"] = "Critical"
            elif gpu["temp"] >= TEMP_WARNING_LIMIT:
                gpu["throttling"] = True
                gpu["clock_speed"] = base_clock - (gpu["temp"] - TEMP_WARNING_LIMIT) * 30.0
                gpu["status"] = "Warning"
            else:
                gpu["throttling"] = False
                # Clock speed scales slightly with utilization (GPU Boost)
                gpu["clock_speed"] = base_clock + (gpu["util"] / 100.0) * 150.0 + random.uniform(-10.0, 10.0)
                gpu["status"] = "Healthy"
                
            # NVLink bandwidth activity (communications between neighboring GPUs)
            if not self.paused_training and gpu["util"] > 30.0:
                # Ring connection simulation: GPU i talks to (i+1)%num_gpus and (i-1)%num_gpus
                gpu["nvlink_out"] = (gpu["util"] / 100.0) * 450.0 + random.uniform(-20, 20)
                gpu["nvlink_in"] = (gpu["util"] / 100.0) * 420.0 + random.uniform(-20, 20)
            else:
                gpu["nvlink_out"] = 0.0
                gpu["nvlink_in"] = 0.0
                
            # Health score calculation
            # Decreased by high temperatures, throttling events, extreme VRAM utilization
            health = 100.0
            if gpu["temp"] > TEMP_WARNING_LIMIT:
                health -= (gpu["temp"] - TEMP_WARNING_LIMIT) * 2.5
            if gpu["vram_util"] > 95.0:
                health -= (gpu["vram_util"] - 95.0) * 1.5
            if gpu["throttling"]:
                health -= 10.0
            gpu["health_score"] = min(max(health, 20.0), 100.0)

        # Archive to history
        if tick:
            snapshot = [dict(gpu) for gpu in self.gpus]
            for s in snapshot:
                s["timestamp"] = timestamp
            self.history.append(snapshot)
            if len(self.history) > self.max_history_len:
                self.history.pop(0)

    def get_current_metrics(self) -> List[Dict[str, Any]]:
        self._update_metrics(tick=True)
        return self.gpus

    def get_historical_metrics(self) -> List[List[Dict[str, Any]]]:
        return self.history

    def set_gpu_power_limit(self, gpu_id: int, limit_w: float) -> Dict[str, Any]:
        if 0 <= gpu_id < self.num_gpus:
            self.gpus[gpu_id]["power_limit"] = min(max(limit_w, 150.0), DEFAULT_POWER_LIMIT_W)
            return {"status": "success", "gpu_id": gpu_id, "power_limit": self.gpus[gpu_id]["power_limit"]}
        return {"status": "error", "message": "Invalid GPU ID"}

    def set_power_saving_mode(self, enabled: bool) -> bool:
        self.power_saving_mode = enabled
        return self.power_saving_mode

    def set_paused_training(self, enabled: bool) -> bool:
        self.paused_training = enabled
        return self.paused_training

gpu_simulator = GPUSimulator()
