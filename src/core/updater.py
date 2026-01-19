import json
import urllib.request
import logging
from PySide6.QtCore import QThread, Signal

class UpdateWorker(QThread):
    finished = Signal(dict)
    def __init__(self, github_api_url):
        super().__init__()
        self.github_api_url = github_api_url

    def run(self):
        try:
            req = urllib.request.Request(self.github_api_url)
            req.add_header('User-Agent', 'Ultimate-Optimizer-App')
            with urllib.request.urlopen(req, timeout=10) as response:
                release_data = json.loads(response.read().decode())
            
            update_json_url = None
            for asset in release_data.get("assets", []):
                if asset.get("name") == "update.json":
                    update_json_url = asset.get("browser_download_url")
                    break
            
            if not update_json_url:
                self.finished.emit({})
                return

            req_json = urllib.request.Request(update_json_url)
            req_json.add_header('User-Agent', 'Ultimate-Optimizer-App')
            with urllib.request.urlopen(req_json, timeout=10) as resp:
                update_json_data = json.loads(resp.read().decode())
                
            update_json_data["html_url"] = release_data.get("html_url")
            update_json_data["body"] = release_data.get("body")
            
            self.finished.emit(update_json_data)
        except Exception as e:
            logging.error(f"Update Check Error: {e}")
            self.finished.emit({})
