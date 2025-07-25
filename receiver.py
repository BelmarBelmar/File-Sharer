import os
from pathlib import Path
import socket
from tkinter import messagebox
from tqdm import tqdm

# Constantes configurables
BUFFER_SIZE = 4096
SAVE_FOLDER = "~/Downloads/files_shared"

def receive_file(conn, addr, save_folder=SAVE_FOLDER):
    """
    Reçoit un fichier à partir d'une connexion fournie.
    Retourne True si le fichier est reçu avec succès, False sinon.
    """
    if conn is None or addr is None:
        print("[RECEIVER] Aucune connexion valide.")
        return False

    # Créer le dossier de sauvegarde s'il n'existe pas
    Path(save_folder).mkdir(exist_ok=True)

    try:
        # Recevoir les métadonnées (nom du fichier et taille)
        meta = conn.recv(BUFFER_SIZE).decode()
        file_name, file_size = meta.split("||")
        file_size = int(file_size)
        print(f"[RECEIVER] Fichier proposé : {file_name} ({file_size} octets)")

        # Demander confirmation à l'utilisateur
        response = messagebox.askyesno(
            "Confirmation",
            f"Souhaitez-vous recevoir le fichier '{file_name}' ({file_size} octets) de {addr[0]} ?"
        )
        if not response:
            conn.send("REJECTED".encode())
            conn.close()
            print(f"[RECEIVER] Connexion refusée pour {file_name} de {addr[0]}")
            return False
        conn.send("OK".encode())

        # Recevoir le fichier
        file_path = os.path.join(save_folder, file_name)
        received = 0
        with open(file_path, "wb") as f, tqdm(
            total=file_size, unit="B", unit_scale=True, desc="Réception"
        ) as pbar:
            while received < file_size:
                data = conn.recv(BUFFER_SIZE)
                if not data:
                    break
                f.write(data)
                received += len(data)
                pbar.update(len(data))

        conn.close()
        if received == file_size:
            print(f"[RECEIVER] Fichier {file_name} reçu avec succès")
            messagebox.showinfo("Succès", f"Fichier {file_name} reçu et sauvegardé.")
            return True
        else:
            print(f"[RECEIVER] Fichier {file_name} reçu partiellement ({received}/{file_size} octets)")
            messagebox.showwarning("Attention", f"Fichier {file_name} reçu partiellement.")
            return False

    except socket.error as e:
        print(f"[ERROR] Erreur réseau pour {addr[0]} : {e}")
        messagebox.showerror("Erreur", f"Erreur réseau : {str(e)}")
        return False
    except ValueError as e:
        print(f"[ERROR] Erreur dans les métadonnées pour {addr[0]} : {e}")
        messagebox.showerror("Erreur", f"Erreur dans les métadonnées : {str(e)}")
        return False
    finally:
        if conn:
            conn.close()
