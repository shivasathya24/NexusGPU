import streamlit as st

def render_landing():
    # Hero Title and Subtitle with Custom Layout
    st.markdown(
        """
        <div style="text-align: center; padding: 20px 0 10px 0;">
            <span style="background: rgba(0, 229, 255, 0.12); color: #00E5FF; padding: 6px 14px; border-radius: 9999px; font-size: 11px; font-weight: 700; border: 1px solid rgba(0, 229, 255, 0.25); text-transform: uppercase; letter-spacing: 0.15em;">Enterprise SaaS Platform</span>
            <h1 style="font-size: 3.5rem; margin-top: 15px; margin-bottom: 5px; font-weight: 800; background: linear-gradient(135deg, #FFFFFF 0%, #A5B4FC 50%, #00E5FF 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-family: 'Outfit', sans-serif;">
                GPU Nexus AIOps Platform
            </h1>
            <p style="font-size: 1.25rem; color: #94A3B8; max-width: 800px; margin: 0 auto 30px auto; line-height: 1.6; font-weight: 400;">
                Intelligent Monitoring, Thermal Prediction, Power Optimization, and AI Workload Orchestration.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    import os
    import base64
    # Hero GPU Visualization - Natively rendered SVG graphic with SMIL animations
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        svg_path = os.path.join(base_dir, "assets", "gpu_visual.svg")
        with open(svg_path, "r", encoding="utf-8") as f:
            svg_content = f.read()
        
        # Base64 encode SVG to avoid path and Javascript TypeError issues
        b64_svg = base64.b64encode(svg_content.encode("utf-8")).decode("utf-8")
        svg_data_uri = f"data:image/svg+xml;base64,{b64_svg}"
        
        # Single self-contained markdown call to avoid split tag issues
        st.markdown(
            f"""
            <div style="display:flex; justify-content:center; margin-bottom: 30px;">
                <img src="{svg_data_uri}" style="max-width: 100%; height: auto; border-radius: 20px;" />
            </div>
            """,
            unsafe_allow_html=True
        )
    except Exception as ex:
        st.error(f"Error loading GPU core animation: {str(ex)}")

    # Animated Statistics Cards Banner
    st.markdown('<div style="margin-bottom: 25px;"><h3 style="text-align: center; color: #FFF; font-family: Outfit;">Active Cluster Analytics Baseline</h3></div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(
            """
            <div class="glass-card border-nvidia">
                <div class="stat-label">TOTAL ACCELERATORS</div>
                <div class="stat-value">8x H100</div>
                <div style="font-size: 11px; color: #10B981;">● Active (80GB SXM5)</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            """
            <div class="glass-card" style="border-left: 4px solid #00D2FF !important;">
                <div class="stat-label">AGGREGATE BANDWIDTH</div>
                <div class="stat-value">7.2 TB/s</div>
                <div style="font-size: 11px; color: #00D2FF;">NVLink 4th-Gen Interconnect</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col3:
        st.markdown(
            """
            <div class="glass-card" style="border-left: 4px solid #A855F7 !important;">
                <div class="stat-label">AI COMPUTE POWER</div>
                <div class="stat-value">32 PFLOPS</div>
                <div style="font-size: 11px; color: #A855F7;">FP8 Tensor Capacity</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col4:
        st.markdown(
            """
            <div class="glass-card" style="border-left: 4px solid #E2E8F0 !important;">
                <div class="stat-label">CLUSTER PUE RATING</div>
                <div class="stat-value">1.42 PUE</div>
                <div style="font-size: 11px; color: #94A3B8;">Target Power Efficiency</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<br><br>", unsafe_allow_html=True)

    # Feature Showcase Section
    st.markdown('<h2 style="text-align: center; color: #FFF; font-family: Outfit; margin-bottom: 30px;">Core Capabilities</h2>', unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(
            """
            <div class="glass-card" style="margin-bottom: 20px;">
                <h4 style="color: #00E5FF; margin-bottom: 10px; font-size: 18px;">🔥 Thermal Intelligence & ML Forecasting</h4>
                <p style="font-size: 14px; color: #94A3B8; line-height: 1.5;">
                    Runs scikit-learn models directly in our daemon processes to predict core hot-spots, thermal throttling probability, and forecast temperatures 15 minutes ahead. Automatically suggests preventive measures.
                </p>
            </div>
            <div class="glass-card" style="margin-bottom: 20px;">
                <h4 style="color: #8B5CF6; margin-bottom: 10px; font-size: 18px;">⚡ Smart Peak-Shaving Power Manager</h4>
                <p style="font-size: 14px; color: #94A3B8; line-height: 1.5;">
                    Links with real-time dynamic grid electricity prices. Pauses or suspends background training runs during peak pricing hours ($0.28/kWh) and re-allocates workloads to compute power limits at lower costs.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
    with c2:
        st.markdown(
            """
            <div class="glass-card" style="margin-bottom: 20px;">
                <h4 style="color: #F59E0B; margin-bottom: 10px; font-size: 18px;">📦 Dynamic AI Inference Batcher</h4>
                <p style="font-size: 14px; color: #94A3B8; line-height: 1.5;">
                    Simulates deep-learning batch execution schedules (similar to Triton or vLLM). Groups incoming requests based on token counts to optimize Tensor Core alignment and maximize processing efficiency.
                </p>
            </div>
            <div class="glass-card" style="margin-bottom: 20px;">
                <h4 style="color: #10B981; margin-bottom: 10px; font-size: 18px;">🧠 Nexus AI Assistant widget</h4>
                <p style="font-size: 14px; color: #94A3B8; line-height: 1.5;">
                    Intelligent diagnostic assistant widget and chat interface that processes telemetry triggers, identifies interconnect NVLink bottlenecks, generates system tickets, and helps schedule actions.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<br><br>", unsafe_allow_html=True)

    # Architecture Overview & Workflow
    st.markdown('<h2 style="text-align: center; color: #FFF; font-family: Outfit; margin-bottom: 30px;">Data Ingestion & Orchestration Workflow</h2>', unsafe_allow_html=True)
    
    st.markdown(
        """
        <div class="glass-card" style="padding: 30px !important;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 20px;">
                <div style="flex: 1; min-width: 150px; text-align: center;">
                    <div style="width: 50px; height: 50px; border-radius: 50%; background: rgba(0, 229, 255, 0.1); border: 2px solid #00E5FF; display: flex; align-items: center; justify-content: center; margin: 0 auto 10px auto; color: #00E5FF; font-weight: bold;">01</div>
                    <h5 style="color: #FFF; margin-bottom: 5px;">Telemetry Ingest</h5>
                    <p style="font-size: 11px; color: #64748B;">Querying 8x GPU states at 1-sec granularity</p>
                </div>
                <div style="color: #00E5FF; font-size: 20px;">➔</div>
                <div style="flex: 1; min-width: 150px; text-align: center;">
                    <div style="width: 50px; height: 50px; border-radius: 50%; background: rgba(139, 92, 246, 0.1); border: 2px solid #8B5CF6; display: flex; align-items: center; justify-content: center; margin: 0 auto 10px auto; color: #8B5CF6; font-weight: bold;">02</div>
                    <h5 style="color: #FFF; margin-bottom: 5px;">ML Core Analysis</h5>
                    <p style="font-size: 11px; color: #64748B;">Regressive model calculates thermal risk</p>
                </div>
                <div style="color: #8B5CF6; font-size: 20px;">➔</div>
                <div style="flex: 1; min-width: 150px; text-align: center;">
                    <div style="width: 50px; height: 50px; border-radius: 50%; background: rgba(245, 158, 11, 0.1); border: 2px solid #F59E0B; display: flex; align-items: center; justify-content: center; margin: 0 auto 10px auto; color: #F59E0B; font-weight: bold;">03</div>
                    <h5 style="color: #FFF; margin-bottom: 5px;">Power Scheduling</h5>
                    <p style="font-size: 11px; color: #64748B;">Price checking grid to schedule pauses</p>
                </div>
                <div style="color: #F59E0B; font-size: 20px;">➔</div>
                <div style="flex: 1; min-width: 150px; text-align: center;">
                    <div style="width: 50px; height: 50px; border-radius: 50%; background: rgba(239, 68, 68, 0.1); border: 2px solid #EF4444; display: flex; align-items: center; justify-content: center; margin: 0 auto 10px auto; color: #EF4444; font-weight: bold;">04</div>
                    <h5 style="color: #FFF; margin-bottom: 5px;">Triton Batching</h5>
                    <p style="font-size: 11px; color: #64748B;">Consolidates inference tasks dynamically</p>
                </div>
                <div style="color: #EF4444; font-size: 20px;">➔</div>
                <div style="flex: 1; min-width: 150px; text-align: center;">
                    <div style="width: 50px; height: 50px; border-radius: 50%; background: rgba(16, 185, 129, 0.1); border: 2px solid #10B981; display: flex; align-items: center; justify-content: center; margin: 0 auto 10px auto; color: #10B981; font-weight: bold;">05</div>
                    <h5 style="color: #FFF; margin-bottom: 5px;">AIOps Mitigation</h5>
                    <p style="font-size: 11px; color: #64748B;">Capping, migrating or dispatching actions</p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<br><br><hr style='border-color: rgba(255,255,255,0.05);'><br>", unsafe_allow_html=True)

    # Footer
    st.markdown(
        """
        <div style="display: flex; justify-content: space-between; align-items: center; color: #64748B; font-size: 12px; padding-bottom: 30px;">
            <div>GPU Nexus AIOps platform | Capstone Research presentation</div>
            <div>Built for NVIDIA H100 cluster virtualization monitoring</div>
            <div>Powered by FastAPI, Streamlit, and Scikit-Learn</div>
        </div>
        """,
        unsafe_allow_html=True
    )
