import subprocess
import time
import sys
import os

def main():
    print("=================================================================")
    print("               GPU Nexus AIOps Platform Launcher                 ")
    print("=================================================================")
    
    # Paths setup
    root_dir = os.path.dirname(os.path.abspath(__file__))
    venv_python = os.path.join(root_dir, ".venv", "Scripts", "python.exe")
    
    if not os.path.exists(venv_python):
        # Fallback to current system python if venv not found
        venv_python = sys.executable
        print(f"[*] Virtual environment python not found at {venv_python}. Using system python: {venv_python}")
    else:
        print(f"[*] Using virtual environment python: {venv_python}")

    backend_dir = os.path.join(root_dir, "backend")
    frontend_dir = os.path.join(root_dir, "frontend")

    print("[*] Launching FastAPI Backend Engine on http://127.0.0.1:8000...")
    backend_proc = subprocess.Popen(
        [venv_python, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
        cwd=backend_dir
    )

    # Allow backend to warm up
    time.sleep(2)

    print("[*] Launching Streamlit UI Engine on http://127.0.0.1:8501...")
    frontend_proc = subprocess.Popen(
        [venv_python, "-m", "streamlit", "run", "app.py", "--server.port", "8501"],
        cwd=frontend_dir
    )

    print("\n[v] Both services are running concurrently.")
    print("    - Backend: http://127.0.0.1:8000")
    print("    - Frontend: http://127.0.0.1:8501")
    print("[*] Press Ctrl+C to stop both processes.\n")

    try:
        while True:
            # Check if backend terminated
            if backend_proc.poll() is not None:
                print(f"[!] Backend process exited with code {backend_proc.poll()}")
                break
                
            # Check if frontend terminated
            if frontend_proc.poll() is not None:
                print(f"[!] Frontend process exited with code {frontend_proc.poll()}")
                break

            time.sleep(1.0)

    except KeyboardInterrupt:
        print("\n[*] Shutting down servers...")
    finally:
        print("[*] Terminating processes...")
        backend_proc.terminate()
        frontend_proc.terminate()
        try:
            backend_proc.wait(timeout=3)
            frontend_proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            backend_proc.kill()
            frontend_proc.kill()
        print("[v] Shutdown complete.")

if __name__ == "__main__":
    main()
