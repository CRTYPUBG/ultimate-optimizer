import subprocess
import os
import sys
import shutil
import logging
import json
from datetime import datetime

# --- CONFIGURATION ---
VERSION = "1.1.6"
APP_NAME = "UltimateOptimizer"
PFX_FILE = r"C:\Users\LenovoPC\cert.pfx"
PFX_PASS = "ueo586_crty555"
SIGNTOOL_BASE = r"C:\Program Files (x86)\Windows Kits\10\bin"
ISS_FILE = "setup.iss"

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
    for root, dirs, files in os.walk(SIGNTOOL_BASE):
        if "signtool.exe" in files and "x64" in root:
            return os.path.join(root, "signtool.exe")
    return None

def find_iscc():
    paths = [
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe"
    ]
    for p in paths:
        if os.path.exists(p): return p
    return None

def main():
    print(f"--- {APP_NAME} v{VERSION} Full Build System ---")
    
    # 1. Build EXE with PyInstaller
    if not run_command("build_exe.bat", "PyInstaller EXE Build"):
        sys.exit(1)

    # 2. Sign the EXE
    signtool = find_signtool()
    if signtool and os.path.exists(PFX_FILE):
        exe_path = f"dist\\{APP_NAME}.exe"
        sign_cmd = f'"{signtool}" sign /f "{PFX_FILE}" /p {PFX_PASS} /d "{APP_NAME}" /tr http://timestamp.digicert.com /td sha256 /fd sha256 "{exe_path}"'
        if run_command(sign_cmd, "Signing Main EXE"):
            verify_cmd = f'"{signtool}" verify /pa /v "{exe_path}"'
            run_command(verify_cmd, "Verifying Main EXE Signature")
            run_command(verify_cmd, "Verifying Main EXE Signature")
        else:
            logging.warning("EXE signing failed!")
        
        # Sertifikayı dist klasörüne kopyala (Manuel kurulum için)
        if os.path.exists("C:\\Users\\LenovoPC\\cert.cer"):
            shutil.copy("C:\\Users\\LenovoPC\\cert.cer", "dist\\cert.cer")
    else:
        logging.warning("SignTool or PFX not found. Skipping EXE signing.")

    # 3. Inno Setup Build
    iscc = find_iscc()
    if iscc:
        if not run_command(f'"{iscc}" {ISS_FILE}', "Inno Setup Installer Build"):
            sys.exit(1)
    else:
        logging.error("ISCC.exe not found! Install Inno Setup 6.")
        sys.exit(1)

    # 4. Sign the Installer
    if signtool and os.path.exists(PFX_FILE):
        installer_dir = "installer"
        setups = [f for f in os.listdir(installer_dir) if f.endswith(".exe") and VERSION in f]
        if setups:
            setup_path = os.path.join(installer_dir, setups[0])
            sign_setup = f'"{signtool}" sign /f "{PFX_FILE}" /p {PFX_PASS} /d "{APP_NAME} Installer" /tr http://timestamp.digicert.com /td sha256 /fd sha256 "{setup_path}"'
            if run_command(sign_setup, "Signing Installer EXE"):
                verify_setup = f'"{signtool}" verify /pa /v "{setup_path}"'
                verify_setup = f'"{signtool}" verify /pa /v "{setup_path}"'
                run_command(verify_setup, "Verifying Installer Signature")
            
            # Sertifikayı installer klasörüne de kopyala
            if os.path.exists("C:\\Users\\LenovoPC\\cert.cer"):
                shutil.copy("C:\\Users\\LenovoPC\\cert.cer", "installer\\cert.cer")

    print("\n--- BUILD COMPLETED SUCCESSFULLY ---")
    print(f"Location: {os.path.abspath('installer')}")

if __name__ == "__main__":
    main()
