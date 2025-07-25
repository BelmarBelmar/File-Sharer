
import socket
from tkinter import messagebox

def start_server(port=5001):
    """
    Ouvre un socket serveur sur le port donné et retourne une seule connexion.
    """
    server_socket = None
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(("", port))
        server_socket.listen(1)
        print(f"[SERVER] En écoute sur le port {port}...")

        conn, addr = server_socket.accept()
        print(f"[SERVER] Connexion de {addr[0]}:{addr[1]}")
        return server_socket, conn, addr

    except socket.error as e:
        print(f"[ERROR] Erreur lors de la création du socket : {e}")
        messagebox.showerror("[x] Erreur", f"Erreur lors de la création du socket : {str(e)}")
        return None, None, None
    except Exception as e:
        print(f"[ERROR] Erreur inattendue : {e}")
        messagebox.showerror("[x] Erreur", f"Erreur inattendue : {str(e)}")
        return None, None, None
    finally:
        if server_socket:
            server_socket.close()
            print("[SERVER] Socket fermé.")
