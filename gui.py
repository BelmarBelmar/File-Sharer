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
        self.ip_entry = ctk.CTkEntry(root, placeholder_text="192.168.x.x")
        self.ip_entry.pack(pady=5)

    def start_send(self):
        # Activer le champ IP pour l'envoi
        self.ip_entry.configure(state="normal")
        file_path = filedialog.askopenfilename()
        if not file_path:
            return
        ip = self.ip_entry.get()
        if not ip:
            messagebox.showerror("Erreur", "Veuillez entrer une adresse IP.")
            return

        # Lance l'envoi dans un thread séparé
        threading.Thread(target=send_file, args=(file_path, ip, 5001), daemon=True).start()
        messagebox.showinfo("Succès", "Envoi du fichier démarré.")

    def start_receive(self):
        # Désactiver le champ IP en mode réception
        self.ip_entry.configure(state="disabled")
        # Lance la réception dans un thread séparé
        threading.Thread(target=receive_file, args=(5001,), daemon=True).start()
        messagebox.showinfo("Info", "Mode réception activé. En attente d'un fichier...")
