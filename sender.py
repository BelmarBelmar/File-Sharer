import os
import socket
from tkinter import messagebox


def send_file(file_path, ip, port):
    try:
        # Création du socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, port))

        # Envoyer le nom du fichier
        file_name = os.path.basename(file_path)
        sock.send(file_name.encode())

        # Attendre la confirmation
        response = sock.recv(1024).decode()
        if response != "OK":
            sock.close()
            messagebox.showerror("[x] Erreur", "La réception a été refusée.")
            return

        # Envoie du fichier
        with open(file_path, "rb") as f:
            while chunk := f.read(1024):
                sock.send(chunk)

        sock.close()
        messagebox.showinfo("[+] Succès", f"Fichier {file_name} envoyé avec succès.")
    except Exception as e:
        messagebox.showerror("[x] Erreur", f"Erreur lors de l'envoi : {str(e)}")




















        

"""def send_file(ip, port, file_path):
    try:
        if not os.path.exist(file_path):
            print("Le fichier n'a pas été trouvé")
            return False
        
        filesize = os.path.getsize(file_path)
        filename = os.path.basename(file_path)

        # Création du socket client
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            print(f"[+] Connexion à {ip}:{port}...")
            s.connect((ip, port))
            print("[+] Connecté")
            s.sendall(f"{filename}|{filesize}".encode())

        # Attente d'un ACK du récepteur
        ack = s.recv(1024).decode()
        if ack != "OK":
            print("[-] Le récepteur a refusé le fichier.")
            return False

        # Envoi du fichier
        with open(file_path, "rb") as f:
            while chunk := f.read(4096):
                s.sendall(chunk)


        print("[+] Fichier envoyé avec succès")
        return True
    except Exception as e:
        print(f"[x] Erreur durant l'envoi: {e}")
        return False
"""