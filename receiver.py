import socket, os
from pathlib import Path
from tkinter import messagebox


def receive_file(port):
    try:
        # Création du socket serveur
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("", port))
        sock.listen(1)

        # Attendre une connexion
        conn, addr = sock.accept()
        ip = addr[0]

        # Recevoir le nom du fichier
        file_name = conn.recv(1024).decode()

        # Affichage d' une confirmation
        response = messagebox.askyesno(
            "Confirmation",
            f"Souhaitez-vous recevoir le fichier '{file_name}' de {ip} ?"
        )
        if not response:
            conn.send("NO".encode())
            conn.close()
            sock.close()
            return

        # Confirmation de la réception
        conn.send("OK".encode())

        # Créer le dossier received_files s'il n'existe pas
        os.makedirs("received_files", exist_ok=True)
        file_path = os.path.join("received_files", file_name)

        # Recevoir le fichier
        with open(file_path, "wb") as f:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                f.write(data)

        conn.close()
        sock.close()
        messagebox.showinfo("[+] Succès", f"Fichier {file_name} reçu et sauvegardé.")
    except Exception as e:
        messagebox.showerror("[x] Erreur", f"Erreur lors de la réception : {str(e)}")































"""RECEIVE_PORT = 5001
BUFFER_SIZE = 4096
SAVE_FOLDER = "received_files"


def start_receiver(ask_user_confirmation_callback):
    Path(SAVE_FOLDER).mkdir(exist_ok=True)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind(('', RECEIVE_PORT))
        server_socket.listen(1)
        print(f"[RECEIVER] En écoute sur le port {RECEIVE_PORT}...")

        while True:
            conn, addr = server_socket.accept()
            with conn:
                print(f"[RECEIVER] Connexion de {addr[0]}:{addr[1]}")
                
                # Récpetion des métadonnées du fichier
                meta = conn.recv(BUFFER_SIZE).decode()
                file_name, file_size = meta.split("||")
                file_size = int(file_size)
                print(f"[RECEIVER] Fichier proposé: {file_name} ({file_size} octets)")

                # Appel à la fonction pour demander au user s'il accepte
                if not ask_user_confirmation_callback(addr[0], file_name, file_size):
                    print("[RECEIVER] L'utilisateur a refusé le fichier.")
                    conn.sendall(b"REJECTED")
                    continue
                else:
                    conn.sendall(b"ACCEPTED")

                # Réception proprement dite
                with open(os.path.join(SAVE_FOLDER, file_name), 'wb') as f:
                    received = 0
                    while received < file_size:
                        data = conn.recv(BUFFER_SIZE)
                        if not data:
                            break
                        f.write(data)
                        received += len(data)
                        print(f"[RECEIVER] Reçu {received}/{file_size} octets", end='\r')

                print(f"\n[RECEIVER] Réception terminée: {file_name}")"""