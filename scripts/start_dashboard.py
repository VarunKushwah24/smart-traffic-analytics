import os
import sys
import subprocess

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
app_path = os.path.join(ROOT, "dashboard", "app.py")

def main():
    print(f"Launching Streamlit Traffic BI Dashboard from {app_path}...")
    venv_streamlit = os.path.join(ROOT, ".venv", "Scripts", "streamlit.exe")
    cmd = [
        venv_streamlit if os.path.exists(venv_streamlit) else "streamlit",
        "run",
        app_path,
        "--server.port", "8501",
        "--server.address", "0.0.0.0"
    ]
    subprocess.run(cmd)

if __name__ == "__main__":
    main()
