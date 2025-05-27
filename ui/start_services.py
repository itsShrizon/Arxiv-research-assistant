"""Script to run both the backend server and UI."""

import subprocess
import sys
import time
import webbrowser
from pathlib import Path

def main():
    # Get the project root directory
    project_root = Path(__file__).parent.parent.parent.parent

    # Start the backend server
    print("Starting arXiv backend server...")
    server_process = subprocess.Popen(
        [sys.executable, "-m", "arxiv_mcp_server"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Give the server a moment to start
    time.sleep(2)
    
    # Check if the server started successfully
    if server_process.poll() is not None:
        print("Failed to start backend server!")
        stderr = server_process.stderr.read().decode()
        print(f"Error: {stderr}")
        return
    
    print("Backend server started successfully!")
    
    # Start the Streamlit UI
    print("\nStarting Streamlit UI...")
    ui_path = project_root / "src" / "arxiv_mcp_server" / "ui" / "run_ui.py"
    ui_process = subprocess.Popen(
        ["streamlit", "run", str(ui_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Give Streamlit a moment to start
    time.sleep(3)
    
    # Open the UI in the default browser
    webbrowser.open("http://localhost:8501")
    
    print("\nBoth services are running!")
    print("- Backend server is available at http://localhost:8000")
    print("- Streamlit UI is available at http://localhost:8501")
    print("\nPress Ctrl+C to stop both services...")
    
    try:
        # Keep the script running and monitor both processes
        while True:
            # Check if either process has terminated
            if server_process.poll() is not None:
                print("\nBackend server stopped unexpectedly!")
                break
            if ui_process.poll() is not None:
                print("\nUI stopped unexpectedly!")
                break
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down services...")
    finally:
        # Clean up processes
        server_process.terminate()
        ui_process.terminate()
        try:
            server_process.wait(timeout=5)
            ui_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_process.kill()
            ui_process.kill()
        
        print("Services stopped successfully!")

if __name__ == "__main__":
    main()
