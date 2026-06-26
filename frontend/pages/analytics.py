import streamlit as st
import requests
import os
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from io import BytesIO

# ReportLab imports for PDF generation
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
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

def generate_pdf_report(gpus, power_info, health_info, thermal_info):
    """
    Generates a beautifully structured PDF report in memory using ReportLab.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles matching dark/cyber branding elements
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        textColor=colors.HexColor('#00A3A6'),
        spaceAfter=6
    )
    
    subtitle_style = ParagraphStyle(
        'DocSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor('#475569'),
        spaceAfter=20
    )
    
    section_heading = ParagraphStyle(
        'SecHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        textColor=colors.HexColor('#0F172A'),
        spaceBefore=15,
        spaceAfter=8,
        borderColor=colors.HexColor('#00A3A6'),
        borderWidth=1,
        borderPadding=4
    )
    
    body_style = ParagraphStyle(
        'Body',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=9.5,
        textColor=colors.HexColor('#334155'),
        spaceAfter=6
    )
    
    header_cell = ParagraphStyle(
        'HeaderCell',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        textColor=colors.white
    )
    
    body_cell = ParagraphStyle(
        'BodyCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        textColor=colors.HexColor('#1E293B')
    )

    story = []
    
    # 1. Header Bar / Title
    story.append(Paragraph("GPU NEXUS AIOps PLATFORM", title_style))
    story.append(Paragraph(f"Cluster Executive Analytics & Diagnostics Report | Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}", subtitle_style))
    story.append(Spacer(1, 10))
    
    # 2. Executive Summary Box
    summary_data = [
        [
            Paragraph("<b>Cluster Size:</b> 8x H100 GPU", body_cell),
            Paragraph(f"<b>Aggregate Health:</b> {health_info.get('health_score', 100.0)}%", body_cell),
        ],
        [
            Paragraph(f"<b>Saved Electricity:</b> {power_info.get('savings_info', {}).get('saved_energy_kwh', 0.0)} kWh", body_cell),
            Paragraph(f"<b>Saved Budget:</b> ${power_info.get('savings_info', {}).get('saved_cost_usd', 0.0)} USD", body_cell),
        ],
        [
            Paragraph(f"<b>Carbon Offset:</b> {power_info.get('savings_info', {}).get('co2_saved_kg', 0.0)} kg CO2", body_cell),
            Paragraph(f"<b>Grid Price Status:</b> {'PEAK RATE ($0.28)' if power_info.get('price_info', {}).get('is_peak_hour') else 'OFF-PEAK ($0.12)'}", body_cell)
        ]
    ]
    summary_table = Table(summary_data, colWidths=[260, 260])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('PADDING', (0,0), (-1,-1), 8),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#E2E8F0')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    
    story.append(Paragraph("Executive Performance Summary", section_heading))
    story.append(summary_table)
    story.append(Spacer(1, 15))
    
    # 3. GPU Node Telemetry Table
    story.append(Paragraph("GPU Node Detailed Metrics Log", section_heading))
    
    # Setup node headers
    node_table_data = [[
        Paragraph("Node ID", header_cell),
        Paragraph("Status", header_cell),
        Paragraph("Temp (°C)", header_cell),
        Paragraph("Util (%)", header_cell),
        Paragraph("VRAM (%)", header_cell),
        Paragraph("Power (W)", header_cell),
        Paragraph("Clock (MHz)", header_cell)
    ]]
    
    # Fill node metrics
    for gpu in gpus:
        node_table_data.append([
            Paragraph(f"GPU {gpu['id']}", body_cell),
            Paragraph(gpu['status'], body_cell),
            Paragraph(f"{round(gpu['temp'], 1)}°C", body_cell),
            Paragraph(f"{round(gpu['util'], 1)}%", body_cell),
            Paragraph(f"{round(gpu['vram_util'], 1)}%", body_cell),
            Paragraph(f"{round(gpu['power_draw'], 1)}W", body_cell),
            Paragraph(f"{round(gpu['clock_speed'], 0)}", body_cell)
        ])
        
    node_table = Table(node_table_data, colWidths=[55, 75, 75, 75, 75, 80, 85])
    node_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
        ('PADDING', (0,0), (-1,-1), 6),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(node_table)
    story.append(Spacer(1, 15))
    
    # 4. Critical Warnings & Recommendations
    story.append(Paragraph("Active Diagnostics & Mitigation Tickets", section_heading))
    
    recs = health_info.get("recommended_actions", [])
    alerts = health_info.get("alerts", [])
    
    if not recs and not alerts:
        story.append(Paragraph("No warning tickets or active performance bottlenecks flagged in the current cycle.", body_style))
    else:
        for idx, alert in enumerate(alerts):
            story.append(Paragraph(f"• <b>[{alert['severity']}] {alert['component']}:</b> {alert['message']}", body_style))
        for idx, rec in enumerate(recs):
            story.append(Paragraph(f"• <b>Recommended Action: {rec['title']}</b> - {rec['action']}", body_style))
            
    # Build Document
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def render_analytics(api_online):
    # Fetch data for analytics display & PDF creation
    if not api_online:
        st.warning("⚠️ FastAPI Backend is offline. Displaying simulated analytics dashboard.")
        # Setup mock data structure
        gpus = [{"id": i, "status": "Healthy", "temp": 55.0 + i, "util": 75.0, "vram_util": 65.0, "power_draw": 240.0, "clock_speed": 1650.0} for i in range(8)]
        health = {
            "health_score": 96.0, "alerts": [{"severity": "WARNING", "component": "Thermal Center", "message": "GPU 7 temp warning"}],
            "bottlenecks": [], "recommended_actions": [{"title": "Activate Power Caps", "action": "Limit GPUs to 280W", "type": "cap_power"}]
        }
        power = {"savings_info": {"saved_energy_kwh": 142.0, "saved_cost_usd": 34.0, "co2_saved_kg": 56.8}, "price_info": {"is_peak_hour": False, "price_per_kwh": 0.12}}
        thermal = {"peak_temp": 68.0}
    else:
        try:
            telemetry_res = requests.get(f"{BACKEND_URL}/api/telemetry").json()
            gpus = telemetry_res["gpus"]
            health = requests.get(f"{BACKEND_URL}/api/health").json()
            power = requests.get(f"{BACKEND_URL}/api/power").json()
            thermal = requests.get(f"{BACKEND_URL}/api/thermal").json()
        except Exception as ex:
            st.error("Could not fetch data for PDF generation.")
            return

    st.markdown(
        """
        <div style="margin-bottom: 25px; padding-bottom: 10px; border-bottom: 1px solid rgba(255,255,255,0.05);">
            <h2 style="margin: 0; color: #FFF; font-family: Outfit;">Historical Analytics & Report Exporter</h2>
            <span style="color: #64748B; font-size: 13px;">Review historical thermal profiles, accumulated grid savings, and generate standard PDF reports.</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    col_btn, col_stats = st.columns([1.5, 2.5])
    
    with col_btn:
        st.markdown(
            """
            <div class="glass-card border-nvidia">
                <h4 style="color:#FFF; font-family:Outfit; margin-bottom: 15px;">Generate Performance Audit PDF</h4>
                <p style="font-size:12px; color:#94A3B8; line-height:1.5; margin-bottom:20px;">
                    Compiles current active H100 cluster parameters, dynamic energy-saving tallies, active system warnings, and diagnostic recomendations into a corporate-ready PDF document.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        pdf_bytes = generate_pdf_report(gpus, power, health, thermal)
        
        st.download_button(
            label="📄 Download Executive PDF Report",
            data=pdf_bytes,
            file_name="gpu_nexus_cluster_report.pdf",
            mime="application/pdf",
            use_container_width=True
        )
        
    with col_stats:
        # Long-term trend graphics
        st.markdown("<h4 style='color:#FFF; font-family:Outfit; margin-top:5px;'>Cluster Historical Efficiency Trends</h4>", unsafe_allow_html=True)
        
        # Power Savings Trend
        days = [f"Day {d}" for d in range(1, 8)]
        cost_savings = [12.4, 25.8, 42.1, 58.5, 75.2, 94.8, 124.5]
        energy_savings = [45.2, 85.0, 140.2, 185.0, 230.1, 290.4, 385.4]
        
        fig_savings = go.Figure()
        fig_savings.add_trace(go.Scatter(x=days, y=energy_savings, name="Energy Saved (kWh)", line=dict(color="#00E5FF", width=2.5)))
        fig_savings.add_trace(go.Scatter(x=days, y=cost_savings, name="Cost Saved ($ USD)", line=dict(color="#00D2FF", width=2.5), yaxis="y2"))
        
        fig_savings.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#94A3B8', size=11),
            margin=dict(l=10, r=10, t=10, b=10),
            height=200,
            legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1),
            yaxis=dict(title="Energy (kWh)", showgrid=True, gridcolor='rgba(255,255,255,0.03)'),
            yaxis2=dict(title="Savings ($)", overlaying="y", side="right", showgrid=False)
        )
        st.plotly_chart(fig_savings, use_container_width=True)

    # Historical metrics log table
    st.markdown("<br><h4 style='color:#FFF; font-family:Outfit;'>Historical System Diagnostics Log</h4>", unsafe_allow_html=True)
    
    log_data = {
        "Timestamp": [pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S") for _ in range(5)],
        "Event ID": ["EVT_9024", "EVT_8910", "EVT_8874", "EVT_8850", "EVT_8722"],
        "Component": ["Inference Serving", "Thermal Center", "Power Optimizer", "Cluster Node 4", "Cluster Interconnect"],
        "Severity": ["Info", "Warning", "Info", "Critical", "Warning"],
        "Details": [
            "Serving Batch Size automatically adjusted to 32.",
            "GPU Node 7 Temperature reached warning threshold (79.2°C).",
            "Peak Grid electricity price activated ($0.28/kWh). Rescheduled job runs.",
            "GPU Node 4 Throttling event detected. Core Clock scaled to 1100MHz.",
            "NVLink interconnect bandwidth congestion: Link 4-to-5 capacity > 90%."
        ]
    }
    df_logs = pd.DataFrame(log_data)
    st.dataframe(
        df_logs,
        column_config={
            "Timestamp": st.column_config.TextColumn("Timestamp"),
            "Event ID": st.column_config.TextColumn("Event ID"),
            "Component": st.column_config.TextColumn("Component"),
            "Severity": st.column_config.TextColumn("Severity"),
            "Details": st.column_config.TextColumn("Diagnostic Details", width="large")
        },
        use_container_width=True,
        hide_index=True
    )
