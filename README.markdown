# Battle Line Game

Bienvenue dans **Battle Line**, une implémentation numérique du jeu de cartes stratégique pour deux joueurs. Ce projet comprend une interface graphique interactive, un environnement pour l'entraînement d'IA, et un agent DQN (Deep Q-Network) pour jouer contre un adversaire humain ou aléatoire.

## Table des Matières

 1. Aperçu
 2. Fonctionnalités
 3. Prérequis
 4. Installation
 5. Structure du Projet
 6. Utilisation
 7. Modes de Jeu
 8. Règles du Jeu
 9. Personnalisation
10. Dépannage
11. Contribuer
12. Licence

## Aperçu

Battle Line est un jeu de cartes où deux joueurs s'affrontent pour capturer des drapeaux en formant des combinaisons de cartes (par exemple, suites, brelans, couleurs). Ce projet propose une version numérique avec une interface graphique développée avec Tkinter, intégrant des effets sonores, de la musique de fond, et une IA entraînée via un agent DQN.

## Fonctionnalités

- **Interface graphique** : Déplacez les cartes par glisser-déposer pour jouer sur les drapeaux.
- **Menu de sélection** : Lancez le jeu via `menu.py` pour choisir le mode de jeu.
- **Modes de jeu** : Humain vs Humain, Humain vs IA, Humain vs Aléatoire, Aléatoire vs Aléatoire.
- **Effets sonores** : Sons de clic et de victoire pour une expérience immersive.
- **Musique de fond** : Musique tirée de Pokemon Omega Ruby & Alpha Sapphire.
- **Environnement d'entraînement** : Compatible avec l'apprentissage par renforcement via `BattleLineEnv`.
- **Agent IA** : Un modèle DQN pré-entraîné pour jouer de manière stratégique.

## Prérequis

- Python 3.8 ou supérieur
- Bibliothèques Python :
  - `numpy`
  - `torch`
  - `pillow`
  - `pygame`
  - `tkinter`
- Dossiers requis :
  - `images/` : pour les cartes et drapeaux
  - `music/` : pour les fichiers audio (clic, victoire, musique)
  - `model/model.pth` : modèle DQN pré-entraîné

## Installation

```bash
git clone https://github.com/Ghizlane1998/ReinforcementLearning.git
cd ReinforcementLearning

# Créer un environnement virtuel (optionnel)
python -m venv venv
source venv/bin/activate  # Windows : venv\Scripts\activate

# Installer les dépendances
pip install numpy torch pillow pygame
```

## Structure du Projet

```
ReinforcementLearning/
├── agent_aleatoire.py         # Mode aléatoire vs aléatoire
├── agent_human.py             # Mode humain vs humain
├── battle_line_env.py         # Environnement RL
├── battle_line_game.py        # Logique du jeu
├── dqn_agent.py               # Agent IA
├── HumainVS_IA.py             # Interface IA vs humain
├── menu.py                    # Menu principal
├── images/                    # Ressources visuelles
├── music/                     # Ressources audio
├── model/                     # Modèle DQN entraîné
├── LICENSE
└── README.md
```

## Utilisation

1. Lancer le menu principal :
   ```bash
   python menu.py
   ```

2. Choisir un mode de jeu :
   - **Humain vs Humain**
   - **Humain vs IA** (avec agent DQN)
   - **Humain vs Aléatoire**
   - **Aléatoire vs Aléatoire**

3. Jouer :
   - Glisser une carte vers un drapeau pour la jouer
   - Le score s'affiche en bas de l'écran
   - Une animation annonce le gagnant avec un bouton **Retour au menu principal**

## Modes de Jeu

- **Humain vs Humain** : 2 joueurs humains sur la même machine
- **Humain vs IA** : Agent DQN qui réfléchit à ses actions
- **Humain vs Aléatoire** : L'adversaire joue au hasard
- **Aléatoire vs Aléatoire** : Simule une partie automatiquement

## Règles du Jeu

- **Objectif** : Capturer 5 drapeaux ou 3 drapeaux consécutifs
- **Cartes** : 60 cartes (6 couleurs x 10 valeurs)
- **Mains** : 7 cartes par joueur au début
- **Drapeaux** : 9, au centre
- **Chaque joueur peut placer jusqu'à 3 cartes par drapeau**
- **Combinaisons (du plus fort au plus faible)** :
  - Brelan
  - Suite couleur
  - Couleur
  - Suite
  - Paire
  - Carte haute

## Personnalisation

- **Images** : Modifier `images/`
- **Sons** : Modifier `music/`
- **IA** : Réentraîner l'agent via `dqn_agent.py` et mettre à jour `model/model.pth`

## Dépannage

- Problèmes audio : vérifiez `pygame` et votre configuration audio
- Images manquantes : assurez-vous que tous les fichiers `.png` sont dans `images/`
- Erreurs IA : `model.pth` doit être présent dans `model/`

## Contribuer

1. Fork du dépôt
2. Nouvelle branche : `git checkout -b feature/...`
3. Push et Pull Request

## Licence

Projet sous licence MIT. Voir `LICENSE`.

---

Pour toute question ou suggestion, ouvrez une issue ou contactez [Ghizlane1998](https://github.com/Ghizlane1998/ReinforcementLearning).

