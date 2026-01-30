#!/usr/bin/env python
# Programme pour l'interface en ligne de commande pour le projet de modélisation des écosystèmes (CLI)

import argparse
import sys
import time
import matplotlib.pyplot as plt


from p25_hackathon.grid import Grid
from p25_hackathon.simulation import Simulation, SimConfig
from p25_hackathon.interface import run_pyxel

def build_parser() -> argparse.ArgumentParser:
    """
    Cette fonction définit tous les paramètres que l’utilisateur peut fournir
    lors de l’exécution du programme depuis le terminal.
    """
    parser = argparse.ArgumentParser(
        prog="ecosystem",
        description="Simulation d'écosystème (moutons, loups, herbe) sur une grille ASCII.",
    )

    # Paramètres physiques et numériques de la simulation
    parser.add_argument("--size", type=int, default=30,
                        help="Taille n de la grille n×n (défaut: 30)")
    parser.add_argument("--sheep", type=int, default=50,
                        help="Nombre initial de moutons (défaut: 50)")
    parser.add_argument("--wolves", type=int, default=10,
                        help="Nombre initial de loups (défaut: 10)")
    parser.add_argument("--grass", type=float, default=0.30,
                        help="Couverture initiale d'herbe [0..1] (défaut: 0.30)")
    parser.add_argument("--turns", type=int, default=500,
                        help="Nombre maximum de tours (défaut: 500)")
    parser.add_argument("--delay", type=float, default=0.05,
                        help="Délai entre tours en secondes (défaut: 0.05)")
    parser.add_argument("--seed", type=int, default=None,
                        help="Graine RNG pour rendre la simulation reproductible")
    parser.add_argument("--no-color", action="store_true",
                        help="Désactiver les couleurs ANSI")
    parser.add_argument("-v", action="count", default=0,
                        help="Verbose (ex: -v, -vv)")
    parser.add_argument("--pyxel", action="store_true",
                        help="Lancer l'interface graphique")
    parser.add_argument("--cell-size", type=int, default=8,
                        help="Taille des cellules dans l'interface graphique (défaut: 8)")
    parser.add_argument("--fps", type=int, default=60,
                        help="Nombre d'images par seconde dans l'interface graphique (défaut: 60)")
    return parser

def clear_screen() -> None:
    """
    Efface le terminal et replace le curseur en haut à gauche.

    Utilise des séquences ANSI, compatibles avec la majorité des terminaux.
    """
    sys.stdout.write("\x1b[2J\x1b[H")

def main() -> int:
    """
    Fonction principale de la CLI.
    """
    # Lecture des arguments passés par l’utilisateur
    args = build_parser().parse_args()

    # Construction de la configuration de simulation à partir de la CLI
    # Les paramètres non fournis gardent leur valeur par défaut
    cfg = SimConfig(
        grid_size=args.size,
        initial_sheep=args.sheep,
        initial_wolves=args.wolves,
        initial_grass_coverage=args.grass,
        max_turns=args.turns,
        delay_s=args.delay,
        use_color=not args.no_color,
    )

    if args.pyxel:
        return run_pyxel(cfg, seed=args.seed, cell_size=args.cell_size, fps=args.fps)

    # Création de la simulation avec une graine aléatoire optionnelle
    sim = Simulation(cfg, seed=args.seed)
    sim.initialize()

    # Dictionnaire pour stocker les données de population
    stats = {
        "turns": [],
        "sheep": [],
        "wolves": [],
        "grass": []
    }


    try:
        # Boucle principale de la simulation
        while True:
            # Nettoyage du terminal avant le nouvel affichage
            clear_screen()

            # Comptage des entités pour affichage synthétique
            s, w, g = sim.grid.count()
            print(f"Tour: {sim.turn} | Sheep: {s} | Wolves: {w} | Grass: {g}")

            # Enregistrement des données
            stats["turns"].append(sim.turn)
            stats["sheep"].append(s)
            stats["wolves"].append(w)
            stats["grass"].append(g)


            # Affichage ASCII de la grille
            print(sim.grid.render_ascii(use_color=cfg.use_color))

            # Condition d'arrêt (extinction ou nombre max de tours)
            if sim.should_stop():
                print("\nArrêt: condition atteinte (max tours ou extinction).")
                break

            # Calcul du tour suivant
            sim.step()

            # Pause pour contrôler la vitesse d’animation
            time.sleep(cfg.delay_s)

    except KeyboardInterrupt:
        # Arrêt propre si l'utilisateur interrompt le programme
        print("\nArrêt manuel (Ctrl+C).")

    # Affichage du graphique d'évolution
    print("Génération du graphique d'évolution des populations...")
    plt.figure(figsize=(10, 6))
    plt.plot(stats["turns"], stats["sheep"], label="Moutons", color="blue")
    plt.plot(stats["turns"], stats["wolves"], label="Loups", color="red")
    plt.plot(stats["turns"], stats["grass"], label="Herbe", color="green")
    
    plt.xlabel("Tours")
    plt.ylabel("Population")
    plt.title("Évolution des populations au cours du temps")
    plt.legend()
    plt.grid(True)
    plt.show()

    return 0


if __name__ == "__main__":
    sys.exit(main())