import random
from dataclasses import dataclass

from p25_hackathon.livingbeings import Sheep, Wolf
from p25_hackathon.grid import Grid

@dataclass(frozen=True)
class SimConfig:
    """Tous les paramètres de la simulation (facile à modifier / tester)."""

    grid_size: int = 30
    initial_sheep: int = 50
    initial_wolves: int = 10
    initial_grass_coverage: float = 0.30

    sheep_initial_energy: int = 20
    wolf_initial_energy: int = 40
    sheep_energy_from_grass: int = 15
    wolf_energy_from_sheep: int = 35
    sheep_energy_loss_per_turn: int = 1
    wolf_energy_loss_per_turn: int = 2

    sheep_reproduction_threshold: int = 50
    wolf_reproduction_threshold: int = 80
    reproduction_energy_cost: int = 20

    sheep_max_age: int = 50
    wolf_max_age: int = 40

    grass_growth_probability: float = 0.08
    grass_regrowth_time: int = 7

    max_turns: int = 500
    delay_s: float = 0.05
    use_color: bool = True

class Simulation:
    """Orchestre les tours.

    Le choix d'implémentation pour éviter les conflits :
    - On traite les animaux dans un ordre aléatoire à chaque phase.
    - Les mouvements échouent si la destination est occupée.
    """

    def _init_(self, config: SimConfig, seed: int | None) -> None:
        self._cfg = config
        self._rng = random.Random(seed)
        self._grid = Grid(size=config.grid_size, grass_regrow_time=config.grass_regrowth_time)
        self._turn = 0

    @property
    def grid(self) -> Grid:
        return self._grid

    @property
    def turn(self) -> int:
        return self._turn

    def initialize(self) -> None:
        """Placement initial : herbe, puis moutons, puis loups."""
        self._grid.place_grass_random(self._cfg.initial_grass_coverage, self._rng)

        for _ in range(self._cfg.initial_sheep):
            if not self._grid.spawn_animal_random(Sheep(energy=self._cfg.sheep_initial_energy), self._rng):
                break

        for _ in range(self._cfg.initial_wolves):
            if not self._grid.spawn_animal_random(Wolf(energy=self._cfg.wolf_initial_energy), self._rng):
                break

        s, w, g = self._grid.count()

    def step(self) -> None:
        """Exécute un tour complet."""
        self._turn += 1

        # 1) Vieillir
        self._increment_ages()

        # 2) Mise à jour de l'herbe
        self._grid.tick_grass(self._cfg.grass_growth_probability, self._rng)

        # 3) Phase moutons
        self._sheep_phase()

        # 4) Phase loups
        self._wolf_phase()

        # 5) Mort (énergie / âge)
        self._remove_dead()

        # 6) Reproduction
        self._reproduction()

    def _increment_ages(self) -> None:
        for (x, y) in self._all_animal_positions_shuffled():
            a = self._grid.cell(x, y).animal
            if a is not None:
                a.increment_age()

    def _sheep_phase(self) -> None:
        for (x, y) in self._positions_of_sheep_shuffled():
            sheep = self._grid.cell(x, y).animal
            if not isinstance(sheep, Sheep):
                continue  # peut avoir bougé / été mangé

            # Stratégie simple :
            # - si herbe adjacente libre : s'y déplacer
            # - sinon : déplacement aléatoire vers une case libre
            target = self._pick_adjacent_grass(x, y)
            if target is None:
                target = self._pick_adjacent_free(x, y)

            if target is not None:
                self._grid.move_animal((x, y), target)
                x, y = target

            # Mange l'herbe seulement si elle est sur la même case
            if self._grid.eat_grass_if_present(x, y):
                sheep.energy += self._cfg.sheep_energy_from_grass

            # Coût énergétique du tour
            sheep.lose_energy(self._cfg.sheep_energy_loss_per_turn)

    def _wolf_phase(self) -> None:
        for (x, y) in self._positions_of_wolves_shuffled():
            wolf = self._grid.cell(x, y).animal
            if not isinstance(wolf, Wolf):
                continue

            # Si un mouton est adjacent : le manger puis se déplacer sur sa case
            sheep_target = self._pick_adjacent_sheep(x, y)
            if sheep_target is not None:
                sx, sy = sheep_target
                self._grid.remove_animal(sx, sy)
                wolf.energy += self._cfg.wolf_energy_from_sheep
                self._grid.move_animal((x, y), (sx, sy))
                x, y = sx, sy
            else:
                # Sinon déplacement aléatoire
                target = self._pick_adjacent_free(x, y)
                if target is not None:
                    self._grid.move_animal((x, y), target)

            wolf.lose_energy(self._cfg.wolf_energy_loss_per_turn)

    def _remove_dead(self) -> None:
        for (x, y) in self._all_animal_positions_shuffled():
            a = self._grid.cell(x, y).animal
            if a is None:
                continue

            if isinstance(a, Sheep):
                dead = (a.energy <= 0) or (a.age > self._cfg.sheep_max_age)
            elif isinstance(a, Wolf):
                dead = (a.energy <= 0) or (a.age > self._cfg.wolf_max_age)
            else:
                dead = False

            if dead:
                self._grid.remove_animal(x, y)

    def _reproduction(self) -> None:
        # Reproduction moutons
        for (x, y) in self._positions_of_sheep_shuffled():
            sheep = self._grid.cell(x, y).animal
            if not isinstance(sheep, Sheep):
                continue
            if sheep.energy > self._cfg.sheep_reproduction_threshold:
                sheep.energy -= self._cfg.reproduction_energy_cost
                self._grid.try_reproduce((x, y), Sheep(energy=self._cfg.sheep_initial_energy), self._rng)

        # Reproduction loups
        for (x, y) in self._positions_of_wolves_shuffled():
            wolf = self._grid.cell(x, y).animal
            if not isinstance(wolf, Wolf):
                continue
            if wolf.energy > self._cfg.wolf_reproduction_threshold:
                wolf.energy -= self._cfg.reproduction_energy_cost
                self._grid.try_reproduce((x, y), Wolf(energy=self._cfg.wolf_initial_energy), self._rng)

    def should_stop(self) -> bool:
        # Arrêt si max tours ou extinction totale
        if self._turn >= self._cfg.max_turns:
            return True
        s, w, _g = self._grid.count()
        return (s + w) == 0

    # --- Helpers (tirages aléatoires pour casser les biais d'ordre) ---

    def _all_animal_positions_shuffled(self) -> list[tuple[int, int]]:
        positions: list[tuple[int, int]] = []
        for y in range(self._grid.size):
            for x in range(self._grid.size):
                if self._grid.cell(x, y).animal is not None:
                    positions.append((x, y))
        self._rng.shuffle(positions)
        return positions

    def _positions_of_sheep_shuffled(self) -> list[tuple[int, int]]:
        positions = self._grid.positions_of(Sheep)
        self._rng.shuffle(positions)
        return positions

    def _positions_of_wolves_shuffled(self) -> list[tuple[int, int]]:
        positions = self._grid.positions_of(Wolf)
        self._rng.shuffle(positions)
        return positions

    def _pick_adjacent_free(self, x: int, y: int) -> tuple[int, int] | None:
        options = [
            (nx, ny)
            for (nx, ny) in self._grid.neighbors4(x, y)
            if self._grid.cell(nx, ny).animal is None
        ]
        if not options:
            return None
        return self._rng.choice(options)

    def _pick_adjacent_grass(self, x: int, y: int) -> tuple[int, int] | None:
        options = [
            (nx, ny)
            for (nx, ny) in self._grid.neighbors4(x, y)
            if self._grid.cell(nx, ny).animal is None and self._grid.cell(nx, ny).grass.present
        ]
        if not options:
            return None
        return self._rng.choice(options)

    def _pick_adjacent_sheep(self, x: int, y: int) -> tuple[int, int] | None:
        options = [
            (nx, ny)
            for (nx, ny) in self._grid.neighbors4(x, y)
            if isinstance(self._grid.cell(nx, ny).animal, Sheep)
        ]
        if not options:
            return None
        return self._rng.choice(options)