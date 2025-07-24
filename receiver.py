import socket
import os
from tkinter import messagebox

def receive_file(port):
    try:
        # Création du socket serveur
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # pour réutiliser le port
        sock.bind(("", port))
        sock.listen(1)

        # Attendre une connexion
        conn, addr = sock.accept()
        ip = addr[0]

        # Recevoir le nom du fichier
        file_name = conn.recv(1024).decode()

        # Afficher une confirmation
        response = messagebox.askyesno(
            "Confirmation",
            f"Souhaitez-vous recevoir le fichier '{file_name}' de {ip} ?"
        )
        if not response:
            conn.send("NO".encode())
            conn.close()
            sock.close()
            return

        # Confirmer la réception
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
        messagebox.showinfo("Succès", f"Fichier {file_name} reçu et sauvegardé.")
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors de la réception : {str(e)}")
    finally:
        sock.close()  # Assure que le socket est fermé même en cas d'erreur
