# ⚡ GPU Nexus AIOps Platform

An advanced, high-fidelity AIOps orchestration and monitoring platform for NVIDIA H100 GPU clusters. Built with FastAPI for the backend simulation engine and Streamlit for the front-end control panel.

### 🔗 Live Deployments
* **Live Web App (Streamlit):** [https://nexusgpu-v8tbjibf2xfzn4haknuiqg.streamlit.app/](https://nexusgpu-v8tbjibf2xfzn4haknuiqg.streamlit.app/)
* **Live API Engine (Render):** [https://nexusgpu-backend.onrender.com/](https://nexusgpu-backend.onrender.com/)

---

## 🚀 Key Features

* **Real-time Telemetry:** Metrics reporting for power draw, VRAM consumption, temperature safety limits, and NVLink inter-GPU bandwidth.
* **Thermal ML Predictor:** Predictive modeling of core temperatures to trigger throttling mitigation before hardware limits are breached.
* **Smart Eco-Scheduler:** Dynamic task management that detects grid energy pricing spikes and reschedules low-priority tasks.
* **Triton-style Batching Coordinator:** Configurable queue coordinators optimizing throughput and latency.
* **Nexus AI Assistant:** Conversational agent providing real-time diagnostic analysis and recommendations.
* **Floating Desktop Widget:** Picture-in-Picture power HUD overlaying system apps.

---

## 🛠️ Tech Stack

* **Frontend:** Streamlit, Plotly, HTML/CSS/JS (custom component injection)
* **Backend:** FastAPI (Python), Uvicorn, REST API
* **Deployment:** Streamlit Community Cloud (Frontend), Render (Backend)

---

## 💻 Local Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/shivasathya24/NexusGPU.git
   cd NexusGPU
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the platform:**
   Simply run the launcher script which boots both the FastAPI backend and Streamlit frontend concurrently:
   ```bash
   python run.py
   ```
   * Frontend: `http://127.0.0.1:8501`
   * Backend: `http://127.0.0.1:8000`
