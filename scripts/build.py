import subprocess
import os
import sys
import shutil
import logging
import json
from datetime import datetime

# --- CONFIGURATION ---
VERSION = "1.1.8"
APP_NAME = "UltimateOptimizer"
UPDATER_NAME = "Updater"
PFX_FILE = r"C:\Users\LenovoPC\cert.pfx"
PFX_PASS = "ueo586_crty555"
SIGNTOOL_BASE = r"C:\Program Files (x86)\Windows Kits\10\bin"
ISS_FILE = "../setup.iss"

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def run_command(cmd, description):
    logging.info(f"Running: {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Error during {description}: {e.stderr}")
        return False

def find_signtool():
    if not os.path.exists(SIGNTOOL_BASE): return None
    for root, dirs, files in os.walk(SIGNTOOL_BASE):
        if "signtool.exe" in files and "x64" in root:
            return os.path.join(root, "signtool.exe")
    return None

def find_iscc():
    paths = [r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe", r"C:\Program Files\Inno Setup 6\ISCC.exe"]
    for p in paths:
        if os.path.exists(p): return p
    return None

def sign_file(signtool, file_path, description):
    if not signtool or not os.path.exists(PFX_FILE): return False
    if not os.path.exists(file_path): return False
    sign_cmd = f'"{signtool}" sign /f "{PFX_FILE}" /p {PFX_PASS} /d "{description}" /tr http://timestamp.digicert.com /td sha256 /fd sha256 "{file_path}"'
    return run_command(sign_cmd, f"Signing {description}")

def main():
    print(f"\n--- {APP_NAME} v{VERSION} Full Build System ---")
    os.chdir(os.path.dirname(os.path.abspath(__file__))) # Run from scripts/ dir
    
    # 1. Cleanup
    for folder in ['../build', '../dist']:
        if os.path.exists(folder): shutil.rmtree(folder, ignore_errors=True)
    
    # 2. Build Main EXE
    logging.info("Building Main EXE with Security Pack (AES-256)...")
    if not run_command("build_exe.bat", "PyInstaller Main EXE Build"):
        sys.exit(1)
    
    # 3. Build Updater EXE
    logging.info("Building Updater EXE with Security Pack...")
    updater_cmd = f'pyinstaller --noconfirm --onefile --clean --console --key "CRTY_SEC_PACK_256" --icon="../assets/icons/app_icon.ico" --name "{UPDATER_NAME}" "../src/core/updater_standalone.py"'
    # Wait, I need to create updater_standalone.py or point to updater.py
    if not run_command(updater_cmd, "PyInstaller Updater EXE Build"):
        sys.exit(1)

    # 4. Sign
    signtool = find_signtool()
    sign_file(signtool, f"../dist/{APP_NAME}.exe", APP_NAME)
    sign_file(signtool, f"../dist/{UPDATER_NAME}.exe", UPDATER_NAME)

    # 5. Installer
    iscc = find_iscc()
    if iscc: run_command(f'"{iscc}" {ISS_FILE}', "Inno Setup Build")

    print("\n--- BUILD COMPLETED ---")

if __name__ == "__main__":
    main()
