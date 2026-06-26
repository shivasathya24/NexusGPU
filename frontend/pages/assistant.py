import streamlit as st
import requests
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

def render_assistant(api_online):
    st.markdown(
        """
        <div style="margin-bottom: 25px; padding-bottom: 10px; border-bottom: 1px solid rgba(255,255,255,0.05);">
            <h2 style="margin: 0; color: #FFF; font-family: Outfit;">Nexus AI Assistant</h2>
            <span style="color: #64748B; font-size: 13px;">Ask questions regarding H100 cluster performance, energy optimizations, and dynamic serving configurations.</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Fetch chat history on startup
    chat_history = []
    current_state = {
        "avg_temp": 54.2,
        "avg_util": 68.0,
        "price": 0.12,
        "is_peak": False,
        "throughput": 8200.0,
        "latency": 22.0,
        "efficiency": 88.0,
        "alert_count": 0
    }
    
    if api_online:
        try:
            # Query status to build contextual payload for chat
            telemetry = requests.get(f"{BACKEND_URL}/api/telemetry").json()
            power = requests.get(f"{BACKEND_URL}/api/power").json()
            batching = requests.get(f"{BACKEND_URL}/api/batching").json()
            health = requests.get(f"{BACKEND_URL}/api/health").json()
            history_res = requests.get(f"{BACKEND_URL}/api/assistant/history").json()
            
            chat_history = history_res.get("chat_history", [])
            gpus = telemetry.get("gpus", [])
            
            current_state = {
                "avg_temp": round(sum([g["temp"] for g in gpus]) / len(gpus), 1) if gpus else 45.0,
                "avg_util": round(sum([g["util"] for g in gpus]) / len(gpus), 1) if gpus else 10.0,
                "price": power.get("price_info", {}).get("price_per_kwh", 0.12),
                "is_peak": power.get("price_info", {}).get("is_peak_hour", False),
                "throughput": batching.get("throughput_tokens_sec", 8000),
                "latency": batching.get("avg_latency_ms", 20),
                "efficiency": batching.get("gpu_efficiency_score", 85),
                "alert_count": len(health.get("alerts", []))
            }
        except Exception:
            pass
    else:
        # Mock chat history fallback
        if "mock_chat" not in st.session_state:
            st.session_state.mock_chat = [
                {"sender": "assistant", "message": "System diagnostics offline. I am Nexus AI. I monitor your 8-node H100 cluster for thermal safety, power consumption, and inference efficiency. How can I assist you today?"}
            ]
        chat_history = st.session_state.mock_chat

    # Main layout split
    col_chat, col_suggestions = st.columns([2.5, 1.5])
    
    with col_chat:
        # Render Chat Message logs
        chat_container = st.container(height=350)
        with chat_container:
            for chat in chat_history:
                role = "assistant" if chat["sender"] == "assistant" else "user"
                avatar = "🧠" if role == "assistant" else "👤"
                with st.chat_message(role, avatar=avatar):
                    st.markdown(chat["message"])

        # Chat input box
        user_input = st.chat_input("Ask Nexus AI (e.g. 'How can I save power costs?')")
        if user_input:
            # Add user message immediately to interface
            if api_online:
                try:
                    res = requests.post(f"{BACKEND_URL}/api/assistant/chat", json={
                        "message": user_input,
                        "current_state": current_state
                    }).json()
                    st.rerun()
                except Exception as e:
                    st.error("Failed to transmit chat query.")
            else:
                st.session_state.mock_chat.append({"sender": "user", "message": user_input})
                # Mock response generator
                mock_ans = ""
                msg_lower = user_input.lower()
                if "power" in msg_lower or "cost" in msg_lower or "save" in msg_lower:
                    mock_ans = "### Power Saving Advice\nCap H100 GPU power limits to **280W** via settings to reduce operational costs by **~20%**."
                elif "thermal" in msg_lower or "temp" in msg_lower:
                    mock_ans = "### Thermal Alert Details\nGPU 5 is running warm at **79°C**. System fans adjusted to **84%** automatically to cool the node."
                else:
                    mock_ans = f"Processed client request: *\"{user_input}\"*. H100 cluster online with aggregate utilization at {current_state['avg_util']}%."
                
                st.session_state.mock_chat.append({"sender": "assistant", "message": mock_ans})
                st.rerun()

    with col_suggestions:
        st.markdown(
            """
            <div class="glass-card border-nvidia">
                <h4 style="color:#FFF; font-family:Outfit; margin-bottom: 12px;">Suggested Queries</h4>
                <p style="font-size:11px; color:#94A3B8; line-height: 1.4;">
                    Clicking a prompt will populate the system context.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        q1 = st.button("💡 How can I reduce power cost?", use_container_width=True)
        q2 = st.button("🔥 Analyze thermal profiles and safety margins", use_container_width=True)
        q3 = st.button("📦 Optimize batching parameter layout", use_container_width=True)
        
        selected_q = ""
        if q1:
            selected_q = "How can I reduce power cost?"
        elif q2:
            selected_q = "Analyze thermal profiles and safety margins"
        elif q3:
            selected_q = "Optimize batching parameter layout"
            
        if selected_q:
            if api_online:
                try:
                    requests.post(f"{BACKEND_URL}/api/assistant/chat", json={
                        "message": selected_q,
                        "current_state": current_state
                    })
                    st.rerun()
                except Exception:
                    pass
            else:
                st.session_state.mock_chat.append({"sender": "user", "message": selected_q})
                # Add preset answers
                if q1:
                    ans = "### Power Saving Advice\nCap H100 GPU power limits to **280W** via settings to reduce operational costs by **~20%**."
                elif q2:
                    ans = "### Thermal Alert Details\nGPU 5 is running warm at **79°C**. System fans adjusted to **84%** automatically to cool the node."
                else:
                    ans = "### Inference batching tuning\nSet `max_batch_size` to **64** and wait delay to **12ms** to optimize serving efficiency."
                st.session_state.mock_chat.append({"sender": "assistant", "message": ans})
                st.rerun()
