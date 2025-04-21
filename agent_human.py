import subprocess
import sys
import tkinter as tk
from PIL import Image, ImageTk
import os
from battle_line_game import BattleLineGame, Card

WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 730
NUM_FLAGS = 9

CARD_WIDTH = 72
CARD_HEIGHT = 96
FLAG_WIDTH = 60
FLAG_HEIGHT = 80

HAND_SPACING = 80
TOP_HAND_Y = 20
BOTTOM_HAND_Y = WINDOW_HEIGHT - CARD_HEIGHT - 150
HAND_START_X = 50

BASE_DIR = os.path.dirname(__file__)
CARD_COLORS = ["blue", "red", "pink", "yellow", "green", "white"]
VALUES = list(range(1, 11))

class HumanVsHuman:
    def __init__(self, root):
        self.root = root
        self.root.title("Battle Line - Humain vs Humain")
        self.canvas = tk.Canvas(root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT - 150, bg="green")
        self.canvas.pack(side="top")

        self.card_images = {}
        self.flag_images = {}
        self.load_images()

        self.game = BattleLineGame()
        self.hand_card_items = {}
        self.placed_cards_visuals = {i: {"player": [], "opponent": []} for i in range(NUM_FLAGS)}

        self.deck_img = self.load_image("card-troop.png", 80, 120)
        self.deck_x = 45
        self.deck_y = (WINDOW_HEIGHT - 150) // 2
        self.canvas.create_image(self.deck_x, self.deck_y, image=self.deck_img, anchor="center")

        self.draw_flags()
        self.draw_hands()
        self.draw_placed_cards()

        self.drag_data = {"item": None, "x": 0, "y": 0}

        self.score_frame = tk.Frame(root)
        self.score_frame.pack(side="bottom", pady=10)
        self.top_info = tk.Label(self.score_frame, text="Joueur Haut: Drapeaux: 0", font=("Arial", 12))
        self.top_info.pack(side="left", padx=50)
        self.bottom_info = tk.Label(self.score_frame, text="Joueur Bas: Drapeaux: 0", font=("Arial", 12))
        self.bottom_info.pack(side="right", padx=50)

    def load_image(self, filename, w, h):
        path = os.path.join(BASE_DIR, "images", filename)
        if os.path.exists(path):
            return ImageTk.PhotoImage(Image.open(path).resize((w, h)))
        return None

    def load_images(self):
        for color in CARD_COLORS:
            for value in VALUES:
                path = os.path.join(BASE_DIR, "images", f"{color}-{value}.png")
                if os.path.exists(path):
                    img = Image.open(path).resize((CARD_WIDTH, CARD_HEIGHT))
                    self.card_images[(color, value)] = ImageTk.PhotoImage(img)
        for color in ["white", "blue", "red"]:
            path = os.path.join(BASE_DIR, "images", f"flag-{color}.png")
            if os.path.exists(path):
                img = Image.open(path).resize((FLAG_WIDTH, FLAG_HEIGHT))
                self.flag_images[color] = ImageTk.PhotoImage(img)

    def draw_flags(self):
        spacing = WINDOW_WIDTH / (NUM_FLAGS + 1)
        self.flag_items = []
        for i in range(NUM_FLAGS):
            cx = (i + 1) * spacing
            cy = (WINDOW_HEIGHT - 150) // 2
            img = self.flag_images.get("white")
            item = self.canvas.create_image(cx, cy, image=img, anchor="center")
            self.flag_items.append((item, cx, cy))

    def draw_hands(self):
        for item in list(self.hand_card_items):
            self.canvas.delete(item)
        self.hand_card_items.clear()

        for idx, card in enumerate(self.game.state.hands["player"]):
            x, y = HAND_START_X + idx * HAND_SPACING, TOP_HAND_Y
            img = self.card_images.get((card.color, card.value))
            if img:
                item = self.canvas.create_image(x, y, image=img, anchor="nw")
                self.hand_card_items[item] = {"card": card, "player": "player", "orig_pos": (x, y)}
                self.bind_card_events(item)

        for idx, card in enumerate(self.game.state.hands["opponent"]):
            x, y = HAND_START_X + idx * HAND_SPACING, BOTTOM_HAND_Y
            img = self.card_images.get((card.color, card.value))
            if img:
                item = self.canvas.create_image(x, y, image=img, anchor="nw")
                self.hand_card_items[item] = {"card": card, "player": "opponent", "orig_pos": (x, y)}
                self.bind_card_events(item)

    def bind_card_events(self, item):
        self.canvas.tag_bind(item, "<ButtonPress-1>", self.on_press)
        self.canvas.tag_bind(item, "<B1-Motion>", self.on_drag)
        self.canvas.tag_bind(item, "<ButtonRelease-1>", self.on_release)

    def on_press(self, event):
        item = self.canvas.find_withtag("current")[0]
        self.drag_data = {"item": item, "x": event.x, "y": event.y}

    def on_drag(self, event):
        dx = event.x - self.drag_data["x"]
        dy = event.y - self.drag_data["y"]
        self.canvas.move(self.drag_data["item"], dx, dy)
        self.drag_data["x"], self.drag_data["y"] = event.x, event.y

    def on_release(self, event):
        item = self.drag_data["item"]
        if not item: return
        data = self.hand_card_items[item]
        cx, cy = self.canvas.coords(item)
        cx += CARD_WIDTH / 2
        cy += CARD_HEIGHT / 2
        for idx, (flag_item, fx, fy) in enumerate(self.flag_items):
            if abs(fx - cx) < 40 and abs(fy - cy) < 60:
                self.play_move(data["player"], data["card"], idx, item)
                break
        self.drag_data = {"item": None, "x": 0, "y": 0}

    def play_move(self, player, card, flag_idx, canvas_item):
        hand = self.game.state.hands[player]
        if card not in hand:
            return
        card_index = hand.index(card)
        valid, winner, error = self.game.step(player, card_index, flag_idx)
        if valid:
            self.canvas.delete(canvas_item)
            self.draw_hands()
            self.update_flags()
            self.draw_placed_cards()
            self.update_scores()
            if winner:
                self.end_game("Joueur Haut" if winner == "player" else "Joueur Bas")

    def draw_placed_cards(self):
        for i in range(NUM_FLAGS):
            for tag in self.placed_cards_visuals[i]["player"] + self.placed_cards_visuals[i]["opponent"]:
                self.canvas.delete(tag)
            self.placed_cards_visuals[i]["player"].clear()
            self.placed_cards_visuals[i]["opponent"].clear()

        for i, flag in enumerate(self.game.state.flags):
            cx, cy = self.flag_items[i][1], self.flag_items[i][2]
            for j, card in enumerate(flag.slots["player"]):
                img = self.card_images.get((card.color, card.value))
                if img:
                    x = cx - CARD_WIDTH / 2
                    y = cy - FLAG_HEIGHT / 2 - CARD_HEIGHT - (j * 10)
                    tag = self.canvas.create_image(x, y, image=img, anchor="nw")
                    self.placed_cards_visuals[i]["player"].append(tag)
            for j, card in enumerate(flag.slots["opponent"]):
                img = self.card_images.get((card.color, card.value))
                if img:
                    x = cx - CARD_WIDTH / 2
                    y = cy + FLAG_HEIGHT / 2 + (j * 10)
                    tag = self.canvas.create_image(x, y, image=img, anchor="nw")
                    self.placed_cards_visuals[i]["opponent"].append(tag)

    def update_flags(self):
        for i, f in enumerate(self.game.state.flags):
            if f.winner == "player":
                self.canvas.itemconfigure(self.flag_items[i][0], image=self.flag_images["blue"])
            elif f.winner == "opponent":
                self.canvas.itemconfigure(self.flag_items[i][0], image=self.flag_images["red"])

    def update_scores(self):
        top_flags = sum(1 for f in self.game.state.flags if f.winner == "player")
        bot_flags = sum(1 for f in self.game.state.flags if f.winner == "opponent")
        self.top_info.config(text=f"Joueur Haut: Drapeaux: {top_flags}")
        self.bottom_info.config(text=f"Joueur Bas: Drapeaux: {bot_flags}")

    def end_game(self, winner):
        self.canvas.create_text(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2, text=f"{winner} a gagné !", font=("Arial", 32, "bold"), fill="white")
        
        bottom_frame = tk.Frame(self.root, bg="white")
        bottom_frame.pack(side="bottom", fill="x", pady=(10, 20))

        return_button = tk.Button(
            bottom_frame, text="Retour au menu principal",
            font=("Arial", 14, "bold"), bg="#2980b9", fg="white",
            command=self.return_to_menu
        )
        return_button.pack(pady=10)

    def return_to_menu(self):
        script_path = os.path.join(os.path.dirname(__file__), "menu.py")
        if os.path.exists(script_path):
            subprocess.Popen([sys.executable, script_path])
        self.root.destroy()

def main():
    root = tk.Tk()
    HumanVsHuman(root)
    root.mainloop()

if __name__ == "__main__":
    main()
