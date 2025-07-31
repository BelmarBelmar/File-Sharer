import os
from pathlib import Path
import socket
from tkinter import messagebox
from tqdm import tqdm
from threading import Event

class ReceptionCancelled(Exception):
    pass

BUFFER_SIZE = 4096

def receive_file(port, cancel_flag):
    """
    Reçoit un fichier à partir d'une connexion sur le port spécifié.
    Retourne True si le fichier est reçu avec succès, False sinon.
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # Activer la réutilisation du port
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(("", port))
        server_socket.listen(5)
        print(f"[RÉCEPTEUR] En attente de connexion sur le port {port} sur toutes les interfaces...")

        while not cancel_flag.is_set():
            conn, addr = server_socket.accept()
            print(f"[RÉCEPTEUR] Nouvelle connexion acceptée de {addr}")

            # Résoudre le répertoire personnel
            home_dir = os.path.expanduser("~")

            # Détecter le dossier de téléchargement (Downloads ou Téléchargements)
            download_folders = ["Downloads", "Téléchargements"]
            save_folder_base = None
            for folder in download_folders:
                potential_folder = os.path.join(home_dir, folder)
                if os.path.isdir(potential_folder):
                    save_folder_base = potential_folder
                    break

            if save_folder_base is None:
                save_folder_base = home_dir  # Fallback au répertoire personnel

            # Chemin final avec sous-dossier files_shared
            save_folder = os.path.join(save_folder_base, "files_shared")
            # Créer le dossier et ses parents si nécessaire
            os.makedirs(save_folder, exist_ok=True)

            try:
                # Recevoir les métadonnées (nom du fichier, taille, et nom de l'utilisateur)
                meta = conn.recv(BUFFER_SIZE).decode()
                if "||" not in meta or meta.count("||") < 2:
                    conn.send("REJECTED".encode())
                    conn.close()
                    continue
                file_name, file_size, user_name = meta.split("||", 2)  # Sépare en 3 parties max
                file_size = int(file_size)
                print(f"[RÉCEPTEUR] Fichier proposé par {user_name} : {file_name} ({file_size} octets)")

                # Demander confirmation à l'utilisateur
                response = messagebox.askyesno(
                    "Confirmation",
                    f"Souhaitez-vous recevoir le fichier '{file_name}' ({file_size} octets) de {user_name} ({addr[0]}) ?"
                )
                if not response:
                    conn.send("REJECTED".encode())
                    conn.close()
                    print(f"[RÉCEPTEUR] Téléchargement refusé pour {file_name} de {user_name}")
                    continue
                conn.send("OK".encode())

                # Recevoir le fichier
                file_path = os.path.join(save_folder, file_name)
                received = 0
                with open(file_path, "wb") as f, tqdm(
                        total=file_size, unit="o", unit_scale=True, desc="Téléchargement en cours"
                ) as pbar:
                    while received < file_size:
                        data = conn.recv(BUFFER_SIZE)
                        if not data or cancel_flag.is_set():
                            break
                        f.write(data)
                        received += len(data)
                        pbar.update(len(data))

                if cancel_flag.is_set():
                    raise ReceptionCancelled("Téléchargement annulé par l'utilisateur")

                conn.close()
                if received == file_size:
                    print(f"[RÉCEPTEUR] Fichier {file_name} téléchargé avec succès de {user_name}")
                    messagebox.showinfo("Succès", f"Fichier {file_name} téléchargé et sauvegardé de {user_name}.")
                else:
                    print(f"[RÉCEPTEUR] Fichier {file_name} téléchargé partiellement ({received}/{file_size} octets) de {user_name}")
                    messagebox.showwarning("Attention", f"Fichier {file_name} téléchargé partiellement de {user_name}.")

            except socket.error as e:
                print(f"[ERREUR] Erreur réseau pour {addr[0]} : {e}")
                messagebox.showerror("Erreur", f"Erreur réseau : {str(e)}")
            except ReceptionCancelled as e:
                print(f"[RÉCEPTEUR] {str(e)}")
                if os.path.exists(file_path):
                    os.remove(file_path)
            except ValueError as e:
                print(f"[ERREUR] Erreur dans les métadonnées pour {addr[0]} : {e} - Données : {meta}")
                messagebox.showerror("Erreur", f"Erreur dans les métadonnées : {str(e)}")
                conn.send("REJECTED".encode())
                conn.close()
                continue
            finally:
                if 'conn' in locals() and conn:
                    conn.close()

    except KeyboardInterrupt:
        print("[RÉCEPTEUR] Arrêt du serveur par l'utilisateur.")
    except Exception as e:
        print(f"[ERREUR] Erreur : {e}")
    finally:
        server_socket.close()
        print("[RÉCEPTEUR] Socket fermé.")