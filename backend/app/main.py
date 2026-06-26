import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router

app = FastAPI(
    title="GPU Nexus AIOps Backend Engine",
    description="High-fidelity NVIDIA H100 GPU cluster simulation, thermal ML prediction, dynamic power pricing scheduler, and Triton-style batching coordinator API.",
    version="1.0.0"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact Streamlit origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router, prefix="/api")

@app.get("/")
def read_root():
    return {
        "status": "Online",
        "message": "GPU Nexus AIOps backend server is active. Documentation available at /docs",
        "endpoints": {
            "telemetry": "/api/telemetry",
            "thermal": "/api/thermal",
            "power": "/api/power",
            "batching": "/api/batching",
            "health": "/api/health"
        }
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
