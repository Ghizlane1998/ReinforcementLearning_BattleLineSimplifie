import subprocess
import sys
import tkinter as tk
from PIL import Image, ImageTk
import os
import random
import numpy as np
import torch
import pygame

from battle_line_env import BattleLineEnv
from battle_line_game import MAX_HAND_SIZE
from dqn_agent import DQNAgent

WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 730
NUM_FLAGS = 9

HAND_CARD_WIDTH = 72
HAND_CARD_HEIGHT = 96
FLAG_WIDTH = 60
FLAG_HEIGHT = 80

HAND_START_X = 50
HAND_Y = WINDOW_HEIGHT - HAND_CARD_HEIGHT - 200
TOP_HAND_START_X = 50
TOP_HAND_Y = 20
HAND_CARD_SPACING = 80

CARD_COLORS = ["blue", "red", "pink", "yellow", "green", "white"]
VALUES = list(range(1, 11))
STATE_DIM = 1836
ACTION_DIM = 63

def init_music():
    pygame.mixer.init()
    music_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "music", 
                              "Pokémon Omega Ruby & Alpha Sapphire - Zinnia Battle Music (HQ).mp3")
    if os.path.exists(music_path):
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
    else:
        print("Fichier de musique introuvable :", music_path)

class GameInterface:
    def __init__(self, root, mode="Humain vs IA"):
        self.root = root
        self.mode = mode
        self.root.title(f"Battle Line - {mode}")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")

        self.canvas = tk.Canvas(root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT - 150, bg="green")
        self.canvas.pack(side="top")

        self.card_images = {}
        self.flag_images = {}
        self.load_images()
        self.init_sounds()

        self.env = BattleLineEnv(opponent_policy="random")
        self.state = self.env.game.get_state_vector()
        self.agent = None
        if mode == "Humain vs IA":
            self.agent = DQNAgent(STATE_DIM, ACTION_DIM)
            self.agent.policy_net.load_state_dict(torch.load("model/model.pth", map_location=torch.device('cpu')))
            self.agent.policy_net.eval()

        self.deck_image = self.load_deck_image("card-troop.png", 80, 120)
        self.deck_x = 45
        self.deck_y = (WINDOW_HEIGHT - 150) // 2
        if self.deck_image:
            self.canvas.create_image(self.deck_x, self.deck_y, image=self.deck_image, anchor="center")

        self.flags = []
        self.hand_card_items = {}
        self.draw_flags()
        self.draw_hands()

        self.drag_data = {"item": None, "x": 0, "y": 0}

        self.button_frame = tk.Frame(root)
        self.button_frame.pack(side="bottom", pady=5)
        self.draw_bottom_btn = tk.Button(self.button_frame, text="Piocher carte (Joueur)", command=self.draw_card_bottom)
        self.draw_bottom_btn.pack(side="left", padx=10)
        self.restart_btn = tk.Button(self.button_frame, text="Recommencer", command=self.restart_game, state="disabled")
        self.restart_btn.pack(side="left", padx=10)

        self.score_frame = tk.Frame(root)
        self.score_frame.pack(side="bottom", pady=5)
        self.top_info_label = tk.Label(self.score_frame, text="Adversaire: Drapeaux: 0 | Adjacents: False", font=("Arial", 12))
        self.top_info_label.pack(side="left", padx=20)
        self.bottom_info_label = tk.Label(self.score_frame, text="Joueur: Drapeaux: 0 | Adjacents: False", font=("Arial", 12))
        self.bottom_info_label.pack(side="left", padx=20)

    def init_sounds(self):
        try:
            pygame.mixer.init()
        except Exception as e:
            print("Erreur d'initialisation du mixer :", e)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        sounds_dir = os.path.join(script_dir, "music")
        click_path = os.path.join(sounds_dir, "Click - Sound Effect (HD).mp3")
        if os.path.exists(click_path):
            try:
                self.click_sound = pygame.mixer.Sound(click_path)
            except Exception as e:
                print("Erreur lors du chargement du son clic :", e)
                self.click_sound = None
        else:
            print("Fichier click.wav manquant dans le dossier sounds")
            self.click_sound = None
        congrats_path = os.path.join(sounds_dir, "congrats.wav")
        if os.path.exists(congrats_path):
            try:
                self.congrats_sound = pygame.mixer.Sound(congrats_path)
            except Exception as e:
                print("Erreur lors du chargement du son de félicitations :", e)
                self.congrats_sound = None
        else:
            print("Fichier congrats.wav manquant dans le dossier sounds")
            self.congrats_sound = None

    def load_images(self):
        images_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")
        for color in CARD_COLORS:
            for value in VALUES:
                path = os.path.join(images_dir, f"{color}-{value}.png")
                if os.path.exists(path):
                    img = Image.open(path).resize((HAND_CARD_WIDTH, HAND_CARD_HEIGHT), Image.Resampling.LANCZOS)
                    self.card_images[(color, value)] = ImageTk.PhotoImage(img)
        for color in ["blue", "red", "white"]:
            path = os.path.join(images_dir, f"flag-{color}.png")
            if os.path.exists(path):
                img = Image.open(path).resize((FLAG_WIDTH, FLAG_HEIGHT), Image.Resampling.LANCZOS)
                self.flag_images[color] = ImageTk.PhotoImage(img)

    def load_deck_image(self, filename, width, height):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images", filename)
        if os.path.exists(path):
            img = Image.open(path).resize((width, height), Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(img)
        return None

    def draw_flags(self):
        for flag in self.flags:
            self.canvas.delete(flag.get("item"))
        self.flags.clear()
        spacing = WINDOW_WIDTH / (NUM_FLAGS + 1)
        for i in range(NUM_FLAGS):
            cx = (i + 1) * spacing
            cy = (WINDOW_HEIGHT - 150) / 2
            winner = self.env.game.state.flags[i].winner
            color = "blue" if winner == "player" else "red" if winner == "opponent" else "white"
            img = self.flag_images[color]
            item = self.canvas.create_image(cx, cy, image=img, anchor="center")
            x1, y1 = cx - FLAG_WIDTH / 2, cy - FLAG_HEIGHT / 2
            x2, y2 = cx + FLAG_WIDTH / 2, cy + FLAG_HEIGHT / 2
            self.flags.append({"index": i, "center": (cx, cy), "bbox": (x1, y1, x2, y2), "item": item})
            self.draw_cards_on_flag(i)

    def draw_cards_on_flag(self, flag_idx):
        flag = self.flags[flag_idx]
        state = self.env.game.state.flags[flag_idx]
        cx, cy = flag["center"]
        for i, card in enumerate(state.slots["player"]):
            x = cx - HAND_CARD_WIDTH / 2
            y = cy + FLAG_HEIGHT / 2 + i * 15
            img = self.card_images.get((card.color, card.value))
            if img:
                self.canvas.create_image(x, y, image=img, anchor="nw")
        for i, card in enumerate(state.slots["opponent"]):
            x = cx - HAND_CARD_WIDTH / 2
            y = cy - FLAG_HEIGHT / 2 - (i + 1) * 15 - 70
            img = self.card_images.get((card.color, card.value))
            if img:
                self.canvas.create_image(x, y, image=img, anchor="nw")

    def draw_hands(self):
        for item_id in list(self.hand_card_items):
            info = self.hand_card_items[item_id]
            if info["player"] in ["top", "bottom"]:
                self.canvas.delete(item_id)
                del self.hand_card_items[item_id]
        for idx, card in enumerate(self.env.game.state.hands["player"]):
            x = HAND_START_X + idx * HAND_CARD_SPACING
            y = HAND_Y
            img = self.card_images.get((card.color, card.value))
            item = self.canvas.create_image(x, y, image=img, anchor="nw")
            self.hand_card_items[item] = {"card": card, "orig_pos": (x, y), "player": "bottom", "index": idx}
            self.canvas.tag_bind(item, "<ButtonPress-1>", self.on_card_press)
            self.canvas.tag_bind(item, "<B1-Motion>", self.on_card_motion)
            self.canvas.tag_bind(item, "<ButtonRelease-1>", self.on_card_release)
        for idx, card in enumerate(self.env.game.state.hands["opponent"]):
            x = TOP_HAND_START_X + idx * HAND_CARD_SPACING
            y = TOP_HAND_Y
            img = self.card_images.get((card.color, card.value))
            item = self.canvas.create_image(x, y, image=img, anchor="nw")
            self.hand_card_items[item] = {"card": card, "orig_pos": (x, y), "player": "top", "index": idx}

    def play_ai_turn(self):
        if self.env.game.state.current_turn != "opponent":
            return
        state = self.env.game.get_state_vector()
        valid_actions = self.env.get_valid_actions()
        state_tensor = torch.FloatTensor(state).unsqueeze(0)
        with torch.no_grad():
            q_values = self.agent.policy_net(state_tensor).squeeze().numpy()
        masked_q = np.full(ACTION_DIM, -np.inf)
        for a in valid_actions:
            masked_q[a] = q_values[a]
        action = int(np.argmax(masked_q))
        
        _, reward, done, info = self.env.step(action)
        self.draw_flags()
        self.draw_hands()
        self.update_scores()
        if self.check_game_over():
            return
        if done:
            self.display_game_over("Partie terminée!")
            self.restart_btn.config(state="normal")
        # Sinon, c'est au tour du joueur

    def on_card_press(self, event):
        item = self.canvas.find_withtag("current")[0]
        self.drag_data = {"item": item, "x": event.x, "y": event.y}
        if self.click_sound:
            self.click_sound.play()

    def on_card_motion(self, event):
        if self.drag_data["item"]:
            dx = event.x - self.drag_data["x"]
            dy = event.y - self.drag_data["y"]
            self.canvas.move(self.drag_data["item"], dx, dy)
            self.drag_data["x"], self.drag_data["y"] = event.x, event.y

    def on_card_release(self, event):
        item = self.drag_data["item"]
        if item is None:
            return
        info = self.hand_card_items.get(item)
        if not info or info["player"] != "bottom":
            self.canvas.coords(item, *info["orig_pos"])
            return
        cx, cy = self.canvas.coords(item)[0] + HAND_CARD_WIDTH / 2, self.canvas.coords(item)[1] + HAND_CARD_HEIGHT / 2
        for flag in self.flags:
            x1, y1, x2, y2 = flag["bbox"]
            if x1 <= cx <= x2 and y1 <= cy <= y2:
                action = info["index"] * NUM_FLAGS + flag["index"]
                _, _, done, step_info = self.env.step(action)
                if "error" in step_info:
                    self.canvas.coords(item, *info["orig_pos"])
                    self.canvas.create_text(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2,
                                              text="Mouvement invalide!", font=("Arial", 24, "bold"),
                                              fill="white", tags="error_message")
                    self.root.after(2000, lambda: self.canvas.delete("error_message"))
                else:
                    self.draw_flags()
                    self.draw_hands()
                    self.update_scores()
                    if not self.check_game_over():
                        self.root.after(1000, self.play_ai_turn)
                break
        self.drag_data["item"] = None

    def draw_card_bottom(self):
        if self.env.game.state.current_turn == "player":
            if self.env.game.state.deck and len(self.env.game.state.hands["player"]) < MAX_HAND_SIZE:
                self.env.game.state.hands["player"].append(self.env.game.state.deck.pop())
                self.draw_hands()

    def update_scores(self):
        flags = self.env.game.state.flags
        pf = sum(1 for f in flags if f.winner == "player")
        of = sum(1 for f in flags if f.winner == "opponent")
        pa = any(flags[i].winner == "player" and flags[i+1].winner == "player" and flags[i+2].winner == "player" 
                 for i in range(len(flags)-2))
        oa = any(flags[i].winner == "opponent" and flags[i+1].winner == "opponent" and flags[i+2].winner == "opponent" 
                 for i in range(len(flags)-2))
        self.top_info_label.config(text=f"Adversaire: Drapeaux: {of} | Adjacents: {oa}")
        self.bottom_info_label.config(text=f"Joueur: Drapeaux: {pf} | Adjacents: {pa}")

    def check_game_over(self):
        flags = self.env.game.state.flags
        pf = sum(1 for f in flags if f.winner == "player")
        of = sum(1 for f in flags if f.winner == "opponent")
        pa = any(flags[i].winner == "player" and flags[i+1].winner == "player" and flags[i+2].winner == "player"
                 for i in range(len(flags)-2))
        oa = any(flags[i].winner == "opponent" and flags[i+1].winner == "opponent" and flags[i+2].winner == "opponent"
                 for i in range(len(flags)-2))
        if pf >= 5 or pa:
            self.display_game_over("Joueur")
            return True
        elif of >= 5 or oa:
            self.display_game_over("Adversaire")
            return True
        return False

    def display_game_over(self, winner):
        self.restart_btn.config(state="normal")  
        self.canvas.create_text(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2, text=f"{winner} a gagné !", font=("Arial", 32, "bold"), fill="white")
        if self.congrats_sound:
            self.congrats_sound.play()
        bottom_frame = tk.Frame(self.root, bg="white")
        bottom_frame.pack(fill="x", pady=(10, 20))
        return_btn = tk.Button(self.root, text="Retour au menu principal", font=("Arial", 14, "bold"), bg="#2980b9", fg="white", command=self.return_to_menu)
        return_btn.pack(in_=bottom_frame, pady=10)


   

    def restart_game(self):
        from battle_line_game import GameState
        self.env = BattleLineEnv(opponent_policy="random")
        self.state = self.env.game.get_state_vector()
        self.canvas.delete("all")
        if self.deck_image:
            self.canvas.create_image(self.deck_x, self.deck_y, image=self.deck_image, anchor="center")
        self.flags = []
        self.hand_card_items = {}
        self.draw_flags()
        self.draw_hands()
        self.update_scores()
        self.draw_bottom_btn.config(state="normal")
        self.restart_btn.config(state="disabled")


    def return_to_menu(self):
        script_path = os.path.join(os.path.dirname(__file__), "menu.py")
        if os.path.exists(script_path):
            subprocess.Popen([sys.executable, script_path])
        self.root.destroy()



def main():
    init_music()
    root = tk.Tk()
    GameInterface(root, mode="Humain vs IA")  #
    root.mainloop()

if __name__ == "__main__":
    main()