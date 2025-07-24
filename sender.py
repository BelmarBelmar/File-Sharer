import socket
import os
from tkinter import messagebox

def send_file(file_path, ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((ip, port))

        # Envoyer le nom du fichier
        file_name = os.path.basename(file_path)
        sock.send(file_name.encode())

        # Attendre confirmation
        response = sock.recv(1024).decode()
        if response != "OK":
            messagebox.showerror("Erreur", "La réception a été refusée.")
            return

        # Envoyer le fichier
        with open(file_path, "rb") as f:
            while chunk := f.read(1024):
                sock.send(chunk)

        messagebox.showinfo("Succès", f"Fichier {file_name} envoyé avec succès.")
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors de l'envoi : {str(e)}")
    finally:
        sock.close()  # ferme le socket
