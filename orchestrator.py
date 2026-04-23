import subprocess
import time
import os
import signal
import sys
import threading

# ==============================================================================
#  CONFIGURATION
# ==============================================================================
AUDIO_PYTHON = r"C:\Users\Moinuddin_Projects\exp-versions\Voice Deepfake\.venv\Scripts\python.exe"
VIDEO_PYTHON = r"C:\Users\Moinuddin_Projects\exp-versions\DeepFake\backend\.venv\Scripts\python.exe"

AUDIO_DIR = r"C:\Users\Moinuddin_Projects\exp-versions\Voice Deepfake"
VIDEO_DIR = r"C:\Users\Moinuddin_Projects\exp-versions\Deepfake\backend"
FRONTEND_DIR = r"C:\Users\Moinuddin_Projects\exp-versions\Deepfake\frontend"
# ==============================================================================

# Global list to track processes for cleanup
processes = []

def install_and_import_psutil():
    """Ensures psutil is installed for accurate port killing."""
    try:
        import psutil
        return psutil
    except ImportError:
        print(" Installing required package 'psutil' for port management...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "psutil"])
        import psutil
        return psutil

# Load psutil
psutil = install_and_import_psutil()

def kill_process_on_port(port):
    """Finds and kills any process listening on a specific port."""
    killed = False
    try:
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                for con in proc.net_connections():
                    if con.laddr.port == port:
                        print(f"🧹 Port {port} is blocked by PID {proc.pid} ({proc.info['name']}) -> KILLING...")
                        proc.kill()
                        killed = True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    except Exception as e:
        print(f" Warning cleaning port {port}: {e}")
    
    if killed:
        time.sleep(1) # Give OS time to release port

def cleanup():
    """Kills all started processes."""
    print("\n Shutting down services...")
    
    # 1. Kill child processes we spawned
    for p in processes:
        try:
            if sys.platform == 'win32':
                subprocess.run(['taskkill', '/F', '/T', '/PID', str(p.pid)], 
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                p.terminate()
        except:
            pass
            
    # 2. Final sweep of ports just in case
    kill_process_on_port(3000)
    kill_process_on_port(5000)
    kill_process_on_port(5001)

def signal_handler(sig, frame):
    cleanup()
    sys.exit(0)

def start_service(name, cmd, cwd):
    print(f" Starting {name}...")
    try:
        # shell=False for Python (cleaner), shell=True for NPM (required on Windows)
        use_shell = "npm" in cmd[0]
        
        # Windows group creation flag to help with kills
        creation_flags = subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == 'win32' else 0
        
        p = subprocess.Popen(
            cmd, 
            cwd=cwd, 
            shell=use_shell,
            creationflags=creation_flags
        )
        processes.append(p)
        return p
    except Exception as e:
        print(f" Failed to start {name}: {e}")
        return None

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)

    print(" PRE-FLIGHT CHECK: Clearing ports...")
    kill_process_on_port(5002) # Identity Service
    kill_process_on_port(5001) # Audio
    kill_process_on_port(5000) # Video
    kill_process_on_port(3000) # Frontend

    print("\n Ports clear. Launching services...\n")

    # 1. Start Identity Service (Phase 1 - Copyright Detection Infrastructure)
    start_service("Identity Service (Copyright Detection)", [VIDEO_PYTHON, "identity_service.py"], VIDEO_DIR)
    time.sleep(2)

    # 2. Start Audio API
    start_service("Audio API", [AUDIO_PYTHON, "api_audio.py"], AUDIO_DIR)
    time.sleep(1)

    # 3. Start Video Backend (integrates with Identity Service for Phase 3)
    start_service("Video Backend API", [VIDEO_PYTHON, "app.py"], VIDEO_DIR)
    time.sleep(2)

    # 4. Start Frontend
    npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
    start_service("Frontend", [npm_cmd, "run", "dev"], FRONTEND_DIR)

    print("\n SYSTEM ONLINE. Press Ctrl+C to stop.\n")
    
    # Keep alive loop
    try:
        while True:
            time.sleep(1)
            # Check if any process died unexpectedly
            for p in processes:
                if p.poll() is not None:
                    print(" A service died unexpectedly! Shutting down...")
                    cleanup()
                    sys.exit(1)
    except KeyboardInterrupt:
        cleanup()
