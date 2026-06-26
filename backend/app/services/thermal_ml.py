import numpy as np
import time
from typing import Dict, List, Any
from sklearn.linear_model import LinearRegression
from app.config import TEMP_WARNING_LIMIT, TEMP_CRITICAL_LIMIT

class ThermalPredictor:
    def __init__(self):
        # We will train a simple LinearRegression model on startup.
        # It maps features [utilization, power_draw, fan_speed] -> temperature_change.
        self.model = LinearRegression()
        self._train_initial_model()

    def _train_initial_model(self):
        # Generate some representative physical physics data:
        # High utilization + high power = temperature rises.
        # High fan speed = temperature drops.
        X = []
        y = []
        
        # Simulating 1000 time steps of state changes
        for _ in range(1000):
            util = np.random.uniform(0.0, 100.0)
            pwr = 60.0 + (util / 100.0) * 290.0 # Power draw between 60W and 350W
            fan = 30.0 + (util / 100.0) * 70.0 + np.random.uniform(-10.0, 10.0)
            fan = min(max(fan, 20.0), 100.0)
            
            # Theoretical temperature change:
            # Heat generation depends on power draw.
            # Heat dissipation depends on fan speed.
            heat_gen = pwr * 0.002
            heat_diss = fan * 0.005
            temp_change = heat_gen - heat_diss + np.random.normal(0.0, 0.05)
            
            X.append([util, pwr, fan])
            y.append(temp_change)
            
        self.model.fit(np.array(X), np.array(y))

    def predict_temperature_forecast(self, current_temp: float, util: float, power_draw: float, fan_speed: float, steps_minutes: int = 15) -> Dict[str, Any]:
        """
        Predicts temperature for the next N minutes.
        Assumes utilization remains stable or drifts slightly, and fan speed responds reactively.
        """
        forecast = []
        temp = current_temp
        current_util = util
        current_pwr = power_draw
        current_fan = fan_speed
        
        throttling_predicted = False
        risk_score = "LOW"
        risk_value = 0.0  # 0 to 100 scale

        for m in range(1, steps_minutes + 1):
            # Assume utility drifts slightly (50% probability of going up or down)
            current_util = min(max(current_util + np.random.normal(0.0, 2.0), 0.0), 100.0)
            current_pwr = min(max(60.0 + (current_util / 100.0) * 290.0, 55.0), 350.0)
            
            # Model predicts temperature change per minute
            features = np.array([[current_util, current_pwr, current_fan]])
            temp_change = self.model.predict(features)[0]
            
            temp = min(max(temp + temp_change, 35.0), 105.0)
            
            # Simple fan controller update inside projection loop
            if temp < 50.0:
                target_fan = 30.0
            elif temp < 70.0:
                target_fan = 30.0 + (temp - 50.0) * 2.0
            else:
                target_fan = 70.0 + (temp - 70.0) * 2.5
            current_fan = min(max(current_fan * 0.8 + target_fan * 0.2, 20.0), 100.0)
            
            forecast.append({
                "minute": m,
                "temperature": round(temp, 2),
                "predicted_fan": round(current_fan, 1)
            })
            
            if temp >= TEMP_CRITICAL_LIMIT:
                throttling_predicted = True

        # Determine risk based on peak temperature in the forecast
        peak_temp = max([f["temperature"] for f in forecast])
        if peak_temp >= TEMP_CRITICAL_LIMIT:
            risk_score = "CRITICAL"
            risk_value = min(90.0 + (peak_temp - TEMP_CRITICAL_LIMIT) * 2.0, 100.0)
        elif peak_temp >= TEMP_WARNING_LIMIT:
            risk_score = "MEDIUM"
            risk_value = 60.0 + ((peak_temp - TEMP_WARNING_LIMIT) / (TEMP_CRITICAL_LIMIT - TEMP_WARNING_LIMIT)) * 30.0
        else:
            risk_score = "LOW"
            # Scale 0 to 60 based on peak_temp up to TEMP_WARNING_LIMIT
            risk_value = max((peak_temp / TEMP_WARNING_LIMIT) * 60.0, 10.0)

        # Generate warnings
        warning_cards = []
        if risk_score == "CRITICAL":
            warning_cards.append({
                "title": "Thermal Throttling Imminent",
                "message": f"Peak temperature forecast reaches {round(peak_temp, 1)}°C, exceeding safety limit of {TEMP_CRITICAL_LIMIT}°C. Performance throttling will occur in the next 10 minutes.",
                "severity": "High",
                "action": "Trigger workload migration or active power cap."
            })
        elif risk_score == "MEDIUM":
            warning_cards.append({
                "title": "High Heat Index Detected",
                "message": f"GPU temperature is trending towards {round(peak_temp, 1)}°C. Fans operating above 80% to compensate.",
                "severity": "Medium",
                "action": "Enable smart energy limit to reduce thermal buildup."
            })
        else:
            warning_cards.append({
                "title": "Thermal System Nominal",
                "message": f"GPU temperature forecast stable under load. All systems operating within standard safety limits.",
                "severity": "Low",
                "action": "No action required."
            })

        return {
            "forecast": forecast,
            "peak_temp": round(peak_temp, 2),
            "throttling_predicted": throttling_predicted,
            "risk_score": risk_score,
            "risk_value": round(risk_value, 1),
            "warnings": warning_cards
        }

thermal_predictor = ThermalPredictor()
