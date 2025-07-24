
import json
import customtkinter as ctk
from tkinter import filedialog, messagebox
from sender import send_file
from receiver import receive_file
import threading
import os


class FileSharerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("File Sharer")
        self.root.geometry("800x600")

        # Label principal
        self.label = ctk.CTkLabel(root, text="File Sharer", font=("Arial", 20))
        self.label.pack(pady=20)

        # Bouton Envoyer
        self.send_button = ctk.CTkButton(root, text="Envoyer un fichier", command=self.start_send)
        self.send_button.pack(pady=10)

        # Bouton Recevoir
        self.receive_button = ctk.CTkButton(root, text="Recevoir un fichier", command=self.start_receive)
        self.receive_button.pack(pady=10)

        # Champ pour entrer l'IP (pour l'envoi)
        self.ip_label = ctk.CTkLabel(root, text="Adresse IP de destination :")
        self.ip_label.pack(pady=5)
        self.ip_entry = ctk.CTkEntry(root, placeholder_text="Ex: 192.168.2.4")
        self.ip_entry.pack(pady=5)


    def start_send(self):
        # Ouvre une boîte de dialogue pour choisir un fichier
        file_path = filedialog.askopenfilename()
        if not file_path:
            return
        ip = self.ip_entry.get()
        if not ip:
            messagebox.showerror("[x] Erreur", "Veuillez entrer une adresse IP.")
            return

        # Lance l'envoi dans un thread séparé pour pas bloquer l'interface
        threading.Thread(target=send_file, args=(file_path, ip, 5001), daemon=True).start()
        messagebox.showinfo("[+] Succès", "Envoi du fichier démarré.")


    def start_receive(self):
        # Lance la réception dans un thread séparé
        threading.Thread(target=receive_file, args=(5001,), daemon=True).start()
        messagebox.showinfo("[+] Info", "Mode réception activé. En attente d'un fichier...")














































































"""# Charger l'IP par défaut depuis config.json
CONFIG_PATH = "config.json"
DEFAULT_IP = ""

if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, 'r') as f:
        config = json.load(f)
        DEFAULT_IP = config.get("last_ip", "")


def choose_and_send_file():
    ip = ip_entry.get().strip()
    if not ip:
        status_label.configure(text="[-] Entrez une adresse IP", text_color="red")
        return
    
    filepath = fd.askopenfilename()
    if not filepath:
        status_label.configure(text="[-] Aucune sélection", text_color="orange")
        return

    try:
        send_file(ip, 5001, filepath)
        status_label.configure(text="[+] Fichier envoyé", text_color="green")
        
        # Sauvegarder l'IP utilisée
        with open(CONFIG_PATH, 'w') as f:
            json.dump({"last_ip": ip}, f)
    except Exception as e:
        status_label.configure(text=f"[x] Erreur : {e}", text_color="red")


# Initialisation GUI
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

root = ctk.CTk()
root.title("File Sender")
root.geometry("800x500")

# Widgets
title_label = ctk.CTkLabel(root, text="Envoi de Fichier", font=("Arial", 20))
title_label.pack(pady=10)

ip_entry = ctk.CTkEntry(root, placeholder_text="Adresse IP du destinataire")
ip_entry.pack(pady=10)
ip_entry.insert(0, DEFAULT_IP)

send_btn = ctk.CTkButton(root, text="Choisir et envoyer un fichier", command=choose_and_send_file)
send_btn.pack(pady=20)

status_label = ctk.CTkLabel(root, text="")
status_label.pack(pady=10)

# Lancer interface
root.mainloop()"""