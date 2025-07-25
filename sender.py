
import socket
import os
from tkinter import messagebox
from tqdm import tqdm

def send_file(file_path, ip, port=5001):
    """
    Envoie un fichier à l'IP et au port spécifiés.
    """
    if not os.path.exists(file_path):
        messagebox.showerror("Erreur", f"Le fichier {file_path} n'existe pas.")
        return

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # Se connecter au serveur
        sock.connect((ip, port))

        # Envoyer les métadonnées (nom du fichier et taille)
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        meta = f"{file_name}||{file_size}"
        sock.send(meta.encode())

        # Attendre confirmation
        response = sock.recv(1024).decode()
        if response != "OK":
            messagebox.showerror("Erreur", "La réception a été refusée.")
            return

        # Envoyer le fichier avec barre de progression
        with open(file_path, "rb") as f, tqdm(
            total=file_size, unit="B", unit_scale=True, desc="Envoi"
        ) as pbar:
            while chunk := f.read(1024):
                sock.send(chunk)
                pbar.update(len(chunk))

        messagebox.showinfo("Succès", f"Fichier {file_name} envoyé avec succès.")
    except socket.error as e:
        messagebox.showerror("Erreur", f"Erreur réseau : {str(e)}")
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors de l'envoi : {str(e)}")
    finally:
        sock.close()
        print("[SENDER] Socket fermé.")
