import psutil
import time
import threading

# Global variable to hold the monitoring thread.
monitor_thread = None
monitoring = False

def _monitor():
    global monitoring
    # Continue running until the monitoring flag is turned off.
    while monitoring:
        for proc in psutil.process_iter(attrs=["name"]):
            try:
                proc_name = proc.info["name"]
                if proc_name and proc_name.lower() in ["taskmgr.exe", "processhacker.exe"]:
                    proc.kill()
                    # Log a message (or print) if desired.
                    print(f"Security Monitor: Killed process {proc_name}")
            except Exception as e:
                # If we can't kill the process, we log/ignore.
                print(f"Security Monitor error: {e}")
        time.sleep(2)  # Check every 2 seconds.

def start_security_monitor():
    """Starts a security monitor thread that kills suspicious processes."""
    global monitor_thread, monitoring
    if not monitoring:
        monitoring = True
        monitor_thread = threading.Thread(target=_monitor, daemon=True)
        monitor_thread.start()
        print("Security monitor started.")

def stop_security_monitor():
    """Stops the security monitor thread."""
    global monitoring, monitor_thread
    monitoring = False
    # Optionally wait a bit for the thread to exit.
    if monitor_thread:
        monitor_thread.join(timeout=3)
        print("Security monitor stopped.")
