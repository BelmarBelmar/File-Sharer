import os
from pathlib import Path
import socket
from tkinter import messagebox, Tk, filedialog
from tqdm import tqdm
from threading import Event

CONFIG_FILE = "user_config.txt"

class ReceptionCancelled(Exception):
    pass

BUFFER_SIZE = 4096

def get_user_name():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return f.read().strip()
    else:
        user_name = input("Entrez votre nom (sauvegardé pour les prochaines utilisations) : ")
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            f.write(user_name)
        return user_name

def receive_file(port, cancel_flag, update_callback=None, save_folder=None):
    """
    Reçoit un fichier à partir d'une connexion sur le port spécifié.
    Retourne True si le fichier est reçu avec succès, False sinon.
    """
    user_name = get_user_name()
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.settimeout(1.0)  # Timeout pour permettre une vérification régulière
        server_socket.bind(("", port))
        server_socket.listen(5)
        print(f"[RÉCEPTEUR] En attente de connexion sur le port {port} sur toutes les interfaces...")

        while not cancel_flag.is_set():
            try:
                conn, addr = server_socket.accept()
                print(f"[RÉCEPTEUR] Nouvelle connexion acceptée de {addr}")

                # Utiliser le dossier personnalisé si fourni, sinon proposer un dossier par défaut
                if save_folder and os.path.isdir(save_folder):
                    save_folder_base = save_folder
                else:
                    home_dir = os.path.expanduser("~")
                    download_folders = ["Downloads", "Téléchargements"]
                    save_folder_base = None
                    for folder in download_folders:
                        potential_folder = os.path.join(home_dir, folder)
                        if os.path.isdir(potential_folder):
                            save_folder_base = potential_folder
                            break
                    if save_folder_base is None:
                        save_folder_base = home_dir
                    save_folder_base = os.path.join(save_folder_base, "files_shared")
                    os.makedirs(save_folder_base, exist_ok=True)

                try:
                    meta = conn.recv(BUFFER_SIZE).decode()
                    if "||" not in meta or meta.count("||") < 2:
                        conn.send("REJECTED".encode())
                        conn.close()
                        continue
                    file_name, file_size, sender_name = meta.split("||", 2)
                    file_size = int(file_size)
                    print(f"[RÉCEPTEUR] Fichier proposé par {sender_name} : {file_name} ({file_size} octets)")

                    response = messagebox.askyesno(
                        "Confirmation",
                        f"Souhaitez-vous recevoir le fichier '{file_name}' ({file_size} octets) de {sender_name} ?"
                    )
                    if not response:
                        conn.send("REJECTED".encode())
                        conn.close()
                        print(f"[RÉCEPTEUR] Téléchargement refusé pour {file_name} de {sender_name}")
                        continue
                    conn.send("OK".encode())

                    file_path = os.path.join(save_folder_base, file_name)
                    received = 0
                    with open(file_path, "wb") as f, tqdm(
                            total=file_size, unit="o", unit_scale=True, desc="Téléchargement en cours"
                    ) as pbar:
                        while received < file_size:
                            if cancel_flag.is_set():
                                raise ReceptionCancelled("Téléchargement annulé par l'utilisateur")
                            data = conn.recv(BUFFER_SIZE)
                            if not data:
                                break
                            f.write(data)
                            received += len(data)
                            pbar.update(len(data))
                            if update_callback:
                                percentage = (received / file_size) * 100
                                update_callback(percentage)

                    if cancel_flag.is_set():
                        raise ReceptionCancelled("Téléchargement annulé par l'utilisateur")

                    conn.close()
                    if received == file_size:
                        print(f"[RÉCEPTEUR] Fichier {file_name} téléchargé avec succès de {sender_name}")
                        messagebox.showinfo("Succès", f"Fichier {file_name} téléchargé et sauvegardé dans {save_folder_base}.")
                    else:
                        print(f"[RÉCEPTEUR] Fichier {file_name} téléchargé partiellement ({received}/{file_size} octets) de {sender_name}")
                        messagebox.showwarning("Attention", f"Fichier {file_name} téléchargé partiellement.")

                except socket.error as e:
                    print(f"[ERREUR] Erreur réseau pour {addr[0]} : {e}")
                    messagebox.showerror("Erreur", f"Erreur réseau : {str(e)}")
                except ReceptionCancelled as e:
                    print(f"[RÉCEPTEUR] {str(e)}")
                    if os.path.exists(file_path):
                        os.remove(file_path)
                except ValueError as e:
                    print(f"[ERREUR] Erreur dans les métadonnées pour {addr[0]} : {e} - Données reçues : {meta}")
                    messagebox.showerror("Erreur", f"Erreur dans les métadonnées : {str(e)}")
                    conn.send("REJECTED".encode())
                    conn.close()
                    continue
                finally:
                    if 'conn' in locals() and conn:
                        conn.close()

            except socket.timeout:
                continue  # Revenir au début de la boucle pour vérifier cancel_flag
            except socket.error as e:
                if not cancel_flag.is_set():
                    print(f"[ERREUR] Erreur réseau : {e}")
                break

    except KeyboardInterrupt:
        print("[RÉCEPTEUR] Arrêt du serveur par l'utilisateur.")
    except Exception as e:
        print(f"[ERREUR] Erreur : {e}")
    finally:
        server_socket.close()
        print("[RÉCEPTEUR] Socket fermé.")