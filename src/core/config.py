import os
import platform
import logging

def get_data_dir():
    app_data = os.environ.get('LOCALAPPDATA') or os.path.expanduser('~')
    path = os.path.join(app_data, "UltimateOptimizer")
    os.makedirs(path, exist_ok=True)
    return path

DATA_DIR = get_data_dir()
SETTINGS_FILE = os.path.join(DATA_DIR, 'Settings.json')
VERSION_FILE = os.path.join(DATA_DIR, 'Version.json')
DNA_FILE = os.path.join(DATA_DIR, 'DNA_Profiles.json')
LOG_FILE = os.path.join(DATA_DIR, 'app.log')

# Paths for assets
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ASSETS_DIR = os.path.join(BASE_DIR, "assets", "icons")

def get_asset_path(filename):
    path = os.path.join(ASSETS_DIR, filename)
    if os.path.exists(path):
        return path
    # Fallback to current directory for local dev if assets folder missing
    return filename

GITHUB_API_URL = "https://api.github.com/repos/CRTYPUBG/ultimate-optimizer/releases/latest"
CURRENT_VERSION = "v1.1.8"
