import socket
import os
from pathlib import Path
from tkinter import messagebox
from tqdm import tqdm

# Constantes configurables
RECEIVE_PORT = 5001
BUFFER_SIZE = 4096
SAVE_FOLDER = "received_files"

def receive_file(port=RECEIVE_PORT, save_folder=SAVE_FOLDER):
    """
    Écoute sur un port donné et reçoit des fichiers, avec confirmation utilisateur.
    """
    # Créer le dossier de sauvegarde s'il n'existe pas
    Path(save_folder).mkdir(exist_ok=True)

    # Création du socket serveur
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(("", port))
        server_socket.listen(1)
        print(f"[RECEIVER] En écoute sur le port {port}...")
    except socket.error as e:
        print(f"[ERROR] Erreur lors de la création du socket : {e}")
        messagebox.showerror("[x] Erreur", f"Erreur lors de la création du socket : {str(e)}")
        return

    try:
        while True:  # Boucle pour accepter plusieurs connexions
            try:
                # Attendre une connexion
                conn, addr = server_socket.accept()
                print(f"[RECEIVER] Connexion de {addr[0]}:{addr[1]}")

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
                    continue
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
                    messagebox.showinfo("[+] Succès", f"Fichier {file_name} reçu et sauvegardé.")
                else:
                    print(f"[RECEIVER] Fichier {file_name} reçu partiellement ({received}/{file_size} octets)")
                    messagebox.showwarning("[!] Attention", f"Fichier {file_name} reçu partiellement.")

            except socket.error as e:
                print(f"[ERROR] Erreur réseau pour {addr[0]} : {e}")
                messagebox.showerror("[x] Erreur", f"Erreur réseau : {str(e)}")
            except ValueError as e:
                print(f"[ERROR] Erreur dans les métadonnées pour {addr[0]} : {e}")
                messagebox.showerror("[x] Erreur", f"Erreur dans les métadonnées : {str(e)}")
            except OSError as e:
                print(f"[ERROR] Erreur d'écriture du fichier {file_name} : {e}")
                messagebox.showerror("[x] Erreur", f"Erreur d'écriture du fichier : {str(e)}")

    except KeyboardInterrupt:
        print("[RECEIVER] Arrêt du serveur par l'utilisateur.")
    finally:
        server_socket.close()
        print("[RECEIVER] Socket fermé.")

if __name__ == "__main__":
    receive_file()