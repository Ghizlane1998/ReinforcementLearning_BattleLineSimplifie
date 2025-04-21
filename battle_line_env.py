import random
import numpy as np
from battle_line_game import BattleLineGame

class BattleLineEnv:
    def __init__(self, opponent_policy="random"):
        self.game = BattleLineGame()
        self.opponent_policy = opponent_policy
        self.prev_flag_winners = [None] * 9

    def reset(self):
        self.game = BattleLineGame()
        self.prev_flag_winners = [None] * 9
        return self.game.get_state_vector()

    def get_valid_actions(self):
        return self.game.get_valid_actions()

    def step(self, action):
        valid_actions = self.get_valid_actions()
        
        if not valid_actions:
            winner = self.game.state.check_game_over()
            final_reward = 50.0 if winner == "player" else -50.0 if winner == "opponent" else 0.0
            final_reward = max(min(final_reward, 1), -1)
            return self.game.get_state_vector(), final_reward, True, {"error": "No valid actions"}

        if action not in valid_actions:
            return self.game.get_state_vector(), -0.1, True, {"error": "Invalid action selected"}

        card_index, flag_index = self.game.decode_action(action)
        valid, winner, error = self.game.step("player", card_index, flag_index)
        
        if not valid:
            return self.game.get_state_vector(), -0.1, True, {"error": error}

        reward = 0.01
        reward += self.check_new_flag_captures()

        if winner is not None:
            final_reward = 50.0 if winner == "player" else -50.0 if winner == "opponent" else 0.0
            final_reward = max(min(final_reward, 1), -1)
            return self.game.get_state_vector(), reward + final_reward, True, {}

        opp_actions = self.game.state.available_actions("opponent")
        if opp_actions:
            opp_choice = random.choice(opp_actions)
            c_idx, f_idx = opp_choice
            self.game.step("opponent", c_idx, f_idx)

        reward += self.check_new_flag_captures()

        winner = self.game.state.check_game_over()
        if winner is not None:
            final_reward = 50.0 if winner == "player" else -50.0 if winner == "opponent" else 0.0
            final_reward = max(min(final_reward, 1), -1)
            return self.game.get_state_vector(), reward + final_reward, True, {}

        reward = max(min(reward, 1), -1)

        return self.game.get_state_vector(), reward, False, {}

    def check_new_flag_captures(self):
        flag_capture_reward = 0.0
        for i, f in enumerate(self.game.state.flags):
            if f.winner != self.prev_flag_winners[i]:
                if f.winner == "player":
                    flag_capture_reward += 0.2
                elif f.winner == "opponent":
                    flag_capture_reward -= 0.2
                self.prev_flag_winners[i] = f.winner
        return flag_capture_reward

    def render(self):
        self.game.render()