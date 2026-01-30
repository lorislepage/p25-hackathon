import random
from dataclasses import dataclass
from typing import Optional

from p25_hackathon.livingbeings import GrassCell, Sheep, Wolf, Animal

@dataclass
class Cell:
    """On représente une cellule de la grille par de l'herbe et éventuellement un animal."""
    grass: GrassCell
    animal: Optional[Animal] = None

class Grid:
    """La grille de taille (n,n), pas de diagonales"""

    def __init__(self, size: int, grass_regrow_time: int) -> None:
        if size <= 0:
            raise ValueError("la taille doit être > 0")
        if grass_regrow_time <= 0:
            raise ValueError("la repousse doit être > 0")

        self._size = size
        self._grass_regrow_time = grass_regrow_time
        
        self._cells: list[list[Cell]] = [
            [
               Cell(grass=GrassCell(present=False)) for i in range(size)
            ]
            for i in range(size)
        ]

    @property
    def size(self) -> int:
        """taille de self"""
        return self._size

    def in_bounds(self, x:int, y: int)->bool :
        """vérifie si on sort pas des bords"""
        return (0 <= x < self._size and 0 <= y < self._size)

    def neighbors4(self, x: int, y: int) -> list[tuple[int, int]]:
        """regarde quels sont les voisins possibles"""
        candidats = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
        l=[]
        for (i,j) in candidats:
            if self.in_bounds(i,j):
                l.append((i,j))
        return l

    def cell(self, x: int, y: int) -> Cell:
        """renvoie la cellule sur laquelle on se trouve"""
        return self._cells[y][x]

    def place_grass_random(self, coverage: float, rng: random.Random) -> None:
        """ """
        for y in range(self._size):
            for x in range(self._size):
                if rng.random() < coverage:
                    self.cell(x, y).grass.present = True

    def spawn_animal_random(self, animal: Animal, rng: random.Random) -> bool:
        """Met un animal sur une case libre, si il y en a"""
        positionslibres=[]
        for y in range(self._size):
            for x in range(self._size):
                if self.cell(x,y).animal is None:
                    positionslibres.append((x,y))
        
        if not positionslibres:
            return False

        x, y = rng.choice(positionslibres)
        self.cell(x, y).animal = animal
        return True

    def positions_of(self, kind: type[Animal]) -> list[tuple[int, int]]:
        """ liste des positions d'un type particulier d'animaux  """
        l: list[tuple[int, int]] = []
        for y in range(self._size):
            for x in range(self._size):
                a = self.cell(x, y).animal
                if isinstance(a,kind):
                    l.append((x, y))
        return l

    def tick_grass(self, grass_growth_probability: float, rng: random.Random) -> None:
        """Met à jour l'herbe : décrémente les timers de repousse et fait pousser aléatoirement sur les cellules libres
        """
        if not (0.0 <= grass_growth_probability <= 1.0):
            raise ValueError("La proba doit être dans [0, 1] !")

        for y in range(self._size):
            for x in range(self._size):
                c = self.cell(x, y)
                c.grass.tick()

                if c.grass.present==False and c.grass.regrow_timer == 0:
                    if rng.random() < grass_growth_probability:
                        c.grass.present = True

    def move_animal(self, dep: tuple[int, int], arr: tuple[int, int]) -> bool:
        """déplace un animal si la destination est libre"""
        fx, fy = dep
        tx, ty = arr
        if not (self.in_bounds(fx, fy) and self.in_bounds(tx, ty)):
            return False

        source = self.cell(fx, fy)
        dest = self.cell(tx, ty)

        if source.animal is None:
            return False
        if dest.animal is not None:
            return False

        dest.animal = source.animal
        source.animal = None
        return True

    def remove_animal(self, x: int, y: int) -> None:
        """enlève un animal mort"""
        self.cell(x, y).animal = None

    def try_reproduce(self, parent: tuple[int, int], baby: Animal, rng: random.Random) -> bool:
        """assure la reproduction des espèces"""
        x, y = parent
        options=[]
        for (i,j) in self.neighbors4(x,y):
            if self.cell(i,j).animal is None:
                options.append((i,j))
        
        if not options:
            return False

        bx, by = rng.choice(options)
        self.cell(bx, by).animal = baby
        return True

    def eat_grass_if_present(self, x: int, y: int) -> bool:
        c = self.cell(x, y)
        if c.grass.present:
            c.grass.eat(regrow_time=self._grass_regrow_time)
            return True
        return False

    def render_ascii(self, use_color: bool) -> str:
        lignes: list[str] = []
        for y in range(self._size):
            row_chars: list[str] = []
            for x in range(self._size):
                c = self.cell(x, y)
                ch = "."
                if c.grass.present:
                    ch = "#"
                if isinstance(c.animal, Sheep):
                    ch = "S"
                elif isinstance(c.animal, Wolf):
                    ch = "W"
                row_chars.append(self._colorize(ch, use_color))

            lignes.append("".join(row_chars))
        return "\n".join(lignes)

    def count(self) -> tuple[int, int, int]:
        sheep = 0
        wolf = 0
        grass = 0

        for y in range(self._size):
            for x in range(self._size):
                c = self.cell(x, y)

                if c.grass.present:
                    grass += 1

                if isinstance(c.animal, Sheep):
                    sheep += 1
                elif isinstance(c.animal, Wolf):
                    wolf += 1

        return sheep, wolf, grass

    def _colorize(self, ch: str, use_color: bool) -> str:
        if not use_color:
            return ch

        if ch == "S":
            return f"\x1b[92m{ch}\x1b[0m"
        if ch == "W":
            return f"\x1b[91m{ch}\x1b[0m"
        if ch == "#":
            return f"\x1b[32m{ch}\x1b[0m"
        return ch

def main() -> None:
    print("Testing Grid...")
    g = Grid(size=10, grass_regrow_time=5)
    g.place_grass_random(0.5, random.Random(42))
    print(g.render_ascii(use_color=True))
    print("Grid test complete.")

if __name__ == "__main__":
    main()