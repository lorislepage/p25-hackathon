# Simulation d’écosystème (Hackathon P25)

Objectif du projet

Ce projet consiste à simuler un écosystème discret sur une grille carrée, composé de :
	•	moutons (S),
	•	loups (W),
	•	herbe (#).

L’objectif est d’étudier l’évolution conjointe de ces populations au cours du temps, en implémentant des règles simples de déplacement, de consommation, de reproduction et de mort.

Le programme est conçu pour être :
	•	simple,
	•	lisible,
	•	reproductible,
	•	exécutable sur n'importe quel ordinateur, en utilisant le package uv.

⸻

**Principe général de la simulation**

La simulation se déroule sur une grille carrée n×n.
Chaque case peut contenir :
	•	de l’herbe,
	•	au plus un animal (mouton ou loup).

À chaque tour de simulation :
	1.	l’herbe pousse ou repousse,
	2.	les moutons se déplacent et mangent l’herbe,
	3.	les loups chassent les moutons,
	4.	les animaux perdent de l’énergie et vieillissent,
	5.	les animaux peuvent mourir,
	6.	les animaux peuvent se reproduire,
	7.	l’état de la grille est affiché dans le terminal.

La simulation s’arrête :
	•	après un nombre maximal de tours,
	•	ou si toutes les populations animales disparaissent.

⸻

**Représentation dans le terminal**

Symboles utilisés :
	•	S : mouton
	•	W : loup
	•	# : herbe
	•	. : case vide

L’affichage est ASCII, directement dans le terminal.

**Représentation dans l'interface**

Couleurs utilisés :
	•	Blanc : mouton
	•	Noir : loup
	•	Vert : herbe
	•	Marron : case vide

⸻

**Structure du projet**

p25-hackathon/
├── pyproject.toml
├── README.md
├── src/
│   └── p25_hackathon/
│       ├── __init__.py
│       ├── main.py        # point d’entrée
│       ├── cli.py         # interface ligne de commande
│       ├── simulation.py # logique temporelle
│       ├── grid.py        # grille et règles spatiales
│       └── livingbeings.py    # animaux et herbe
└── tests/
    ├── test_grid.py
    └── test_reproduction.py

⸻

**Rôle des fichiers**
	•	main.py : lance le programme
	•	cli.py : gère les arguments de la ligne de commande
	•	simulation.py : orchestre les tours de simulation
	•	grid.py : gère la grille, les déplacements et l’herbe
	•	livingbeings.py : définit les animaux et leur état
  •	interface.py : permet d'afficher une interface dynamique, via la bibliothèque pyxel

⸻

**Bibliothèques utilisées**

Uniquement la bibliothèque standard Python :
	•	argparse
	•	logging
	•	random
	•	dataclasses
	•	time
	•	sys

Aucune dépendance externe n’est requise pour exécuter la simulation.

⸻

**Création de l’environnement**

uv init
uv venv
uv pip install pyxel

**Lancement**

Il faut se placer **dans le dossier p25-hackathon**, donc : *cd p25-hackathon*, avant d'exécuter les lignes suivantes.
Pour obtenir **l'interface en ligne de commande** et le tracé de l'évolution des populations : *uv run p25-hackathon-cli*
Pour obtenir **l'interface graphique** via la bibliothèque pyxel : *uv run p25-hackathon-cli --pyxel*

⸻

Paramètres modifiables via la CLI
	•	--size : taille de la grille
	•	--sheep : nombre initial de moutons
	•	--wolves : nombre initial de loups
	•	--grass : couverture initiale d’herbe
	•	--turns : nombre maximal de tours
	•	--delay : délai entre deux tours
	•	--seed : graine aléatoire (reproductibilité)
	•	-v, -vv : verbosité (logging)
... et d'autres paramètres visualibles dans le programme cli.py dans les différents parsers.

Sans arguments, des valeurs par défaut raisonnables sont utilisées.

⸻

Choix de conception
	•	Affichage ASCII pour la portabilité
	•	Données simples (listes, entiers, booléens)
	•	Aucune variable globale
	•	Paramètres centralisés dans une configuration
	•	Séparation claire entre logique et interface

Ces choix garantissent un code facile à comprendre, tester et évaluer.

⸻

Arrêt de la simulation
	•	automatique (extinction ou nombre maximal de tours)
	•	manuel via Ctrl + C

⸻

**Auteur**

Projet réalisé dans le cadre du hackathon P25 par **Anna Bergougnoux-Santini**, **Agathe Buchert**, **Christiane Hebey** et **Loris Lepage**
