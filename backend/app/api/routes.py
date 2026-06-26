from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Any

# Import simulator objects
from app.services.telemetry import gpu_simulator
from app.services.thermal_ml import thermal_predictor
from app.services.power import power_manager
from app.services.batching import inference_batcher
from app.services.assistant import aiops_assistant

router = APIRouter()

# --- Telemetry Endpoints ---
@router.get("/telemetry")
def get_telemetry():
    gpus = gpu_simulator.get_current_metrics()
    history = gpu_simulator.get_historical_metrics()
    return {"gpus": gpus, "history": history}

@router.post("/telemetry/power-saving")
def set_power_saving(payload: Dict[str, bool]):
    enabled = payload.get("enabled", False)
    val = gpu_simulator.set_power_saving_mode(enabled)
    # Mirror state into power manager paused_training flag
    if enabled:
        power_manager.paused_training = True
    else:
        power_manager.paused_training = False
    return {"power_saving_mode": val}

# --- Thermal Endpoints ---
@router.get("/thermal")
def get_thermal():
    gpus = gpu_simulator.get_current_metrics()
    # Run prediction for the hottest GPU in the cluster
    hottest_gpu = max(gpus, key=lambda g: g["temp"])
    
    prediction = thermal_predictor.predict_temperature_forecast(
        current_temp=hottest_gpu["temp"],
        util=hottest_gpu["util"],
        power_draw=hottest_gpu["power_draw"],
        fan_speed=hottest_gpu["fan_speed"]
    )
    return {
        "hottest_gpu_id": hottest_gpu["id"],
        "hottest_gpu_temp": hottest_gpu["temp"],
        **prediction
    }

# --- Power Endpoints ---
@router.get("/power")
def get_power():
    gpus = gpu_simulator.get_current_metrics()
    total_power = sum([g["power_draw"] for g in gpus])
    avg_util = sum([g["util"] for g in gpus]) / len(gpus)
    
    price_info = power_manager.get_current_electricity_price()
    savings_info = power_manager.update_energy_metrics(
        current_cluster_power_w=total_power,
        power_saving_mode=gpu_simulator.power_saving_mode
    )
    recs = power_manager.get_power_recommendations(
        is_peak=price_info["is_peak_hour"],
        cluster_util=avg_util
    )
    
    return {
        "price_info": price_info,
        "savings_info": savings_info,
        "recommendations": recs,
        "active_jobs": power_manager.active_jobs,
        "total_power_w": round(total_power, 1),
        "paused_training": gpu_simulator.paused_training
    }

class PowerLimitPayload(BaseModel):
    gpu_id: int
    limit_w: float

@router.post("/power/limit")
def set_power_limit(payload: PowerLimitPayload):
    res = gpu_simulator.set_gpu_power_limit(payload.gpu_id, payload.limit_w)
    if res["status"] == "error":
        raise HTTPException(status_code=400, detail=res["message"])
    return res

class ActionPayload(BaseModel):
    action_type: str

@router.post("/power/action")
def trigger_power_action(payload: ActionPayload):
    # Trigger side effects in telemetry
    if payload.action_type == "pause_training":
        gpu_simulator.set_paused_training(True)
    elif payload.action_type == "resume_training":
        gpu_simulator.set_paused_training(False)
        
    res = power_manager.trigger_action(payload.action_type)
    if res["status"] == "error":
        raise HTTPException(status_code=400, detail=res["message"])
    return res

# --- Inference Batcher Endpoints ---
@router.get("/batching")
def get_batching():
    return inference_batcher.update_simulation()

class BatcherConfigPayload(BaseModel):
    max_batch_size: int
    delay_ms: float
    arrival_rate: float

@router.post("/batching/configure")
def configure_batching(payload: BatcherConfigPayload):
    return inference_batcher.configure_batcher(
        max_batch_size=payload.max_batch_size,
        delay_ms=payload.delay_ms,
        arrival_rate=payload.arrival_rate
    )

# --- Health Command Center Endpoints ---
@router.get("/health")
def get_health():
    gpus = gpu_simulator.get_current_metrics()
    total_power = sum([g["power_draw"] for g in gpus])
    avg_util = sum([g["util"] for g in gpus]) / len(gpus)
    
    price_info = power_manager.get_current_electricity_price()
    
    hottest_gpu = max(gpus, key=lambda g: g["temp"])
    thermal_info = thermal_predictor.predict_temperature_forecast(
        current_temp=hottest_gpu["temp"],
        util=hottest_gpu["util"],
        power_draw=hottest_gpu["power_draw"],
        fan_speed=hottest_gpu["fan_speed"]
    )
    
    batch_info = inference_batcher.update_simulation()
    
    diagnostics = aiops_assistant.analyze_system_health(
        gpus=gpus,
        power_info=price_info,
        thermal_info=thermal_info,
        batch_info=batch_info
    )
    
    return diagnostics

# --- AI Chat Assistant Endpoints ---
class ChatPayload(BaseModel):
    message: str
    current_state: Dict[str, Any]

@router.post("/assistant/chat")
def chat_with_assistant(payload: ChatPayload):
    response = aiops_assistant.respond_to_chat(payload.message, payload.current_state)
    # Save to history
    aiops_assistant.chat_history.append({"sender": "user", "message": payload.message})
    aiops_assistant.chat_history.append({"sender": "assistant", "message": response})
    return {"response": response, "chat_history": aiops_assistant.chat_history}

@router.get("/assistant/history")
def get_chat_history():
    return {"chat_history": aiops_assistant.chat_history}
