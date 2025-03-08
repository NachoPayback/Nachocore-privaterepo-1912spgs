import ctypes

# Constants for SetThreadExecutionState.
ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001

def start_sleep_blocker():
    """
    Prevents the system from sleeping.
    """
    ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED)
    print("Sleep blocker started.")

def stop_sleep_blocker():
    """
    Allows the system to sleep normally.
    """
    ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS)
    print("Sleep blocker stopped.")
