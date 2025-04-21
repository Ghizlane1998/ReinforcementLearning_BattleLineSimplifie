import random
import numpy as np

COLORS = ['red', 'blue', 'green', 'pink', 'yellow', 'white']
NUM_VALUES = 10
MAX_HAND_SIZE = 7
NBR_BITS = 27

def encode_card_full16(card, deposited=False, owner=None, flag=None):
    vec = np.zeros(16, dtype=np.int32)
    if 1 <= card.value <= 10:
        bin_value = [int(x) for x in format(card.value, '04b')]
        vec[0:4] = bin_value
    if card.color in COLORS:
        color_idx = COLORS.index(card.color)
        bin_color = [int(x) for x in format(color_idx, '03b')]
        vec[4:7] = bin_color
    vec[7] = 1 if deposited else 0
    vec[8] = 1 if deposited and owner == "player" else 0
    if deposited and flag is not None and 0 <= flag <= 8:
        bin_flag = [int(x) for x in format(flag, '04b')]
        vec[9:13] = bin_flag
    return vec

def encode_card_full(card, deposited=False, owner=None, flag=None):
    vec = [0] * 27
    if 1 <= card.value <= NUM_VALUES:
        vec[card.value - 1] = 1
    if card.color in COLORS:
        color_idx = COLORS.index(card.color)
        vec[10 + color_idx] = 1
    if deposited:
        vec[16] = 1
        vec[17] = 1 if owner == "player" else 0
    if deposited and flag is not None and 0 <= flag < 9:
        vec[18 + flag] = 1
    return np.array(vec, dtype=np.int32)

def encode_hand(hand, max_cards=MAX_HAND_SIZE):
    encoded = []
    for i in range(max_cards):
        if i < len(hand):
            encoded.extend(encode_card_full(hand[i], deposited=False, owner=None, flag=None))
        else:
            encoded.extend([0]*27)
    return np.array(encoded, dtype=np.int32)

class Card:
    def __init__(self, color, value):
        self.color = color
        self.value = value

    def __repr__(self):
        return f"{self.color[0].upper()}{self.value}"

class Flag:
    def __init__(self):
        self.slots = {"player": [], "opponent": []}
        self.winner = None

    def add_card(self, player, card):
        if self.winner is not None:
            return False, "Drapeau déjà décidé."
        if len(self.slots[player]) >= 3:
            return False, "Ce côté a déjà 3 cartes."
        self.slots[player].append(card)
        if self.is_complete():
            self.winner = self.get_winner()
        return True, ""

    def is_complete(self):
        return (len(self.slots["player"]) == 3) and (len(self.slots["opponent"]) == 3)

    def get_winner(self):
        if not self.is_complete():
            return None
        p_strength = evaluate_hand(self.slots["player"])
        o_strength = evaluate_hand(self.slots["opponent"])
        if p_strength > o_strength:
            return "player"
        elif o_strength > p_strength:
            return "opponent"
        else:
            return "draw"

def evaluate_hand(cards):
    if len(cards) < 3:
        return (0, 0)
    values = sorted([c.value for c in cards])
    colors = [c.color for c in cards]
    if values[0] == values[1] == values[2]:
        return (6, values[0])
    is_straight = (values[0] + 1 == values[1] and values[1] + 1 == values[2])
    is_flush = (colors[0] == colors[1] == colors[2])
    if is_straight and is_flush:
        return (5, values[2])
    if is_flush:
        desc = sorted(values, reverse=True)
        return (4, desc[0], desc[1], desc[2])
    if is_straight:
        return (3, values[2])
    if values[0] == values[1] or values[1] == values[2] or values[0] == values[2]:
        if values[0] == values[1]:
            pair = values[0]
            kicker = values[2]
        elif values[1] == values[2]:
            pair = values[1]
            kicker = values[0]
        else:
            pair = values[0]
            kicker = values[1]
        return (2, pair, kicker)
    desc = sorted(values, reverse=True)
    return (1, desc[0], desc[1], desc[2])

class GameState:
    def __init__(self):
        self.deck = []
        for color in COLORS:
            for val in range(1, NUM_VALUES+1):
                self.deck.append(Card(color, val))
        random.shuffle(self.deck)
        self.flags = [Flag() for _ in range(9)]
        self.hands = {"player": [], "opponent": []}
        for _ in range(MAX_HAND_SIZE):
            self.hands["player"].append(self.deck.pop())
            self.hands["opponent"].append(self.deck.pop())
        self.current_turn = "player"

    def check_game_over(self):
        for f in self.flags:
            if f.is_complete() and f.winner is None:
                f.winner = f.get_winner()
        results = [f.winner for f in self.flags]
        player_flags = sum(1 for r in results if r == "player")
        opp_flags = sum(1 for r in results if r == "opponent")
        if player_flags >= 5:
            return "player"
        if opp_flags >= 5:
            return "opponent"
        for i in range(len(results) - 2):
            if results[i] == results[i+1] == results[i+2] == "player":
                return "player"
            if results[i] == results[i+1] == results[i+2] == "opponent":
                return "opponent"
        return None

    def available_actions(self, player):
        acts = []
        for i in range(len(self.hands[player])):
            for fi, f in enumerate(self.flags):
                if f.winner is not None:
                    continue
                if len(f.slots[player]) < 3:
                    acts.append((i, fi))
        return acts

    def play_move(self, player, card_index, flag_index):
        if card_index >= len(self.hands[player]) or flag_index >= len(self.flags):
            return False, "Index invalide."
        flag = self.flags[flag_index]
        success, error = flag.add_card(player, self.hands[player][card_index])
        if not success:
            return False, error
        self.hands[player].pop(card_index)
        if self.deck and len(self.hands[player]) < MAX_HAND_SIZE:
            self.hands[player].append(self.deck.pop())
        self.current_turn = "opponent" if player == "player" else "player"
        return True, ""

class BattleLineGame:
    def __init__(self):
        self.state = GameState()
        self.winner = None
        self.move_count = 0

    def step(self, player, card_index, flag_index):
        valid, error = self.state.play_move(player, card_index, flag_index)
        self.move_count += 1
        self.winner = self.state.check_game_over()
        return valid, self.winner, error

    def render(self):
        print("\n--- État du jeu Battle Line ---")
        for i, f in enumerate(self.state.flags):
            print(f"Drapeau {i+1} (Gagnant: {f.winner}):")
            print("  Joueur:", f.slots["player"])
            print("  Adversaire:", f.slots["opponent"])
        print("Main joueur:", self.state.hands["player"])
        print("Main adversaire:", self.state.hands["opponent"])
        print("Tour actuel:", self.state.current_turn)
        print("--------------------------------\n")

    def get_valid_actions(self):
        acts = self.state.available_actions("player")
        valid = []
        for (c, f) in acts:
            valid.append(c * 9 + f)
        return valid

    def decode_action(self, action):
        c_idx = action // 9
        f_idx = action % 9
        return c_idx, f_idx

    def get_state_vector(self):
        encodings = []
        for i in range(MAX_HAND_SIZE):
            if i < len(self.state.hands["player"]):
                enc = encode_card_full(self.state.hands["player"][i],
                                       deposited=False, owner=None, flag=None)
            else:
                enc = np.zeros(NBR_BITS, dtype=np.int32)
            encodings.append(enc)
        for i in range(MAX_HAND_SIZE):
            if i < len(self.state.hands["opponent"]):
                enc = encode_card_full(self.state.hands["opponent"][i],
                                       deposited=False, owner=None, flag=None)
            else:
                enc = np.zeros(NBR_BITS, dtype=np.int32)
            encodings.append(enc)
        for flag_idx, flag in enumerate(self.state.flags):
            for i in range(3):
                if i < len(flag.slots["player"]):
                    enc = encode_card_full(flag.slots["player"][i],
                                           deposited=True, owner="player", flag=flag_idx)
                else:
                    enc = np.zeros(NBR_BITS, dtype=np.int32)
                encodings.append(enc)
            for i in range(3):
                if i < len(flag.slots["opponent"]):
                    enc = encode_card_full(flag.slots["opponent"][i],
                                           deposited=True, owner="opponent", flag=flag_idx)
                else:
                    enc = np.zeros(NBR_BITS, dtype=np.int32)
                encodings.append(enc)
        state_vector = np.concatenate(encodings)
        return state_vector