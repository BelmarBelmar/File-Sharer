import socket
import os
from tkinter import messagebox
from tqdm import tqdm
from utils.utils import save_history

CONFIG_FILE = "user_config.txt"

def get_user_name():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return f.read().strip()
    else:
        user_name = input("Entrez votre nom : ")
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            f.write(user_name)
        return user_name

def send_file(file_path, ip, port=5001, user_name=None, update_callback=None):
    """
    Envoie un fichier à l'IP et au port spécifiés.
    """
    user_name = get_user_name() if user_name is None else user_name
    if not os.path.exists(file_path):
        messagebox.showerror("Erreur", f"Le fichier {file_path} n'existe pas.")
        return

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((ip, port))

        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        meta = f"{file_name}||{file_size}||{user_name}"
        sock.send(meta.encode())

        response = sock.recv(1024).decode()
        if response != "OK":
            messagebox.showerror("Erreur", "La réception a été refusée.")
            return

        with open(file_path, "rb") as f, tqdm(
            total=file_size, unit="B", unit_scale=True, desc="Envoi"
        ) as pbar:
            sent = 0
            while chunk := f.read(1024):
                sock.send(chunk)
                sent += len(chunk)
                pbar.update(len(chunk))
                if update_callback:
                    percentage = (sent / file_size) * 100
                    update_callback(percentage)

        messagebox.showinfo("Succès", f"Fichier {file_name} envoyé avec succès par {user_name}.")
        save_history("sent", file_name, ip)
    except socket.error as e:
        messagebox.showerror("Erreur", f"Erreur réseau : {str(e)}")
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors de l'envoi : {str(e)}")
    finally:
        sock.close()
        print("[SENDER] Socket fermé.")
