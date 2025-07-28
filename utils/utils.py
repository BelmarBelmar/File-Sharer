import json
import os
from datetime import datetime


def load_history():
    config_file = "config.json"
    if not os.path.exists(config_file):
        return []
    try:
        with open(config_file, "r") as f:
            return json.load(f).get("history", [])
    except Exception:
        return []


def save_history(operation, file_name, ip):
    config_file = "config.json"
    history = load_history()
    entry = {
        "operation": operation,  # "sent" ou "received"
        "file_name": file_name,
        "ip": ip,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    history.append(entry)
    
    config_data = {"history": history}
    try:
        with open(config_file, "w") as f:
            json.dump(config_data, f, indent=4)
    except Exception as e:
        print(f"Erreur lors de l'écriture dans config.json : {e}")