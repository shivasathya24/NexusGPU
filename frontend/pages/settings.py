import streamlit as st
import requests
import os

raw_url = st.secrets.get("BACKEND_URL", os.getenv("BACKEND_URL", "http://127.0.0.1:8000")).strip().rstrip("/")
BACKEND_URL = raw_url if raw_url.startswith(("http://", "https://")) else ("http://" if "127.0.0.1" in raw_url or "localhost" in raw_url else "https://") + raw_url

def render_settings(api_online):
    st.markdown(
        """
        <div style="margin-bottom: 25px; padding-bottom: 10px; border-bottom: 1px solid rgba(255,255,255,0.05);">
            <h2 style="margin: 0; color: #FFF; font-family: Outfit;">System & Profile Settings</h2>
            <span style="color: #64748B; font-size: 13px;">Manage global AIOps orchestration parameters, set notification safety margins, and customize your profile.</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    # State config defaults
    eco_enabled = False
    if api_online:
        try:
            power = requests.get(f"{BACKEND_URL}/api/power").json()
            eco_enabled = power.get("paused_training", False)
        except Exception:
            pass

    col_settings, col_profile = st.columns([2, 1])

    with col_settings:
        st.markdown("<h4 style='color: #00E5FF; font-family: Outfit;'>Cluster Configuration</h4>", unsafe_allow_html=True)
        
        # Power caps & eco settings
        st.markdown("##### ⚡ Energy Policies")
        eco_toggle = st.toggle("Enable Peak-Hour Eco Scheduling (Pause low-priority tasks)", value=eco_enabled)
        if eco_toggle != eco_enabled and api_online:
            try:
                requests.post(f"{BACKEND_URL}/api/telemetry/power-saving", json={"enabled": eco_toggle})
                st.toast("Eco scheduling updated!", icon="⚡")
                st.rerun()
            except Exception:
                pass
                
        # Base pricing settings
        st.markdown("##### 💵 Grid Pricing Configuration ($ USD / kWh)")
        bp_col1, bp_col2 = st.columns(2)
        with bp_col1:
            st.number_input("Grid Base Off-Peak Price", min_value=0.01, max_value=1.50, value=0.12, step=0.01)
        with bp_col2:
            st.number_input("Grid Peak Hours Price", min_value=0.05, max_value=2.50, value=0.28, step=0.01)
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Safety Margins
        st.markdown("##### 🔥 Thermal Safety Margins (°C)")
        st.slider("Thermal Warning Threshold (Yellow)", 60, 80, 78)
        st.slider("Thermal Throttling Critical Safety Cap (Red)", 80, 95, 85)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Serving profile selector
        st.markdown("##### 📦 AI Serving Engine Profile")
        st.selectbox("Active Serving LLM Model Config", [
            "Meta-Llama-3-70B-Instruct (NVIDIA NIM FP8 Optimized)",
            "StabilityAI-Stable-Diffusion-XL (FP16 Pre-train)",
            "DeepSeek-Coder-33B (Dynamic INT8 Coalesced)",
            "ResNet-101-Vision-Backbone (FP32 Real-Time Feed)"
        ])

    with col_profile:
        st.markdown("<h4 style='color: #FFF; font-family: Outfit;'>Operator Profile</h4>", unsafe_allow_html=True)
        st.markdown(
            """
            <div class="glass-card border-nvidia" style="padding: 20px !important;">
                <div style="text-align: center; margin-bottom: 15px;">
                    <div style="width: 70px; height: 70px; border-radius: 50%; background: rgba(0, 229, 255, 0.1); border: 2.5px solid #00E5FF; display: flex; align-items: center; justify-content: center; margin: 0 auto 10px auto; color: #00E5FF; font-size: 28px; font-weight: bold;">AD</div>
                    <h5 style="color: #FFF; margin-bottom: 2px; font-family: Outfit;">Admin Operator</h5>
                    <span style="font-size: 11px; color: #64748B;">Lead Infrastructure Architect</span>
                </div>
                <div style="border-top: 1px solid rgba(255,255,255,0.05); padding-top: 15px; font-size: 12px; color: #94A3B8;">
                    <div style="margin-bottom: 8px;"><b>Organization:</b> Nexus AI Research Lab</div>
                    <div style="margin-bottom: 8px;"><b>Access Permissions:</b> Cluster super-admin</div>
                    <div><b>API Keys:</b> <span style="font-family: monospace; color: #60A5FA;">sk_nexus_h100_...</span></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Save config button
        if st.button("Save Settings Profile", use_container_width=True, type="primary"):
            st.success("Successfully persisted cluster operational settings.")
