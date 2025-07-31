import json
import os
from datetime import datetime


def load_history():
    config_file = "config.json"
    if not os.path.exists(config_file):
        print(f"Fichier {config_file} non trouvé, retourne une liste vide.")
        return []
    try:
        with open(config_file, "r") as f:
            data = json.load(f)
            print(f"Données chargées depuis {config_file} : {data}")
            return data.get("history", [])
    except Exception as e:
        print(f"Erreur lors du chargement de {config_file} : {e}")
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
    print(f"Ajout de l'entrée à l'historique : {entry}")

    config_data = {"history": history}
    try:
        with open(config_file, "w") as f:
            json.dump(config_data, f, indent=4)
        print(f"Historique sauvegardé dans {config_file} : {config_data}")
    except Exception as e:
        print(f"Erreur lors de l'écriture dans {config_file} : {e}")