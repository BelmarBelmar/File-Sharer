import os
from tkinter import filedialog, messagebox, Toplevel
import customtkinter as ctk
from sender import send_file
from receiver import receive_file, ReceptionCancelled
from utils.utils import load_history
from network import scan_network
import threading
import traceback
from threading import Event
import time
import re
import socket
import subprocess

CONFIG_FILE = "user_config.txt"


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
        self.is_receiving = False
        self.selected_path = None
        self.file_path = None
        self.ip_placeholder = "Choisir un destinataire..."

        # Nouvel attribut pour le nom de l'utilisateur et la map nom-IP
        self.user_name = None
        self.ip_name_map = {}  # Dictionnaire {nom: IP}
        self.local_ip = self.get_local_ip()

        # Initialisation des éléments d'interface
        self.label = ctk.CTkLabel(
            self.root, text="File Sharer", font=("Arial", 24, "bold"), text_color="#FFFFFF"
        )
        self.label.pack(pady=30)

        self.button_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.button_frame.pack(pady=(100, 10))

        self.send_button = ctk.CTkButton(
            self.button_frame, text="⬆ Envoyer", command=self.prepare_send,
            fg_color="#1E90FF", hover_color="#4682B4", font=("Arial", 16), width=150
        )
        self.send_button.pack(side="left", padx=5)

        self.receive_button = ctk.CTkButton(
            self.button_frame, text="⬇ Recevoir", command=self.start_receive,
            fg_color="#1E90FF", hover_color="#4682B4", font=("Arial", 16), width=150
        )
        self.receive_button.pack(side="left", padx=5)

        self.history_button = ctk.CTkButton(
            self.button_frame, text="Historique", command=self.show_history,
            fg_color="#FFD700", hover_color="#FFA500", font=("Arial", 16), width=150
        )
        self.history_button.pack(side="left", padx=5)

        self.scan_button = ctk.CTkButton(
            self.button_frame, text="Scanner", command=self.scan_networks,
            fg_color="#FFD700", hover_color="#FFA500", font=("Arial", 16), width=150
        )
        self.scan_button.pack(side="left", padx=5)

        self.change_name_button = ctk.CTkButton(
            self.button_frame, text="Changer de nom", command=self.change_name,
            fg_color="#FFD700", hover_color="#FFA500", font=("Arial", 16), width=150
        )
        self.change_name_button.pack(side="left", padx=5)

        self.status_label = ctk.CTkLabel(
            self.root, text="Choisissez une action", font=("Arial", 14), text_color="#87CEEB"
        )
        self.status_label.pack(pady=20)

        # Label de progression masqué par défaut
        self.progress_label = ctk.CTkLabel(
            self.root, text="Progression : 0%", font=("Arial", 14), text_color="#87CEEB"
        )
        # Ne pas packer ici, sera affiché uniquement pendant l'envoi ou la réception

        self.ip_label = ctk.CTkLabel(self.root, text="Destinataire :", font=("Arial", 14), text_color="#FFFFFF")
        self.ip_dropdown = ctk.CTkComboBox(
            self.root, values=[self.ip_placeholder], font=("Arial", 14), width=250,
            fg_color="#1E90FF", button_color="#4682B4", dropdown_fg_color="#2B2B2B"
        )
        self.ip_dropdown.set(self.ip_placeholder)
        self.ip_dropdown.bind("<FocusIn>", self._clear_placeholder)
        self.confirm_send_button = ctk.CTkButton(
            self.root, text="Confirmer l'envoi", command=self.start_send,
            fg_color="#1E90FF", hover_color="#4682B4", font=("Arial", 14), width=200
        )
        self.cancel_button = ctk.CTkButton(
            self.root, text="Annuler", command=self.reset_interface,
            fg_color="#FF4500", hover_color="#FF6347", font=("Arial", 14), width=200
        )
        self.cancel_receive_button = ctk.CTkButton(
            self.root, text="Annuler la réception", command=self.cancel_receive,
            fg_color="#FF4500", hover_color="#FF6347", font=("Arial", 14), width=200
        )
        self.send_file_button = ctk.CTkButton(
            self.root, text="Envoyer un fichier", command=self.select_file,
            fg_color="#1E90FF", hover_color="#4682B4", font=("Arial", 14), width=200
        )
        self.send_folder_button = ctk.CTkButton(
            self.root, text="Envoyer un dossier", command=self.select_folder,
            fg_color="#1E90FF", hover_color="#4682B4", font=("Arial", 14), width=200
        )
        self.back_button = ctk.CTkButton(
            self.root, text="Retour", command=self.reset_interface,
            fg_color="#FFD700", hover_color="#FFA500", font=("Arial", 14), width=200
        )
        self.selected_label = ctk.CTkLabel(self.root, text="", font=("Arial", 12), text_color="#FFFFFF")

        # Lancer le serveur socket en arrière-plan
        self.server_thread = threading.Thread(target=self.run_socket_server, daemon=True)
        self.server_thread.start()

        # Charger ou définir le nom au démarrage
        self.load_or_set_user_name()

    def load_or_set_user_name(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                self.user_name = f.read().strip()
        else:
            self.name_window = ctk.CTkToplevel(self.root)
            self.name_window.title("Définir votre nom")
            self.name_window.geometry("300x150")
            default_name = f"User_{self.local_ip.split('.')[-1]}"
            ctk.CTkLabel(self.name_window,
                         text="Entrez votre nom (sauvegardé pour les prochaines utilisations) :").pack(pady=5)
            self.name_entry = ctk.CTkEntry(self.name_window, width=200)
            self.name_entry.insert(0, default_name)
            self.name_entry.pack(pady=10)
            ctk.CTkButton(self.name_window, text="Valider", command=self._save_name).pack(pady=10)
            self.name_window.grab_set()
            self.root.wait_window(self.name_window)
        self.ip_name_map[self.user_name] = self.local_ip
        self.broadcast_name()

    def _save_name(self):
        base_name = self.name_entry.get().strip()
        if not base_name:
            messagebox.showwarning("Attention", "Veuillez entrer un nom !")
            return
        self.user_name = base_name
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            f.write(self.user_name)
        self.name_window.destroy()
        self.button_frame.pack(pady=(100, 10))

    def change_name(self):
        self.name_window = ctk.CTkToplevel(self.root)
        self.name_window.title("Changer votre nom")
        self.name_window.geometry("300x150")
        ctk.CTkLabel(self.name_window, text="Entrez un nouveau nom :").pack(pady=5)
        name_entry = ctk.CTkEntry(self.name_window, width=200)
        name_entry.insert(0, self.user_name or f"User_{self.local_ip.split('.')[-1]}")
        name_entry.pack(pady=10)
        ctk.CTkButton(self.name_window, text="Valider", command=lambda: self._update_name(name_entry.get())).pack(
            pady=10)
        self.name_window.grab_set()
        self.root.wait_window(self.name_window)

    def _update_name(self, new_name):
        if not new_name.strip():
            messagebox.showwarning("Attention", "Veuillez entrer un nom !")
            return
        self.user_name = new_name.strip()
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            f.write(self.user_name)
        self.ip_name_map[self.user_name] = self.local_ip
        self.broadcast_name()
        self.name_window.destroy()
        messagebox.showinfo("Succès", f"Nom mis à jour : {self.user_name}")

    def _clear_placeholder(self, event):
        if self.ip_dropdown.get() == self.ip_placeholder:
            self.ip_dropdown.set("")

    def prepare_send(self):
        self.update_status("Choisissez de envoyer un fichier ou un dossier...", "#87CEEB")
        self.button_frame.pack_forget()
        self.send_file_button.pack(pady=10)
        self.send_folder_button.pack(pady=10)
        self.back_button.pack(pady=10)

    def select_file(self):
        self.send_file_button.pack_forget()
        self.send_folder_button.pack_forget()
        self.back_button.pack_forget()
        file_path = filedialog.askopenfilename(
            title="Choisir un fichier", initialdir=os.path.expanduser("~/Desktop"),
            filetypes=[("Tous les fichiers", "*.*"), ("Documents", "*.pdf *.docx *.txt"), ("Images", "*.jpg *.png")]
        )
        if not file_path:
            self.reset_interface()
            return
        self.selected_path = file_path
        self.file_path = file_path
        self.selected_label.configure(text=f"Sélectionné : {os.path.basename(file_path)}")
        self.selected_label.pack(pady=5)
        self.scan_networks()
        self.ip_label.pack(pady=10)
        self.ip_dropdown.pack(pady=10)
        self.confirm_send_button.pack(pady=10)
        self.cancel_button.pack(pady=10)
        self.update_status("Choisissez un appareil ou scannez le réseau...", "#87CEEB")

    def select_folder(self):
        self.send_file_button.pack_forget()
        self.send_folder_button.pack_forget()
        self.back_button.pack_forget()
        folder_path = filedialog.askdirectory(
            title="Choisir un dossier", initialdir=os.path.expanduser("~/Desktop")
        )
        if not folder_path:
            self.reset_interface()
            return
        self.selected_path = folder_path
        import zipfile
        temp_zip = os.path.join(os.path.dirname(folder_path), "temp_send.zip")
        with zipfile.ZipFile(temp_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, os.path.relpath(file_path, os.path.dirname(folder_path)))
        self.file_path = temp_zip
        self.selected_label.configure(text=f"Sélectionné : {os.path.basename(folder_path)}")
        self.selected_label.pack(pady=5)
        self.scan_networks()
        self.ip_label.pack(pady=10)
        self.ip_dropdown.pack(pady=10)
        self.confirm_send_button.pack(pady=10)
        self.cancel_button.pack(pady=10)
        self.update_status("Choisissez un appareil ou scannez le réseau...", "#87CEEB")

    def _perform_auto_scan(self):
        try:
            active_devices = scan_network("192.168.1.0/24", port=5001)
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
        self.scan_button.configure(state="disabled")
        threading.Thread(target=self._perform_auto_scan, daemon=True).start()

    def _update_scan_results(self, active_devices):
        if not active_devices or not all(isinstance(device, str) for device in active_devices):
            self.ip_dropdown.configure(values=[self.ip_placeholder])
            self.ip_dropdown.set(self.ip_placeholder)
            self.update_status("Aucun appareil trouvé ou erreur de détection", "#FF4500")
            return

        if self.user_name and self.local_ip:
            self.ip_name_map[self.user_name] = self.local_ip
            self.broadcast_name()

        device_names = []
        for ip in active_devices:
            if ip == self.local_ip:
                continue
            for name, mapped_ip in list(self.ip_name_map.items()):
                if mapped_ip == ip and name != self.user_name and name not in device_names:
                    device_names.append(name)
            if ip not in [mapped_ip for _, mapped_ip in self.ip_name_map.items()]:
                default_name = f"Appareil_{ip.split('.')[-1]}"
                if default_name not in device_names:
                    device_names.append(default_name)
                    self.ip_name_map[default_name] = ip

        device_names = [name for name in device_names if name is not None]
        if not device_names:
            self.ip_dropdown.configure(values=[self.ip_placeholder])
            self.ip_dropdown.set(self.ip_placeholder)
            self.update_status("Aucun nom d'appareil détecté", "#FF4500")
            return

        options = [self.ip_placeholder] + sorted(device_names)
        self.ip_dropdown.configure(values=options)
        if not self.ip_dropdown.get() or self.ip_dropdown.get() == self.ip_placeholder:
            self.ip_dropdown.set("")
        self.update_status(f"{len(active_devices)} appareil(s) détecté(s) - Noms: {', '.join(device_names)}", "#32CD32")

    def get_local_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
        finally:
            s.close()
        return ip

    def run_socket_server(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(("", 5002))
        last_map = {}
        while True:
            data, addr = server_socket.recvfrom(1024)
            try:
                name_ip = data.decode().split(":")
                if len(name_ip) == 2 and all(name_ip) and name_ip[1] != self.local_ip:
                    self.ip_name_map[name_ip[0]] = name_ip[1]
                    if self.ip_name_map != last_map:
                        active_ips = [ip for ip in self.ip_name_map.values() if ip != self.local_ip]
                        self.root.after(0, lambda: self._update_scan_results(active_ips))
                        last_map = self.ip_name_map.copy()
            except (ValueError, UnicodeDecodeError):
                continue

    def broadcast_name(self):
        if not self.user_name or not self.local_ip:
            return
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        message = f"{self.user_name}:{self.local_ip}"
        sock.sendto(message.encode(), ('<broadcast>', 5002))
        sock.close()

    def start_send(self):
        target_name = self.ip_dropdown.get()
        if not target_name or target_name == self.ip_placeholder:
            messagebox.showerror("Erreur", "Veuillez sélectionner un destinataire.")
            self.update_status("Erreur : Aucun destinataire sélectionné", "#FF4500")
            return

        target_ip = self.ip_name_map.get(target_name)
        if not target_ip:
            messagebox.showerror("Erreur", "Destinataire non trouvé.")
            self.update_status("Erreur : Destinataire non valide", "#FF4500")
            return

        self.update_status("Envoi en cours...", "#87CEEB")
        if self.file_path is None:
            messagebox.showerror("Erreur", "Aucun fichier ou dossier sélectionné.")
            self.update_status("Erreur : Aucun fichier/dossier sélectionné", "#FF4500")
            return
        self.progress_label.pack(pady=10)
        threading.Thread(target=self._send_file_thread, args=(self.file_path, target_ip, 5001, self.user_name),
                         daemon=True).start()

    def _send_file_thread(self, file_path, ip, port, user_name):
        def update_progress(percentage):
            self.root.after(0, lambda: self.progress_label.configure(text=f"Progression : {percentage:.1f}%"))

        try:
            send_file(file_path, ip, port, user_name, update_progress)
            if file_path.endswith(".zip") and os.path.exists(file_path):
                os.remove(file_path)
            self.root.after(0, lambda: self.update_status("Fichier envoyé avec succès !", "#32CD32"))
            self.root.after(0, lambda: self.progress_label.configure(text="Progression : 100%"))
        except Exception as e:
            self.root.after(0, lambda: self.update_status(f"Erreur : {str(e)}", "#FF4500"))
        finally:
            self.root.after(0, self._hide_progress)

    def _hide_progress(self):
        self.progress_label.pack_forget()

    def start_receive(self):
        if self.is_receiving:
            self.update_status("Une réception est déjà en cours. Attendez ou annulez.", "#FF4500")
            return

        # Arrêter proprement un thread précédent s'il existe
        if self.receive_thread and self.receive_thread.is_alive():
            self.cancel_flag.set()
            self.receive_thread.join(timeout=1)  # Attendre 1 seconde pour terminer
            self.is_receiving = False
            self.cancel_flag.clear()

        # Fenêtre pour choisir entre dossier par défaut et personnalisé
        choice_window = ctk.CTkToplevel(self.root)
        choice_window.title("Choisir un dossier")
        choice_window.geometry("300x150")

        # Suppression de choice_window.grab_set() pour éviter l'erreur

        def use_default_folder():
            save_folder = None  # Utilisera le dossier par défaut dans receiver.py
            choice_window.destroy()
            self._proceed_receive(save_folder)

        def choose_custom_folder():
            save_folder = filedialog.askdirectory(
                title="Choisir un dossier pour sauvegarder les fichiers reçus",
                initialdir=os.path.expanduser("~/")
            )
            if save_folder:
                choice_window.destroy()
                self._proceed_receive(save_folder)
            else:
                messagebox.showwarning("Attention", "Aucun dossier sélectionné, réception annulée.")
                choice_window.destroy()

        ctk.CTkLabel(choice_window, text="Choisir où sauvegarder les fichiers :", font=("Arial", 12),
                     text_color="#FFFFFF").pack(pady=10)
        ctk.CTkButton(choice_window, text="Utiliser le dossier par défaut (files_shared)", command=use_default_folder,
                      fg_color="#1E90FF", hover_color="#4682B4", font=("Arial", 12), width=250).pack(pady=5)
        ctk.CTkButton(choice_window, text="Choisir un dossier personnalisé", command=choose_custom_folder,
                      fg_color="#1E90FF", hover_color="#4682B4", font=("Arial", 12), width=250).pack(pady=5)

        # Utiliser wait_window au lieu de grab_set pour attendre la fermeture de la fenêtre
        self.root.wait_window(choice_window)
        def use_default_folder():
            save_folder = None  # Utilisera le dossier par défaut dans receiver.py
            choice_window.destroy()
            self._proceed_receive(save_folder)

        def choose_custom_folder():
            save_folder = filedialog.askdirectory(
                title="Choisir un dossier pour sauvegarder les fichiers reçus",
                initialdir=os.path.expanduser("~/")
            )
            if save_folder:
                choice_window.destroy()
                self._proceed_receive(save_folder)
            else:
                messagebox.showwarning("Attention", "Aucun dossier sélectionné, réception annulée.")
                choice_window.destroy()

        ctk.CTkLabel(choice_window, text="Choisir où sauvegarder les fichiers :", font=("Arial", 12),
                     text_color="#FFFFFF").pack(pady=10)
        ctk.CTkButton(choice_window, text="Utiliser le dossier par défaut (files_shared)", command=use_default_folder,
                      fg_color="#1E90FF", hover_color="#4682B4", font=("Arial", 12), width=250).pack(pady=5)
        ctk.CTkButton(choice_window, text="Choisir un dossier personnalisé", command=choose_custom_folder,
                      fg_color="#1E90FF", hover_color="#4682B4", font=("Arial", 12), width=250).pack(pady=5)

        self.root.wait_window(choice_window)

    def _proceed_receive(self, save_folder):
        self.button_frame.pack_forget()
        self.ip_label.pack_forget()
        self.ip_dropdown.pack_forget()
        self.confirm_send_button.pack_forget()
        self.cancel_button.pack_forget()
        self.update_status("En attente d'un fichier...", "#87CEEB")
        self.cancel_flag.clear()
        self.cancel_receive_button.pack(pady=10)
        self.back_button.pack(pady=10)
        self.is_receiving = True
        self.progress_label.pack(pady=10)
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                self.receive_thread = threading.Thread(target=self._receive_file_thread,
                                                       args=(5001, self.cancel_flag, save_folder), daemon=True)
                self.receive_thread.start()
                break
            except OSError as e:
                if "Address already in use" in str(e) or "[Errno 98]" in str(e):
                    if attempt < max_attempts - 1:
                        self.update_status(f"Port occupé, réessai {attempt + 1}/{max_attempts}...", "#FFA500")
                        time.sleep(2)
                    else:
                        self.update_status("Port occupé après plusieurs tentatives. Relancez l'application.", "#FF4500")
                        self.is_receiving = False
                        self._hide_progress()
                        self.reset_interface()
                        return
                else:
                    raise

    def cancel_receive(self):
        if self.receive_thread and self.receive_thread.is_alive():
            self.cancel_flag.set()
            self.update_status("Annulation en cours...", "#FFA500")
            self.cancel_receive_button.configure(state="disabled")
            self.receive_thread.join(timeout=2)
            if self.receive_thread.is_alive():
                self.update_status("Annulation forcée, veuillez relancer.", "#FF4500")
            else:
                self.update_status("Réception annulée.", "#32CD32")
            self.is_receiving = False
            self._hide_progress()
            self.reset_interface()

    def _receive_file_thread(self, port, cancel_flag, save_folder):
        def update_progress(percentage):
            self.root.after(0, lambda: self.progress_label.configure(text=f"Progression : {percentage:.1f}%"))

        try:
            receive_file(port, cancel_flag, update_progress, save_folder)
            self.root.after(0, lambda: self.update_status("Fichier reçu avec succès !", "#32CD32"))
            self.root.after(0, lambda: self.progress_label.configure(text="Progression : 100%"))
        except ReceptionCancelled:
            self.root.after(0, lambda: self.update_status("Réception annulée.", "#32CD32"))
        except Exception as e:
            self.root.after(0, lambda: self.update_status(f"Erreur : {str(e)}", "#FF4500"))
        finally:
            self.is_receiving = False
            self.root.after(0, self._hide_progress)

    def reset_interface(self):
        # Arrêter le thread de réception s'il est actif
        if self.receive_thread and self.receive_thread.is_alive():
            self.cancel_flag.set()
            self.update_status("Arrêt de la réception en cours...", "#FFA500")
            self.receive_thread.join(timeout=1)  # Attendre 1 seconde pour terminer
            if self.receive_thread.is_alive():
                self.update_status("Annulation forcée du thread de réception.", "#FF4500")
            else:
                self.update_status("Réception arrêtée.", "#32CD32")
            self.is_receiving = False
            self.cancel_flag.clear()

        self.ip_label.pack_forget()
        self.ip_dropdown.pack_forget()
        self.confirm_send_button.pack_forget()
        self.cancel_button.pack_forget()
        self.cancel_receive_button.pack_forget()
        self.send_file_button.pack_forget()
        self.send_folder_button.pack_forget()
        self.back_button.pack_forget()
        self.selected_label.pack_forget()
        self.progress_label.pack_forget()
        self.button_frame.pack(pady=(100, 10))
        self.is_receiving = False  # Réinitialiser l'état de réception
        self.update_status("Choisissez une action", "#87CEEB")  # Forcer le statut initial
        self.cancel_flag.clear()  # Réinitialiser le drapeau d'annulation

    def show_history(self):
        history_window = ctk.CTkToplevel(self.root)
        history_window.title("Historique des transferts")
        history_window.geometry("600x400")
        history_window.resizable(False, False)

        # Frame pour contenir les entrées d'historique
        history_frame = ctk.CTkFrame(history_window)
        history_frame.pack(pady=10, padx=10, fill="both", expand=True)

        history = load_history()
        if not history:
            ctk.CTkLabel(history_frame, text="Aucun fichier reçu dans l'historique.", font=("Arial", 12),
                         text_color="#FFFFFF").pack(pady=5)
        else:
            received_files = [entry for entry in history if entry.get('operation') == 'received']
            if not received_files:
                ctk.CTkLabel(history_frame, text="Aucun fichier reçu dans l'historique.", font=("Arial", 12),
                             text_color="#FFFFFF").pack(pady=5)
            else:
                for entry in received_files:
                    frame = ctk.CTkFrame(history_frame)
                    frame.pack(fill="x", pady=2, padx=5)

                    file_name = entry['file_name']
                    label = ctk.CTkLabel(frame, text=file_name, font=("Arial", 12), text_color="#FFFFFF")
                    label.pack(side="left", padx=5)

                    # Bouton pour ouvrir le fichier
                    def open_file(file_name=file_name):
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
                        save_folder = os.path.join(save_folder_base, "files_shared")
                        file_path = os.path.join(save_folder, file_name)
                        print(f"Chemin vérifié : {file_path}")  # Pour débogage
                        if os.path.exists(file_path):
                            try:
                                if os.name == 'nt':  # Windows
                                    os.startfile(file_path)
                                else:  # macOS/Linux
                                    subprocess.run([
                                                       'open' if os.name == 'posix' and os.uname().sysname == 'Darwin' else 'xdg-open',
                                                       file_path])
                            except Exception as e:
                                messagebox.showerror("Erreur", f"Impossible d'ouvrir le fichier : {str(e)}")
                        else:
                            messagebox.showwarning("Attention",
                                                   f"Le fichier {file_name} n'a pas été trouvé à {file_path}.")

                    open_button = ctk.CTkButton(frame, text="Ouvrir", command=open_file, fg_color="#1E90FF",
                                                hover_color="#4682B4", font=("Arial", 12), width=60)
                    open_button.pack(side="right", padx=5)

        # Bouton de retour
        back_button = ctk.CTkButton(history_window, text="Retour", command=history_window.destroy, fg_color="#FFD700",
                                    hover_color="#FFA500", font=("Arial", 14), width=200)
        back_button.pack(pady=10)

    def update_status(self, message, color):
        self.status_label.configure(text=message, text_color=color)


if __name__ == "__main__":
    root = ctk.CTk()
    app = FileSharerGUI(root)
    root.mainloop()