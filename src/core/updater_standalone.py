import os
import sys
import json
import hashlib
import zipfile
import subprocess
import time
import psutil
import shutil

def get_sha256(file_path):
    sha = hashlib.sha256()
    with open(file_path, 'rb') as f:
        while True:
            data = f.read(65536)
            if not data: break
            sha.update(data)
    return sha.hexdigest().lower()

def kill_process(name):
    name_lower = name.lower()
    for proc in psutil.process_iter(['name']):
        try:
            p_name = proc.info['name'].lower()
            if p_name == name_lower or p_name == f"{name_lower}.exe":
                proc.kill()
                proc.wait(timeout=5)
        except: pass

def main():
    print("=== Ultimate Optimizer Updater ===")
    try:
        base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        update_json_path = os.path.join(base_dir, "update.json")
        if not os.path.exists(update_json_path):
            print("update.json not found!")
            time.sleep(3)
            return

        with open(update_json_path, 'r', encoding='utf-8') as f:
            update_data = json.load(f)

        version = update_data.get("version", "Unknown")
        asset_name = update_data.get("asset", "UltimateOptimizer_Update.zip")
        expected_hash = update_data.get("sha256", "").lower()
        exe_name = update_data.get("exe", "UltimateOptimizer.exe")

        print(f"New Version: {version}")
        
        aria2_path = os.path.join(base_dir, "tools", "aria2c.exe")
        if not os.path.exists(aria2_path):
            aria2_path = os.path.join(base_dir, "aria2c.exe")
            if not os.path.exists(aria2_path):
                print("aria2c.exe not found!")
                time.sleep(5)
                return

        update_temp_dir = os.path.join(base_dir, "update")
        if not os.path.exists(update_temp_dir): os.makedirs(update_temp_dir)
        zip_path = os.path.join(update_temp_dir, "update.zip")
        
        asset_url = f"https://github.com/CRTYPUBG/ultimate-optimizer/releases/latest/download/{asset_name}"
        cmd = [aria2_path, "-x16", "-s16", "-k1M", "--continue=true", "-d", "update", "-o", "update.zip", asset_url]

        print("Downloading...")
        subprocess.run(cmd, check=True)

        print("Verifying...")
        if get_sha256(zip_path) != expected_hash:
            print("SHA256 Mismatch!")
            time.sleep(10)
            return

        print(f"Closing {exe_name}...")
        kill_process(exe_name.replace(".exe", ""))
        time.sleep(2)

        print("Extracting...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(base_dir)

        print(f"Restarting {exe_name}...")
        target_exe = os.path.join(base_dir, exe_name)
        if os.path.exists(target_exe):
            subprocess.Popen([target_exe], shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)

        print("Update Success.")
        shutil.rmtree(update_temp_dir)
        os.remove(update_json_path)

    except Exception as e:
        print(f"Update Failed: {e}")
        time.sleep(10)

if __name__ == "__main__":
    main()
