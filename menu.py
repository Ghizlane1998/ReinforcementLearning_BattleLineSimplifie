import tkinter as tk
import subprocess
import sys
import os

class GameMenu:
    def __init__(self, root):
        self.root = root
        self.root.title("Sélection du mode de jeu")
        self.root.geometry("1000x700")
        self.root.configure(bg="#2c3e50")

        # Cadre du menu
        self.menu_frame = tk.Frame(root, bg="#34495e", padx=130, pady=100)
        self.menu_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Titre
        tk.Label(self.menu_frame, text="Battle Line", font=("Arial", 24, "bold"),
                 fg="white", bg="#34495e").pack(pady=10)
        tk.Label(self.menu_frame, text="Sélectionnez un mode de jeu", font=("Arial", 14),
                 fg="white", bg="#34495e").pack(pady=10)

        # Style des boutons
        button_style = {
            "font": ("Arial", 14),
            "fg": "white",
            "bg": "#16a085",
            "activebackground": "#1abc9c",
            "width": 20,
            "height": 2,
            "bd": 0
        }

        # Boutons
        tk.Button(self.menu_frame, text="Humain vs Humain",
                  command=self.launch_humain_vs_humain, **button_style).pack(pady=5)

        tk.Button(self.menu_frame, text="Humain vs IA",
                  command=self.launch_humain_vs_ia, **button_style).pack(pady=5)

        tk.Button(self.menu_frame, text="Aléatoire vs Aléatoire",
                  command=self.launch_aleatoire_vs_aleatoire, **button_style).pack(pady=5)

    def launch_humain_vs_ia(self):
        self.launch_script("HumainVS_IA.py")

    def launch_humain_vs_humain(self):
        self.launch_script("agent_human.py")

    def launch_aleatoire_vs_aleatoire(self):
        self.launch_script("agent_aleatoire.py")

    def launch_script(self, filename):
        script_path = os.path.join(os.path.dirname(__file__), filename)
        if os.path.exists(script_path):
            subprocess.Popen([sys.executable, script_path])
            self.root.destroy()
        else:
            print(f"Le fichier {filename} n'existe pas.")

def main():
    root = tk.Tk()
    GameMenu(root)
    root.mainloop()

if __name__ == "__main__":
    main()
