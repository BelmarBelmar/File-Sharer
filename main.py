import subprocess
import os
import platform

def main():
    # Chemin vers le fichier .bat ou .sh (ajuste selon ton dossier)
    script_dir = os.path.dirname(__file__)
    bat_path = os.path.join(script_dir, "launch.bat")
    sh_path = os.path.join(script_dir, "launch.sh")  # Ajoute le chemin du .sh

    # Lancer le script approprié selon le système d'exploitation
    if platform.system() == "Windows":
        if os.path.exists(bat_path):
            subprocess.Popen(bat_path, shell=True)
        else:
            print(f"Erreur : Le fichier {bat_path} n'est pas trouvé.")
    else:  # Linux, macOS, ou autres Unix
        if os.path.exists(sh_path):
            subprocess.Popen(["bash", sh_path], shell=False)  # Exécuter avec bash
        else:
            print(f"Erreur : Le fichier {sh_path} n'est pas trouvé.")

    # Continuer avec le reste de main()
    import customtkinter as ctk
    from gui import FileSharerGUI

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    root = ctk.CTk()
    app = FileSharerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()