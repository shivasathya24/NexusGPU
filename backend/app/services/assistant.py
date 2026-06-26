import time
from typing import Dict, List, Any

class AIOpsAssistant:
    def __init__(self):
        # Chat history
        self.chat_history: List[Dict[str, str]] = [
            {"sender": "assistant", "message": "System diagnostics online. I am Nexus AI. I monitor your 8-node H100 cluster for thermal safety, power consumption, and inference efficiency. How can I assist you today?"}
        ]

    def analyze_system_health(self, gpus: List[Dict[str, Any]], power_info: Dict[str, Any], thermal_info: Dict[str, Any], batch_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze current cluster parameters and return tickets/issues and recommended actions.
        """
        alerts = []
        bottlenecks = []
        recommended_actions = []
        
        # 1. Thermal check
        peak_temp = thermal_info.get("peak_temp", 45.0)
        risk = thermal_info.get("risk_score", "LOW")
        if risk in ["MEDIUM", "CRITICAL"]:
            alerts.append({
                "severity": "CRITICAL" if risk == "CRITICAL" else "WARNING",
                "component": "Thermal Center",
                "message": f"Predictive thermal warning: Cluster peak projected to cross threshold ({peak_temp}°C)."
            })
            recommended_actions.append({
                "title": "Mitigate Thermal Loading",
                "action": "Enable Dynamic Voltage Frequency Scaling (DVFS) or cap GPU power draw to 280W.",
                "type": "cap_power"
            })
            
        # 2. VRAM check
        for gpu in gpus:
            if gpu["vram_util"] > 90.0:
                alerts.append({
                    "severity": "WARNING",
                    "component": f"GPU {gpu['id']} VRAM",
                    "message": f"Memory pressure high: GPU {gpu['id']} is at {round(gpu['vram_util'], 1)}% allocation."
                })
                bottlenecks.append(f"VRAM capacity on Node {gpu['id']} is nearly exhausted, potentially causing Out-Of-Memory (OOM) errors.")
                recommended_actions.append({
                    "title": "Rebalance Workloads",
                    "action": f"Migrate 10GB of checkpoint weights from GPU {gpu['id']} to underutilized GPUs in the cluster.",
                    "type": "suspend_nodes"
                })

        # 3. Interconnect Bottlenecks (NVLink)
        avg_nvlink_util = sum([g["nvlink_out"] for g in gpus]) / len(gpus)
        if avg_nvlink_util > 400.0:
            bottlenecks.append("NVLink Ring communication is saturated (utilization > 88%). Ring topology sync is bottlenecking gradient accumulation.")
            recommended_actions.append({
                "title": "Enable FP8 Hybrid Training",
                "action": "Transition training precision to FP8 to halve network sync packet volume.",
                "type": "none"
            })

        # 4. Power Pricing Peak Check
        if power_info.get("is_peak_hour", False):
            alerts.append({
                "severity": "INFO",
                "component": "Smart Power Manager",
                "message": "Peak hours active ($0.28/kWh rate). Low-priority jobs are running at higher utility charges."
            })
            recommended_actions.append({
                "title": "Pause Low-Priority Runs",
                "action": "Pause scheduled SDXL Pre-train background execution to save $24.80/hour.",
                "type": "pause_training"
            })

        # 5. Batching efficiency check
        efficiency = batch_info.get("gpu_efficiency_score", 90.0)
        if efficiency < 70.0:
            bottlenecks.append(f"GPU Tensor Core occupancy is low ({efficiency}%). Batch sizes are too small to saturate H100 execution pipes.")
            recommended_actions.append({
                "title": "Increase Serving Batch Size",
                "action": "Adjust max_batch_size to 64 and max_queue_delay to 15ms in the Inference Batcher settings.",
                "type": "cap_power" # Proxy action trigger
            })

        # Base health calculation
        base_score = 100.0 - (len(alerts) * 8.0) - (len(bottlenecks) * 5.0)
        base_score = min(max(base_score, 10.0), 100.0)
        
        # Add a default recommendation if empty
        if not recommended_actions:
            recommended_actions.append({
                "title": "Optimal Cluster Config",
                "action": "Keep current baseline configs. Schedule next checkpoint backups.",
                "type": "none"
            })

        return {
            "health_score": round(base_score, 1),
            "alerts": alerts,
            "bottlenecks": bottlenecks,
            "recommended_actions": recommended_actions
        }

    def respond_to_chat(self, user_message: str, current_state: Dict[str, Any]) -> str:
        msg_lower = user_message.lower()
        
        # Power management responses
        if "power" in msg_lower or "cost" in msg_lower or "electricity" in msg_lower or "save" in msg_lower:
            is_peak = current_state.get("is_peak", False)
            price = current_state.get("price", 0.12)
            return (
                f"### Nexus Power Optimization Analysis\n"
                f"Currently, the electricity grid price is **${price}/kWh** "
                f"({'Peak Hour Rate' if is_peak else 'Off-Peak Rate'}).\n\n"
                f"**Action Plan to Reduce Costs:**\n"
                f"1. **Enable Power Capping**: Set all H100 GPU limits to **280W**. This reduces thermal accumulation and cluster power draw by **20%** while yielding only a minor **~3-5%** throughput delta.\n"
                f"2. **Reschedule Training**: Pause the active **Stable-Diffusion-XL Pre-train** job during peak hours (2:00 PM - 8:00 PM) to avoid the $0.28/kWh rate. This will reduce operational expenses by approximately **$32.50/hour**."
            )
            
        # Thermal responses
        elif "thermal" in msg_lower or "temperature" in msg_lower or "heat" in msg_lower or "hot" in msg_lower:
            peak_temp = current_state.get("peak_temp", 45.0)
            return (
                f"### Thermal Prediction & Throttling Mitigation\n"
                f"The cluster peak temperature is currently trending at **{peak_temp}°C**.\n\n"
                f"**Diagnostics & Recommendations:**\n"
                f"- **VRAM Congestion**: Hot spots are localized to nodes 0 and 1 due to high pipeline parallelism.\n"
                f"- **Fan Speed Curve**: System fans are automatically running at **{current_state.get('avg_fan', 40)}%** capacity. "
                f"I recommend increasing the minimum fan speed floor to **60%** if the temperature exceeds 75°C to buffer sudden workload spikes."
            )
            
        # Inference/batching responses
        elif "batch" in msg_lower or "inference" in msg_lower or "throughput" in msg_lower or "latency" in msg_lower:
            tps = current_state.get("throughput", 8000)
            lat = current_state.get("latency", 20)
            eff = current_state.get("efficiency", 85)
            return (
                f"### Inference Batching Center Report\n"
                f"- **Throughput**: {tps} tokens/sec\n"
                f"- **Avg Latency**: {lat} ms\n"
                f"- **Tensor Occupancy**: {eff}%\n\n"
                f"**Optimization Insights:**\n"
                f"To boost token throughput: increase `max_batch_size` to **64**. This raises Tensor Core utilization to **94%** and increases GPU bandwidth utilization, though average request latency will rise to **31ms**. \n"
                f"If you require low latency, reduce `max_batch_size` to **16** and set `max_queue_delay` to **4ms** to achieve a Time-to-First-Token (TTFT) of **5.8ms**."
            )
            
        # Default responses
        else:
            return (
                f"I have processed your query: *\"{user_message}\"*\n\n"
                f"Here is a summary of the cluster health status:\n"
                f"- **GPU Status**: 8/8 Nodes online and running.\n"
                f"- **Average Workload**: {current_state.get('avg_util', 0.0)}% GPU Utilization.\n"
                f"- **Active Alerts**: {current_state.get('alert_count', 0)} active events.\n\n"
                f"Please let me know if you would like me to optimize power limits, pause background jobs, or generate an analytics PDF report."
            )

aiops_assistant = AIOpsAssistant()
