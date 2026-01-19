import os
import sys
import subprocess
import ctypes
import logging

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def request_admin():
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)

def run_powershell(command):
    try:
        result = subprocess.run(["powershell", "-Command", command], capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        logging.error(f"PowerShell error: {e}")
        return None

def get_free_space(drive="C:"):
    import psutil
    try:
        usage = psutil.disk_usage(drive)
        return usage.free / (1024**3) # GB
    except:
        return 0
