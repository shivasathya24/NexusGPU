import streamlit as st
import requests
import os
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
def get_backend_url():
    keys = ["BACKEND_URL", "backend_url", "BackendUrl", "Backend_URL"]
    url = None
    for key in keys:
        try:
            if key in st.secrets:
                url = st.secrets[key]
                break
        except Exception:
            pass
    if not url:
        for key in keys:
            val = os.getenv(key)
            if val:
                url = val
                break
    if not url:
        url = "http://127.0.0.1:8000"
    url = url.strip().rstrip("/")
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "http://" + url if "127.0.0.1" in url or "localhost" in url else "https://" + url
    return url

BACKEND_URL = get_backend_url()

# Custom functions to render Plotly charts with styling
def make_gauge_chart(value, title, unit, color, max_val):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = value,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': title, 'font': {'size': 14, 'color': '#94A3B8', 'family': 'Outfit'}},
        number = {'suffix': unit, 'font': {'size': 24, 'color': '#FFFFFF', 'family': 'Outfit'}},
        gauge = {
            'axis': {'range': [None, max_val], 'tickwidth': 1, 'tickcolor': "#475569"},
            'bar': {'color': color},
            'bgcolor': "rgba(30, 41, 59, 0.3)",
            'borderwidth': 1,
            'bordercolor': "rgba(255, 255, 255, 0.15)",
            'steps': [
                {'range': [0, max_val * 0.7], 'color': 'rgba(255,255,255,0.01)'},
                {'range': [max_val * 0.7, max_val * 0.9], 'color': 'rgba(245, 158, 11, 0.1)'},
                {'range': [max_val * 0.9, max_val], 'color': 'rgba(239, 68, 68, 0.15)'}
            ]
        }
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=10, r=10, t=30, b=10),
        height=150
    )
    return fig

def render_dashboard(api_online):
    # Fallback simulation if API is down
    if not api_online:
        st.warning("⚠️ FastAPI Backend is offline. Displaying simulation preview with client-side mocked data.")
        # Setup mock data structure
        gpus = []
        for i in range(8):
            gpus.append({
                "id": i, "name": f"GPU {i}: NVIDIA H100 80GB", "temp": 55.0 + i * 2, "util": 60.0 + (i % 3) * 10,
                "vram_util": 45.0 + i * 4, "power_draw": 220.0 + i * 15, "power_limit": 350.0,
                "fan_speed": 45.0, "clock_speed": 1600.0, "health_score": 98.0, "throttling": False,
                "status": "Healthy", "nvlink_in": 120.0, "nvlink_out": 125.0
            })
        health = {
            "health_score": 92.5,
            "alerts": [{"severity": "WARNING", "component": "Thermal Center", "message": "GPU 7 temp warning"}],
            "bottlenecks": ["NVLink communication is rising (utilization > 60%)"],
            "recommended_actions": [{"title": "Activate Power Caps", "action": "Limit GPUs to 280W", "type": "cap_power"}]
        }
        thermal = {
            "risk_score": "LOW", "risk_value": 32.0, "peak_temp": 68.0, "throttling_predicted": False,
            "forecast": [{"minute": m, "temperature": 68.0 + m * 0.4, "predicted_fan": 50.0} for m in range(1, 16)],
            "warnings": [{"title": "Thermal System Nominal", "message": "Stable under load.", "severity": "Low"}]
        }
        power = {
            "price_info": {"price_per_kwh": 0.12, "is_peak_hour": False},
            "savings_info": {"cumulative_energy_kwh": 412.0, "cumulative_cost_usd": 49.44, "saved_energy_kwh": 50.0, "saved_cost_usd": 6.00, "co2_saved_kg": 20.0},
            "recommendations": [{"title": "Cap GPU Power limits", "recommendation": "Cap limits to 280W during spikes.", "potential_saving": "$10/day"}],
            "active_jobs": [{"name": "LLama-3 Fine-Tune", "status": "Running", "priority": "High"}],
            "total_power_w": 1820.0, "paused_training": False
        }
        batching = {
            "queue_depth": 14, "throughput_tokens_sec": 8450.0, "avg_latency_ms": 21.4, "ttft_ms": 7.8,
            "gpu_efficiency_score": 89.0, "active_queue": [{"id": f"req_{k}", "prompt_tokens": 256} for k in range(5)],
            "completed_batches": [{"id": f"b_{k}", "size": 16, "throughput_tps": 8200.0, "latency_ms": 20.0, "efficiency": 88.0} for k in range(5)]
        }
        history = [[dict(g, timestamp=time.time() - (60 - tick) * 5) for g in gpus] for tick in range(60)]
    else:
        # Load from API
        try:
            telemetry_res = requests.get(f"{BACKEND_URL}/api/telemetry").json()
            gpus = telemetry_res["gpus"]
            history = telemetry_res["history"]
            
            health = requests.get(f"{BACKEND_URL}/api/health").json()
            thermal = requests.get(f"{BACKEND_URL}/api/thermal").json()
            power = requests.get(f"{BACKEND_URL}/api/power").json()
            batching = requests.get(f"{BACKEND_URL}/api/batching").json()
        except Exception as ex:
            st.error(f"Error querying API endpoints: {str(ex)}")
            return

    # Top Command Center Summary Bar
    st.markdown(
        f"""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px; padding-bottom: 10px; border-bottom: 1px solid rgba(255,255,255,0.05);">
            <div>
                <h2 style="margin: 0; color: #FFF; font-family: Outfit;">Cluster Control Center</h2>
                <span style="color: #64748B; font-size: 13px;">Real-time diagnostics and orchestration of 8x H100 cluster.</span>
            </div>
            <div style="display: flex; gap: 15px; align-items: center;">
                <div class="glass-card" style="padding: 8px 16px !important; display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 11px; color: #94A3B8; font-weight: 600; text-transform: uppercase;">Health Score</span>
                    <span style="font-size: 18px; color: {'#10B981' if health['health_score'] >= 85 else '#F59E0B' if health['health_score'] >= 70 else '#EF4444'}; font-weight: 800; font-family: Outfit;">
                        {health['health_score']}%
                    </span>
                </div>
                <div class="glass-card" style="padding: 8px 16px !important; display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 11px; color: #94A3B8; font-weight: 600; text-transform: uppercase;">Grid Price</span>
                    <span style="font-size: 18px; color: {'#EF4444' if power['price_info']['is_peak_hour'] else '#76B900'}; font-weight: 800; font-family: Outfit;">
                        ${power['price_info']['price_per_kwh']}/kWh
                    </span>
                </div>
                <div class="glass-card" style="padding: 8px 16px !important; display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 11px; color: #94A3B8; font-weight: 600; text-transform: uppercase;">Aggregate Load</span>
                    <span style="font-size: 18px; color: #FFF; font-weight: 800; font-family: Outfit;">
                        {round(sum([g['util'] for g in gpus]) / len(gpus), 1)}%
                    </span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ------------------ LEFT COLUMN: TELEMETRY AND TOPOLOGY ------------------
    # ------------------ RIGHT COLUMN: INTELLIGENCE & CONTROL CENTERS --------
    col_left, col_right = st.columns([1.6, 1.4])
    
    with col_left:
        # 1. GPU Monitoring Panel
        st.markdown("<h3 style='color: #00E5FF; font-family: Outfit; font-size: 1.25rem;'>📊 Live GPU Telemetry</h3>", unsafe_allow_html=True)
        
        # GPU Selector Tabs
        gpu_names = ["Cluster Summary"] + [f"GPU {g['id']}" for g in gpus]
        selected_tab = st.selectbox("Select GPU Node for Detail View:", gpu_names)
        
        if selected_tab == "Cluster Summary":
            # Grid of all 8 GPUs metrics
            grid_cols = st.columns(4)
            for idx, g in enumerate(gpus):
                with grid_cols[idx % 4]:
                    status_class = "status-healthy" if g["status"] == "Healthy" else "status-warning" if g["status"] == "Warning" else "status-critical"
                    st.markdown(
                        f"""
                        <div class="glass-card" style="padding: 12px !important; margin-bottom: 12px;">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                                <b style="font-size: 13px; color: #FFF; font-family: Outfit;">Node {g['id']}</b>
                                <span class="status-pill {status_class}" style="padding: 1px 6px !important; font-size: 8px !important;">
                                    <span class="status-pulse"></span>{g['status']}
                                </span>
                            </div>
                            <div style="font-size: 11px; color: #94A3B8; margin-bottom: 4px;">Temp: <b style="color: #FFF;">{round(g['temp'], 1)}°C</b></div>
                            <div style="font-size: 11px; color: #94A3B8; margin-bottom: 4px;">Util: <b style="color: #FFF;">{round(g['util'], 1)}%</b></div>
                            <div style="font-size: 11px; color: #94A3B8; margin-bottom: 4px;">VRAM: <b style="color: #FFF;">{round(g['vram_util'], 1)}%</b></div>
                            <div style="font-size: 11px; color: #94A3B8;">Power: <b style="color: #FFF;">{round(g['power_draw'], 1)}W</b></div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    
            # Cluster Average charts
            df_history_list = []
            for tick in history:
                timestamp = tick[0]["timestamp"]
                # average metrics
                avg_t = sum([g["temp"] for g in tick]) / len(tick)
                avg_u = sum([g["util"] for g in tick]) / len(tick)
                avg_v = sum([g["vram_util"] for g in tick]) / len(tick)
                tot_p = sum([g["power_draw"] for g in tick])
                df_history_list.append({
                    "Time": pd.to_datetime(timestamp, unit='s'),
                    "Temperature (°C)": avg_t,
                    "Utilization (%)": avg_u,
                    "VRAM Allocation (%)": avg_v,
                    "Total Power (W)": tot_p
                })
            df_history = pd.DataFrame(df_history_list)
            
            # Draw line plot
            fig_lines = make_subplots(rows=2, cols=2, shared_xaxes=True, 
                                       subplot_titles=("Avg Temperature", "Avg Utilization", "Avg VRAM Allocation", "Total Cluster Power"))
            fig_lines.add_trace(go.Scatter(x=df_history["Time"], y=df_history["Temperature (°C)"], name="Temp", line=dict(color="#00E5FF", width=2)), row=1, col=1)
            fig_lines.add_trace(go.Scatter(x=df_history["Time"], y=df_history["Utilization (%)"], name="Util", line=dict(color="#60A5FA", width=2)), row=1, col=2)
            fig_lines.add_trace(go.Scatter(x=df_history["Time"], y=df_history["VRAM Allocation (%)"], name="VRAM", line=dict(color="#A855F7", width=2)), row=2, col=1)
            fig_lines.add_trace(go.Scatter(x=df_history["Time"], y=df_history["Total Power (W)"], name="Power", line=dict(color="#EF4444", width=2)), row=2, col=2)
            
            fig_lines.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#94A3B8', size=10),
                margin=dict(l=20, r=20, t=30, b=20),
                height=320,
                showlegend=False
            )
            fig_lines.update_xaxes(showgrid=True, gridcolor='rgba(255,255,255,0.03)')
            fig_lines.update_yaxes(showgrid=True, gridcolor='rgba(255,255,255,0.03)')
            st.plotly_chart(fig_lines, use_container_width=True)
            
        else:
            # Single GPU view
            gpu_id = int(selected_tab.split(" ")[1])
            gpu_data = gpus[gpu_id]
            
            g_col1, g_col2, g_col3, g_col4 = st.columns(4)
            with g_col1:
                st.plotly_chart(make_gauge_chart(gpu_data["temp"], "Temperature", "°C", "#00E5FF", 100.0), use_container_width=True)
            with g_col2:
                st.plotly_chart(make_gauge_chart(gpu_data["util"], "Utilization", "%", "#60A5FA", 100.0), use_container_width=True)
            with g_col3:
                st.plotly_chart(make_gauge_chart(gpu_data["vram_util"], "VRAM", "%", "#A855F7", 100.0), use_container_width=True)
            with g_col4:
                st.plotly_chart(make_gauge_chart(gpu_data["power_draw"], "Power Draw", "W", "#EF4444", 400.0), use_container_width=True)
                
            # Single GPU historical data
            df_history_list = []
            for tick in history:
                g_tick = tick[gpu_id]
                df_history_list.append({
                    "Time": pd.to_datetime(g_tick["timestamp"], unit='s'),
                    "Temperature": g_tick["temp"],
                    "Utilization": g_tick["util"],
                    "VRAM": g_tick["vram_util"],
                    "Power": g_tick["power_draw"]
                })
            df_history = pd.DataFrame(df_history_list)
            
            fig_line = go.Figure()
            fig_line.add_trace(go.Scatter(x=df_history["Time"], y=df_history["Temperature"], name="Temp (°C)", line=dict(color="#00E5FF", width=2)))
            fig_line.add_trace(go.Scatter(x=df_history["Time"], y=df_history["Utilization"], name="Util (%)", line=dict(color="#60A5FA", width=2)))
            fig_line.add_trace(go.Scatter(x=df_history["Time"], y=df_history["VRAM"], name="VRAM (%)", line=dict(color="#A855F7", width=2)))
            fig_line.add_trace(go.Scatter(x=df_history["Time"], y=df_history["Power"], name="Power (W)", line=dict(color="#EF4444", width=2), yaxis="y2"))
            
            fig_line.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#94A3B8', size=11),
                margin=dict(l=10, r=10, t=30, b=10),
                height=250,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                yaxis=dict(title="Temp / Util / VRAM", showgrid=True, gridcolor='rgba(255,255,255,0.03)'),
                yaxis2=dict(title="Power (W)", overlaying="y", side="right", showgrid=False)
            )
            st.plotly_chart(fig_line, use_container_width=True)
            
            # Manual limit adjustment
            st.markdown("<div style='font-size:12px; color:#94A3B8; margin-top:-5px; margin-bottom: 5px;'>Adjust Power Cap:</div>", unsafe_allow_html=True)
            p_cap = st.slider("Power Limit (Watts)", 150.0, 350.0, float(gpu_data["power_limit"]), step=10.0, key=f"sld_{gpu_id}")
            if p_cap != gpu_data["power_limit"] and api_online:
                try:
                    requests.post(f"{BACKEND_URL}/api/power/limit", json={"gpu_id": gpu_id, "limit_w": p_cap})
                    st.toast(f"Updated Node {gpu_id} power limit to {p_cap}W!", icon="⚡")
                    st.rerun()
                except Exception:
                    pass

        # 2. Interconnect NVLink Topology Visualization
        st.markdown("<br><h3 style='color: #00D2FF; font-family: Outfit; font-size: 1.25rem;'>🔗 Dynamic NVLink Topology</h3>", unsafe_allow_html=True)
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            svg_path = os.path.join(base_dir, "assets", "nvlink_topology.svg")
            with open(svg_path, "r", encoding="utf-8") as f:
                svg_content = f.read()
            
            import base64
            b64_svg = base64.b64encode(svg_content.encode("utf-8")).decode("utf-8")
            svg_data_uri = f"data:image/svg+xml;base64,{b64_svg}"
            
            # Single self-contained markdown call to avoid split tag issues
            st.markdown(
                f"""
                <style>
                .nvlink-wrapper {{
                    background: radial-gradient(circle at 50% 50%, rgba(15, 23, 42, 0.8) 0%, rgba(8, 11, 16, 0.95) 100%);
                    border: 1px solid rgba(255, 255, 255, 0.05);
                    border-radius: 12px;
                    padding: 15px;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                }}
                </style>
                <div class="nvlink-wrapper">
                    <img src="{svg_data_uri}" style="width: 100%; height: auto;" />
                </div>
                """,
                unsafe_allow_html=True
            )
        except Exception as ex:
            st.error(f"Error loading topology asset: {str(ex)}")
            
        st.markdown(
            """
            <div style="font-size: 11px; color: #64748B; text-align: center; margin-top: 5px; font-family: sans-serif;">
                NVLink Ring (glowing green lines, max 900 GB/s per link) sync status nominal. G5 showing warning thermal threshold.
            </div>
            """,
            unsafe_allow_html=True
        )

    with col_right:
        # 3. Thermal Intelligence Center
        st.markdown("<h3 style='color: #EF4444; font-family: Outfit; font-size: 1.25rem;'>🔥 Thermal Intelligence Center</h3>", unsafe_allow_html=True)
        
        # Risk gauge & Alert banner
        risk_color = "#10B981" if thermal["risk_score"] == "LOW" else "#F59E0B" if thermal["risk_score"] == "MEDIUM" else "#EF4444"
        st.markdown(
            f"""
            <div class="glass-card border-critical" style="margin-bottom: 15px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span style="font-size: 11px; font-weight: 600; color: #94A3B8; text-transform: uppercase;">ML Throttling Risk</span>
                    <span style="font-size: 13px; font-weight: 800; color: {risk_color};">{thermal['risk_score']} RISK ({thermal['risk_value']}%)</span>
                </div>
                <div style="width: 100%; bg-color: rgba(255,255,255,0.05); height: 8px; border-radius: 4px; overflow: hidden; background: #1E293B;">
                    <div style="width: {thermal['risk_value']}%; height: 100%; background: {risk_color};"></div>
                </div>
                <div style="font-size: 12px; color: #E2E8F0; margin-top: 10px;">
                    <b>Prediction Warning:</b> {thermal['warnings'][0]['message']}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Historical & Forecast graph
        forecast_df = pd.DataFrame(thermal["forecast"])
        # Generate some mock historical nodes for plotting
        hist_temps = [g["temp"] for g in gpus]
        avg_hist = sum(hist_temps) / len(hist_temps)
        time_hist = [f"-{15 - k}m" for k in range(15)]
        temp_hist = [avg_hist + np.random.normal(0, 0.5) for _ in range(15)]
        
        time_fore = [f"+{f['minute']}m" for f in thermal["forecast"]]
        temp_fore = [f["temperature"] for f in thermal["forecast"]]
        
        fig_forecast = go.Figure()
        fig_forecast.add_trace(go.Scatter(x=time_hist, y=temp_hist, name="Historical", line=dict(color="#64748B", width=2)))
        fig_forecast.add_trace(go.Scatter(x=time_fore, y=temp_fore, name="ML Projected", line=dict(color="#EF4444", width=2.5, dash="dash")))
        fig_forecast.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#94A3B8', size=10),
            margin=dict(l=10, r=10, t=10, b=10),
            height=130,
            showlegend=False,
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.03)'),
            xaxis=dict(showgrid=False)
        )
        st.plotly_chart(fig_forecast, use_container_width=True)

        # 4. Smart Power Manager
        st.markdown("<h3 style='color: #F59E0B; font-family: Outfit; font-size: 1.25rem;'>⚡ Smart Power Optimizer</h3>", unsafe_allow_html=True)
        
        pow1, pow2 = st.columns(2)
        with pow1:
            st.markdown(
                f"""
                <div class="glass-card" style="padding: 12px !important; margin-bottom: 10px;">
                    <div style="font-size: 10px; color: #94A3B8;">ACCUMULATED ENERGY SAVED</div>
                    <div style="font-size: 18px; font-weight: 800; color: #00E5FF; margin-top: 5px;">{power['savings_info']['saved_energy_kwh']} kWh</div>
                    <div style="font-size: 10px; color: #64748B; margin-top: 2px;">CO₂ Offset: {power['savings_info']['co2_saved_kg']} kg</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with pow2:
            st.markdown(
                f"""
                <div class="glass-card" style="padding: 12px !important; margin-bottom: 10px;">
                    <div style="font-size: 10px; color: #94A3B8;">OPERATIONAL BUDGET SAVINGS</div>
                    <div style="font-size: 18px; font-weight: 800; color: #00E5FF; margin-top: 5px;">${power['savings_info']['saved_cost_usd']} USD</div>
                    <div style="font-size: 10px; color: #64748B; margin-top: 2px;">Rate: ${power['price_info']['price_per_kwh']}/kWh</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
        # Recommendations and pause/resume button
        st.markdown(f"<div style='font-size: 11px; color:#E2E8F0; margin-bottom: 5px;'><b>Power Cap Policy Recommendation:</b> {power['recommendations'][0]['title']}</div>", unsafe_allow_html=True)
        
        btn_label = "Resume Training Jobs" if power["paused_training"] else "Pause Low-Priority Training"
        btn_type = "secondary" if power["paused_training"] else "primary"
        
        if st.button(btn_label, use_container_width=True, key="pwr_action"):
            if api_online:
                action = "resume_training" if power["paused_training"] else "pause_training"
                try:
                    requests.post(f"{BACKEND_URL}/api/power/action", json={"action_type": action})
                    st.toast("Updated active job schedule on cluster!", icon="⚡")
                    st.rerun()
                except Exception:
                    pass

        # 5. AI Inference Batching Center
        st.markdown("<br><h3 style='color: #A855F7; font-family: Outfit; font-size: 1.25rem;'>📦 AI Inference Batching Center</h3>", unsafe_allow_html=True)
        
        b_col1, b_col2, b_col3 = st.columns(3)
        with b_col1:
            st.markdown(
                f"""
                <div style="text-align: center;">
                    <div style="font-size: 9px; color:#94A3B8; text-transform: uppercase;">Throughput</div>
                    <div style="font-size: 14px; font-weight: 800; color: #FFF;">{batching['throughput_tokens_sec']} t/s</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with b_col2:
            st.markdown(
                f"""
                <div style="text-align: center;">
                    <div style="font-size: 9px; color:#94A3B8; text-transform: uppercase;">Avg Latency</div>
                    <div style="font-size: 14px; font-weight: 800; color: #FFF;">{batching['avg_latency_ms']} ms</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with b_col3:
            st.markdown(
                f"""
                <div style="text-align: center;">
                    <div style="font-size: 9px; color:#94A3B8; text-transform: uppercase;">GPU Efficiency</div>
                    <div style="font-size: 14px; font-weight: 800; color: #00E5FF;">{batching['gpu_efficiency_score']}%</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
        # Queue visualization HTML/CSS
        active_queue_count = batching["queue_depth"]
        queue_boxes = "".join([f"<span class='request-node' style='padding: 2px 6px; margin-right: 4px; display: inline-block;'>req_{str(i)}</span>" for i in range(min(active_queue_count, 6))])
        if active_queue_count > 6:
            queue_boxes += f"<span style='font-size:10px; color:#64748B;'>+{active_queue_count-6} more</span>"
            
        st.markdown(
            f"""
            <div class="glass-card" style="padding: 12px !important; margin-top: 10px; margin-bottom: 10px;">
                <div style="font-size: 10px; color:#94A3B8; margin-bottom: 6px;">DYNAMIC INFERENCE REQUEST QUEUE</div>
                <div style="overflow-x: auto; white-space: nowrap; padding: 4px; background: rgba(0,0,0,0.2); border-radius: 4px; margin-bottom: 8px;">
                    {queue_boxes if active_queue_count > 0 else "<span style='font-size:10px; color:#64748B;'>Queue Empty</span>"}
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 10px; color: #94A3B8;">Serving Engine configuration:</span>
                    <span style="font-size: 10px; color: #A855F7; font-weight: bold;">Triton / vLLM Simulator</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Batching sliders
        bs_col1, bs_col2 = st.columns(2)
        with bs_col1:
            max_bs = st.slider("Max Batch Size", 8, 128, 32, step=8, key="sld_bs")
        with bs_col2:
            delay_ms = st.slider("Max Delay (ms)", 2.0, 50.0, 10.0, step=2.0, key="sld_delay")
            
        if (max_bs != 32 or delay_ms != 10.0) and api_online:
            try:
                requests.post(f"{BACKEND_URL}/api/batching/configure", json={
                    "max_batch_size": max_bs,
                    "delay_ms": delay_ms,
                    "arrival_rate": 240.0
                })
            except Exception:
                pass

        # 6. System Health Command Center Alerts
        st.markdown("<br><h3 style='color: #00E5FF; font-family: Outfit; font-size: 1.25rem;'>🚨 Diagnostics Command Center</h3>", unsafe_allow_html=True)
        
        # Bottleneck warning
        for b in health["bottlenecks"][:2]:
            st.markdown(
                f"""
                <div class="ai-assistant-bubble" style="margin-bottom: 8px;">
                    ⚠️ <b>Bottleneck Alert:</b> {b}
                </div>
                """,
                unsafe_allow_html=True
            )
            
        # Action button
        for action in health["recommended_actions"][:1]:
            if st.button(f"⚡ Auto-Mitigate: {action['title']}", key=f"btn_act_{action['type']}", use_container_width=True):
                if api_online:
                    try:
                        requests.post(f"{BACKEND_URL}/api/power/action", json={"action_type": action["type"]})
                        st.toast(f"Dispatched mitigation action: {action['title']}!", icon="✅")
                        st.rerun()
                    except Exception:
                        pass
