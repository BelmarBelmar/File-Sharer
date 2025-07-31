import customtkinter as ctk
from gui import FileSharerGUI

if __name__ == "__main__":
    root = ctk.CTk()
    app = FileSharerGUI(root)
    root.mainloop()