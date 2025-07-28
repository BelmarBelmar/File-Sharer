import customtkinter as ctk
from tkinter import filedialog, messagebox, Toplevel
from sender import send_file
from receiver import receive_file, ReceptionCancelled
from utils.utils import load_history
from network import scan_network
import threading
import os
import traceback
from threading import Event
import time
import re
import socket

class FileSharerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("File Sharer")
        self.root.geometry("800x600")
        self.root.resizable(False, False)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Référence au thread de réception et drapeau d'annulation
        self.receive_thread = None
        self.cancel_flag = Event()
        self.is_receiving = False  # Nouvel attribut pour suivre l'état
        self.selected_path = None  # Attribut pour stocker le chemin sélectionné
        self.file_path = None  # Attribut pour le chemin du fichier/dossier à envoyer
        self.ip_placeholder = "Entrez une IP (ex. 192.168.1.1)..."  # Placeholder mis à jour

        # Label principal
        self.label = ctk.CTkLabel(
            root,
            text="File Sharer",
            font=("Arial", 24, "bold"),
            text_color="#FFFFFF"
        )
        self.label.pack(pady=30)

        # Frame pour les boutons
        self.button_frame = ctk.CTkFrame(root, fg_color="transparent")
        self.button_frame.pack(pady=(100, 10))  # Marge supérieure augmentée

        # Bouton Envoyer
        self.send_button = ctk.CTkButton(
            self.button_frame,
            text="⬆ Envoyer",
            command=self.prepare_send,
            fg_color="#1E90FF",
            hover_color="#4682B4",
            font=("Arial", 16),
            width=150
        )
        self.send_button.pack(side="left", padx=5)

        # Bouton Recevoir
        self.receive_button = ctk.CTkButton(
            self.button_frame,
            text="⬇ Recevoir",
            command=self.start_receive,
            fg_color="#1E90FF",
            hover_color="#4682B4",
            font=("Arial", 16),
            width=150
        )
        self.receive_button.pack(side="left", padx=5)

        # Bouton Historique
        self.history_button = ctk.CTkButton(
            self.button_frame,
            text="Historique",
            command=self.show_history,
            fg_color="#FFD700",
            hover_color="#FFA500",
            font=("Arial", 16),
            width=150
        )
        self.history_button.pack(side="left", padx=5)

        # Bouton Scanner
        self.scan_button = ctk.CTkButton(
            self.button_frame,
            text="Scanner",
            command=self.scan_networks,
            fg_color="#FFD700",
            hover_color="#FFA500",
            font=("Arial", 16),
            width=150
        )
        self.scan_button.pack(side="left", padx=5)

        # Label d'état
        self.status_label = ctk.CTkLabel(
            root,
            text="Choisissez une action",
            font=("Arial", 14),
            text_color="#87CEEB"
        )
        self.status_label.pack(pady=20)

        # Widgets pour l'envoi
        self.ip_label = ctk.CTkLabel(
            root,
            text="Adresse IP de destination :",
            font=("Arial", 14),
            text_color="#FFFFFF"
        )
        self.ip_dropdown = ctk.CTkComboBox(
            root,
            values=[self.ip_placeholder],  # Initialiser avec le placeholder
            font=("Arial", 14),
            width=250,
            fg_color="#1E90FF",
            button_color="#4682B4",
            dropdown_fg_color="#2B2B2B"
        )
        self.ip_dropdown.set(self.ip_placeholder)  # Définir le placeholder comme valeur initiale
        self.ip_dropdown.bind("<FocusIn>", self._clear_placeholder)  # Effacer le placeholder quand cliqué
        self.confirm_send_button = ctk.CTkButton(
            root,
            text="Confirmer l'envoi",
            command=self.start_send,
            fg_color="#1E90FF",
            hover_color="#4682B4",
            font=("Arial", 14),
            width=200
        )
        self.cancel_button = ctk.CTkButton(
            root,
            text="Annuler",
            command=self.reset_interface,
            fg_color="#FF4500",
            hover_color="#FF6347",
            font=("Arial", 14),
            width=200
        )
        # Nouveau bouton Annuler pour réception
        self.cancel_receive_button = ctk.CTkButton(
            root,
            text="Annuler la réception",
            command=self.cancel_receive,
            fg_color="#FF4500",
            hover_color="#FF6347",
            font=("Arial", 14),
            width=200
        )
        # Nouveaux boutons pour choisir fichier ou dossier
        self.send_file_button = ctk.CTkButton(
            root,
            text="Envoyer un fichier",
            command=self.select_file,
            fg_color="#1E90FF",
            hover_color="#4682B4",
            font=("Arial", 14),
            width=200
        )
        self.send_folder_button = ctk.CTkButton(
            root,
            text="Envoyer un dossier",
            command=self.select_folder,
            fg_color="#1E90FF",
            hover_color="#4682B4",
            font=("Arial", 14),
            width=200
        )
        # Label pour afficher le chemin sélectionné
        self.selected_label = ctk.CTkLabel(
            root,
            text="",
            font=("Arial", 12),
            text_color="#FFFFFF"
        )

    def _clear_placeholder(self, event):
        if self.ip_dropdown.get() == self.ip_placeholder:
            self.ip_dropdown.set("")  # Effacer le placeholder quand l'utilisateur clique

    def prepare_send(self):
        self.update_status("Choisissez de envoyer un fichier ou un dossier...", "#87CEEB")
        self.button_frame.pack_forget()
        self.send_file_button.pack(pady=10)
        self.send_folder_button.pack(pady=10)

    def select_file(self):
        self.send_file_button.pack_forget()
        self.send_folder_button.pack_forget()
        file_path = filedialog.askopenfilename(
            title="Choisir un fichier",
            initialdir=os.path.expanduser("~/Desktop"),
            filetypes=[("Tous les fichiers", "*.*"), ("Documents", "*.pdf *.docx *.txt"), ("Images", "*.jpg *.png")]
        )
        if not file_path:
            self.reset_interface()
            return
        self.selected_path = file_path
        self.file_path = file_path  # Mettre à jour file_path pour les fichiers
        self.selected_label.configure(text=f"Sélectionné : {os.path.basename(file_path)}")
        self.selected_label.pack(pady=5)
        self._auto_scan_network()  # Lancer le scan automatiquement
        self.ip_label.pack(pady=10)
        self.ip_dropdown.pack(pady=10)
        self.confirm_send_button.pack(pady=10)
        self.cancel_button.pack(pady=10)
        self.update_status("Choisissez un appareil ou scannez le réseau...", "#87CEEB")

    def select_folder(self):
        self.send_file_button.pack_forget()
        self.send_folder_button.pack_forget()
        folder_path = filedialog.askdirectory(
            title="Choisir un dossier",
            initialdir=os.path.expanduser("~/Desktop")
        )
        if not folder_path:
            self.reset_interface()
            return
        self.selected_path = folder_path
        # Compresser le dossier en ZIP temporairement
        import zipfile
        temp_zip = os.path.join(os.path.dirname(folder_path), "temp_send.zip")
        with zipfile.ZipFile(temp_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, os.path.relpath(file_path, os.path.dirname(folder_path)))
        self.file_path = temp_zip  # Utiliser le ZIP comme fichier à envoyer
        self.selected_label.configure(text=f"Sélectionné : {os.path.basename(folder_path)}")
        self.selected_label.pack(pady=5)
        self._auto_scan_network()  # Lancer le scan automatiquement
        self.ip_label.pack(pady=10)
        self.ip_dropdown.pack(pady=10)
        self.confirm_send_button.pack(pady=10)
        self.cancel_button.pack(pady=10)
        self.update_status("Choisissez un appareil ou scannez le réseau...", "#87CEEB")

    def _auto_scan_network(self):
        self.update_status("Scanning réseau automatiquement...", "#87CEEB")
        self.scan_button.configure(state="disabled")  # Désactiver le bouton pendant le scan auto
        threading.Thread(target=self._perform_auto_scan, daemon=True).start()

    def _perform_auto_scan(self):
        try:
            active_devices = scan_network(port=5001)
            if not isinstance(active_devices, list):
                raise ValueError("Les appareils renvoyés ne sont pas une liste valide")
            self.root.after(0, lambda: self._update_scan_results(active_devices))
        except Exception as e:
            error_msg = f"Erreur de scan : {str(e)}\nDétail : {traceback.format_exc()}"
            self.root.after(0, lambda: self.update_status(error_msg, "#FF4500"))
        finally:
            self.root.after(0, lambda: self.scan_button.configure(state="normal"))

    def scan_networks(self):
        self.update_status("Scanning réseau manuellement...", "#87CEEB")
        self.scan_button.configure(state="disabled")  # Désactiver le bouton pendant le scan manuel
        threading.Thread(target=self._perform_auto_scan, daemon=True).start()

    def _update_scan_results(self, active_devices):
        if active_devices and all(isinstance(device, tuple) and len(device) == 2 for device in active_devices):
            device_strings = [f"{device[1]}:{device[0]}" for device in active_devices]  # Format "IP:nom"
            self.ip_dropdown.configure(values=device_strings)
            if self.ip_dropdown.get() == self.ip_placeholder:
                self.ip_dropdown.set("")  # Effacer le placeholder si aucune IP n'est entrée
            self.update_status(f"{len(active_devices)} appareil(s) détecté(s)", "#32CD32")
        else:
            self.ip_dropdown.configure(values=[self.ip_placeholder])
            self.ip_dropdown.set(self.ip_placeholder)
            self.update_status("Aucun appareil trouvé ou erreur de détection", "#FF4500")

    def start_send(self):
        ip = self.ip_dropdown.get()
        if not ip or ip == self.ip_placeholder:
            messagebox.showerror("Erreur", "Veuillez entrer ou sélectionner une adresse IP.")
            self.update_status("Erreur : Aucune IP sélectionnée", "#FF4500")
            return

        # Extraire l'IP de "IP:nom" si sélectionnée, sinon valider comme IP
        if ':' in ip:
            ip = ip.split(':')[0]  # Prendre seulement l'IP
        else:
            # Validation de l'IP
            ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
            if not re.match(ip_pattern, ip):
                messagebox.showerror("Erreur", "Veuillez entrer une adresse IP valide.")
                self.update_status("Erreur : Entrée non valide, une IP est requise", "#FF4500")
                return
            octets = ip.split('.')
            if not all(0 <= int(octet) <= 255 for octet in octets):
                messagebox.showerror("Erreur", "Chaque octet doit être entre 0 et 255.")
                self.update_status("Erreur : IP invalide", "#FF4500")
                return

        self.update_status("Envoi en cours...", "#87CEEB")
        if self.file_path is None:
            messagebox.showerror("Erreur", "Aucun fichier ou dossier sélectionné.")
            self.update_status("Erreur : Aucun fichier/dossier sélectionné", "#FF4500")
            return
        threading.Thread(target=self._send_file_thread, args=(self.file_path, ip, 5001), daemon=True).start()

    def _send_file_thread(self, file_path, ip, port):
        try:
            send_file(file_path, ip, port)
            # Nettoyer le fichier ZIP temporaire si c'était un dossier
            if file_path.endswith(".zip") and os.path.exists(file_path):
                os.remove(file_path)
            self.root.after(0, lambda: self.update_status("Fichier envoyé avec succès !", "#32CD32"))
        except Exception as e:
            self.root.after(0, lambda: self.update_status(f"Erreur : {str(e)}", "#FF4500"))
        finally:
            self.root.after(2000, self.reset_interface)

    def start_receive(self):
        if self.is_receiving:
            self.update_status("Une réception est déjà en cours. Attendez ou annulez.", "#FF4500")
            return
        self.button_frame.pack_forget()
        self.ip_label.pack_forget()
        self.ip_dropdown.pack_forget()
        self.confirm_send_button.pack_forget()
        self.cancel_button.pack_forget()
        self.update_status("En attente d'un fichier...", "#87CEEB")
        self.cancel_flag.clear()  # Réinitialiser le drapeau
        self.cancel_receive_button.pack(pady=10)  # Afficher le bouton Annuler
        self.is_receiving = True
        # Ajouter une tentative de rebinding si le port est occupé
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                self.receive_thread = threading.Thread(target=self._receive_file_thread, args=(5001, self.cancel_flag), daemon=True)
                self.receive_thread.start()
                break
            except OSError as e:
                if "Address already in use" in str(e) or "[Errno 98]" in str(e):
                    if attempt < max_attempts - 1:
                        self.update_status(f"Port occupé, réessai {attempt + 1}/{max_attempts}...", "#FFA500")
                        time.sleep(2)  # Attendre 2 secondes avant de réessayer
                    else:
                        self.update_status("Port occupé après plusieurs tentatives. Relancez l'application.", "#FF4500")
                        self.is_receiving = False
                        self.reset_interface()
                        return
                else:
                    raise

    def cancel_receive(self):
        if self.receive_thread and self.receive_thread.is_alive():
            self.cancel_flag.set()  # Définir le drapeau d'annulation
            self.update_status("Annulation en cours...", "#FFA500")
            self.cancel_receive_button.configure(state="disabled")  # Désactiver pendant l'annulation
            self.receive_thread.join(timeout=2)  # Attendre un maximum de 2 secondes
            if self.receive_thread.is_alive():
                self.update_status("Annulation forcée, veuillez relancer.", "#FF4500")
            else:
                self.update_status("Réception annulée.", "#32CD32")
            self.is_receiving = False
            self.reset_interface()

    def _receive_file_thread(self, port, cancel_flag):
        try:
            receive_file(port, cancel_flag)
            self.root.after(0, lambda: self.update_status("Fichier reçu avec succès !", "#32CD32"))
        except ReceptionCancelled:
            self.root.after(0, lambda: self.update_status("Réception annulée.", "#32CD32"))
        except Exception as e:
            self.root.after(0, lambda: self.update_status(f"Erreur : {str(e)}", "#FF4500"))
        finally:
            self.is_receiving = False
            self.root.after(0, self.reset_interface)

    def reset_interface(self):
        self.ip_label.pack_forget()
        self.ip_dropdown.pack_forget()
        self.confirm_send_button.pack_forget()
        self.cancel_button.pack_forget()
        self.cancel_receive_button.pack_forget()
        self.send_file_button.pack_forget()
        self.send_folder_button.pack_forget()
        self.selected_label.pack_forget()
        self.button_frame.pack(pady=(100, 10))  # Réappliquer la marge supérieure
        self.update_status("Choisissez une action", "#87CEEB")

    def show_history(self):
        history_window = ctk.CTkToplevel(self.root)
        history_window.title("Historique des transferts")
        history_window.geometry("500x300")
        history_window.resizable(False, False)

        history_text = ctk.CTkTextbox(
            history_window,
            font=("Arial", 12),
            width=450,
            height=250,
            fg_color="#2B2B2B",
            text_color="#FFFFFF"
        )
        history_text.pack(pady=10, padx=10)

        history = load_history()
        if not history:
            history_text.insert("end", "Aucun transfert dans l'historique.")
        else:
            for entry in history:
                text = f"{entry['timestamp']} - {entry['operation'].capitalize()} : {entry['file_name']} ({entry['ip']})\n"
                history_text.insert("end", text)
        history_text.configure(state="disabled")

    def update_status(self, message, color):
        self.status_label.configure(text=message, text_color=color)