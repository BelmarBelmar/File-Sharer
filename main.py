import customtkinter as ctk
from gui import FileSharerGUI

def main():
    ctk.set_appearance_mode("dark") 
    ctk.set_default_color_theme("blue")
    root = ctk.CTk()  # Fenêtre principale
    app = FileSharerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()