'''

import socket
from tkinter import messagebox

def start_server(ip="0.0.0.0", port=5001):

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(("", port))
        server_socket.listen(5)  # Queue de 5 connexions en attente
        print(f"[SERVER] En écoute sur le port {port}...")

        while True:
            conn, addr = server_socket.accept()
            print(f"[SERVER] Connexion de {addr[0]}:{addr[1]}")
            # Gère la connexion (exemple minimal, à adapter selon tes besoins)
            conn.close()  # Ferme la connexion client, mais garde le serveur actif

    except socket.error as e:
        print(f"[ERROR] Erreur lors de la création du socket : {e}")
        messagebox.showerror("[x] Erreur", f"Erreur lors de la création du socket : {str(e)}")
    except KeyboardInterrupt:
        print("[SERVER] Arrêt du serveur par l'utilisateur.")
    except Exception as e:
        print(f"[ERROR] Erreur inattendue : {e}")
        messagebox.showerror("[x] Erreur", f"Erreur inattendue : {str(e)}")
    finally:
        if server_socket:
            server_socket.close()
            print("[SERVER] Socket fermé.")

if __name__ == "__main__":
    start_server()
'''
