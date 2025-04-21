from matplotlib import pyplot as plt
import numpy as np
from battle_line_env import BattleLineEnv
from dqn_agent import DQNAgent

DIM_ETAT = 1836
DIM_ACTION = 63

def entrainer_agent(episodes=1000):
    env = BattleLineEnv(opponent_policy="random")
    agent = DQNAgent(
        state_dim=DIM_ETAT,
        action_dim=DIM_ACTION,
        lr=1e-5,
        gamma=0.99,
        epsilon=1.0,
        epsilon_min=0.05,
        epsilon_decay=0.995,
        batch_size=64,
        tau=0.005
    )
    victoires = 0
    recompense_totale = 0.0
    stats = {
        "episodes": [],
        "recompenses_moyennes": [],
        "taux_victoire": [],
        "epsilons": []
    }
    for ep in range(episodes):
        etat = env.reset()
        termine = False
        recompense_ep = 0.0
        while not termine:
            actions_valides = env.get_valid_actions()
            if not actions_valides:
                gagnant = env.game.state.check_game_over()
                recompense_finale = 100.0 if gagnant == "player" else -100.0 if gagnant == "opponent" else 0.0
                agent.store_transition(etat, 0, recompense_finale, etat, True)
                recompense_ep += recompense_finale
                termine = True
                break
            action = agent.select_action(etat, actions_valides)
            etat_suivant, recompense, termine, info = env.step(action)
            agent.store_transition(etat, action, recompense, etat_suivant, termine)
            agent.update()
            etat = etat_suivant
            recompense_ep += recompense
        gagnant = env.game.state.check_game_over()
        if gagnant == "player":
            victoires += 1
        recompense_totale += recompense_ep
        if (ep + 1) % 50 == 0:
            taux_victoire_moyen = victoires / 50
            recompense_moyenne = recompense_totale / 50
            print(f"Épisode {ep + 1}/{episodes} | Taux de victoire : {taux_victoire_moyen:.2f} | Epsilon : {agent.epsilon:.2f} | Récompense moyenne : {recompense_moyenne:.2f}")
            stats["episodes"].append(ep + 1)
            stats["taux_victoire"].append(taux_victoire_moyen)
            stats["recompenses_moyennes"].append(recompense_moyenne)
            stats["epsilons"].append(agent.epsilon)
            victoires = 0
            recompense_totale = 0.0
    agent.policy_net.save()
    return stats

def jouer_partie():
    env = BattleLineEnv(opponent_policy="random")
    etat = env.reset()
    termine = False
    while not termine:
        env.render()
        actions_valides = env.get_valid_actions()
        print("Actions valides :", actions_valides)
        try:
            action = int(input("Entrez une action (index_carte * 9 + index_drapeau) : "))
        except ValueError:
            print("Entrée invalide. Réessayez.")
            continue
        if action not in actions_valides:
            print("Action invalide. Réessayez.")
            continue
        etat, recompense, termine, info = env.step(action)
    env.render()
    gagnant_final = env.game.state.check_game_over()
    if gagnant_final == "player":
        print("Vous gagnez !")
    elif gagnant_final == "opponent":
        print("Vous perdez !")
    else:
        print("Égalité !")

if __name__ == "__main__":
    mode = input("Entrez le mode (entrainer/jouer) : ").strip().lower()
    if mode == "entrainer":
        stats = entrainer_agent(episodes=1000)
        plt.figure(figsize=(12, 5))
        plt.subplot(1, 2, 1)
        plt.plot(stats["episodes"], stats["taux_victoire"], marker='o')
        plt.title("Taux de Victoire")
        plt.xlabel("Épisodes")
        plt.ylabel("Taux de Victoire")
        plt.grid(True)
        plt.subplot(1, 2, 2)
        plt.plot(stats["episodes"], stats["recompenses_moyennes"], marker='o', color="orange")
        plt.title("Récompense Moyenne")
        plt.xlabel("Épisodes")
        plt.ylabel("Récompense Moyenne")
        plt.grid(True)
        plt.tight_layout()
        plt.show()
    elif mode == "jouer":
        jouer_partie()
    else:
        print("Mode inconnu. Choisissez 'entrainer' ou 'jouer'.")