from pathlib import Path
import os
import logging

APP_NAME = "UltimateOptimizer"
# Use LOCALAPPDATA for logs
BASE_PATH = Path(os.getenv("LOCALAPPDATA")) / APP_NAME
LOG_DIR = BASE_PATH / "logs"

def setup_logger():
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        
        # Clear existing handlers to avoid double logging if re-called
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
            
        logging.basicConfig(
            filename=LOG_DIR / "app.log",
            level=logging.INFO,
            format="%(asctime)s | %(levelname)s | %(message)s",
            encoding='utf-8'
        )
        # Add console handler for development, though typically hidden in production
        console = logging.StreamHandler()
        console.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
        logging.getLogger().addHandler(console)
        
        logging.info("--- Ultimate Optimizer Session Started ---")
    except Exception as e:
        print(f"Failed to setup logger: {e}")
