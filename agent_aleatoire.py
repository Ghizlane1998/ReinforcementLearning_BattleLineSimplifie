import tkinter as tk
import random
import os
import sys
import subprocess
from PIL import Image, ImageTk
from battle_line_env import BattleLineEnv

WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 730
NUM_FLAGS = 9
HAND_CARD_WIDTH = 72
HAND_CARD_HEIGHT = 96
FLAG_WIDTH = 60
FLAG_HEIGHT = 80

CARD_COLORS = ["blue", "red", "pink", "yellow", "green", "white"]
VALUES = list(range(1, 11))

class BattleLineAutoInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("Battle Line - Agent aléatoire vs Agent aléatoire")

        self.canvas = tk.Canvas(root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT - 150, bg="green")
        self.canvas.pack()

        self.card_images = {}
        self.flag_images = {}
        self.load_images()

        self.env = BattleLineEnv(opponent_policy="random")
        self.state = self.env.reset()
        self.flags = []

        self.draw_labels()
        self.draw_flags()

        # Ajout d’un conteneur pour le bouton retour
        self.end_frame = tk.Frame(root, bg="green")
        self.end_frame.pack(side="bottom", pady=10)

        self.root.after(1000, self.play_turns)

    def draw_labels(self):
        self.top_player_label = tk.Label(self.root, text="Joueur Aléatoire 1 (bleu)", font=("Arial", 14, "bold"), bg="green", fg="white")
        self.top_player_label.place(x=80, y=20)

        self.bottom_player_label = tk.Label(self.root, text="Joueur Aléatoire 2 (rouge)", font=("Arial", 14, "bold"), bg="green", fg="white")
        self.bottom_player_label.place(x=80, y=WINDOW_HEIGHT - 200)

    def load_images(self):
        images_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")
        for color in CARD_COLORS:
            for value in VALUES:
                filename = f"{color}-{value}.png"
                path = os.path.join(images_dir, filename)
                if os.path.exists(path):
                    img = Image.open(path).resize((HAND_CARD_WIDTH, HAND_CARD_HEIGHT), Image.Resampling.LANCZOS)
                    self.card_images[(color, value)] = ImageTk.PhotoImage(img)
        for color in ["white", "blue", "red"]:
            path = os.path.join(images_dir, f"flag-{color}.png")
            if os.path.exists(path):
                img = Image.open(path).resize((FLAG_WIDTH, FLAG_HEIGHT), Image.Resampling.LANCZOS)
                self.flag_images[color] = ImageTk.PhotoImage(img)

    def draw_flags(self):
        spacing = WINDOW_WIDTH / (NUM_FLAGS + 1)
        self.flags.clear()
        for i in range(NUM_FLAGS):
            cx = (i + 1) * spacing
            cy = (WINDOW_HEIGHT - 150) / 2
            img = self.flag_images["white"]
            item = self.canvas.create_image(cx, cy, image=img, anchor="center")
            self.flags.append({"index": i, "center": (cx, cy), "item": item})

    def draw_cards_on_flags(self):
        self.canvas.delete("card")
        for i, flag in enumerate(self.env.game.state.flags):
            cx, cy = self.flags[i]["center"]
            # Player cards (top)
            for j, card in enumerate(flag.slots["player"]):
                x = cx - HAND_CARD_WIDTH / 2
                y = cy - FLAG_HEIGHT / 2 - HAND_CARD_HEIGHT - j * 20
                img = self.card_images.get((card.color, card.value))
                if img:
                    self.canvas.create_image(x, y, image=img, anchor="nw", tags="card")
            # Opponent cards (bottom)
            for j, card in enumerate(flag.slots["opponent"]):
                x = cx - HAND_CARD_WIDTH / 2
                y = cy + FLAG_HEIGHT / 2 + j * 20
                img = self.card_images.get((card.color, card.value))
                if img:
                    self.canvas.create_image(x, y, image=img, anchor="nw", tags="card")

    def update_flag_status(self):
        for i, flag in enumerate(self.env.game.state.flags):
            color = "white"
            if flag.winner == "player":
                color = "blue"
            elif flag.winner == "opponent":
                color = "red"
            self.canvas.itemconfigure(self.flags[i]["item"], image=self.flag_images[color])

    def play_turns(self):
        if self.env.get_valid_actions():
            action = random.choice(self.env.get_valid_actions())
            _, _, done, _ = self.env.step(action)
            self.draw_cards_on_flags()
            self.update_flag_status()
            if done:
                winner = self.env.game.state.check_game_over()
                label = "Joueur Aléatoire 1" if winner == "player" else "Joueur Aléatoire 2" if winner == "opponent" else "Égalité"
                self.canvas.create_text(WINDOW_WIDTH // 2, 40, text=f"🏆 Gagnant : {label} 🏆", font=("Arial", 28, "bold"), fill="white")

                # Bouton de retour au menu
                return_button = tk.Button(self.end_frame, text="Retour au menu principal", font=("Arial", 14, "bold"),
                                          bg="#2980b9", fg="white", command=self.return_to_menu)
                return_button.pack()
                return

            self.root.after(1000, self.play_turns)

    def return_to_menu(self):
        script_path = os.path.join(os.path.dirname(__file__), "menu.py")
        if os.path.exists(script_path):
            subprocess.Popen([sys.executable, script_path])
        self.root.destroy()

def main():
    root = tk.Tk()
    app = BattleLineAutoInterface(root)
    root.mainloop()

if __name__ == "__main__":
    main()
