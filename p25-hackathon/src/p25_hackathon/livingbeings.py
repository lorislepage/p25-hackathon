from dataclasses import dataclass


@dataclass
class Animal:
    """Classe de base pour les animaux.
    La position est gérée par la grille (Grid), ici on garde seulement l'état.
    """
    energy: int
    age: int = 0

    def increment_age(self) -> None:
        self.age += 1

    def lose_energy(self, amount: int) -> None:
        self.energy -= amount


@dataclass
class Sheep(Animal):
    """Mouton."""
    pass


@dataclass
class Wolf(Animal):
    """Loup."""
    pass


@dataclass
class GrassCell:
    """État de l'herbe pour une cellule.

    present : herbe disponible
    regrow_timer : si l'herbe a été mangée, compteur avant repousse
    """
    present: bool
    regrow_timer: int = 0

    def tick(self) -> None: 
        if self.regrow_timer > 0:
            self.regrow_timer -= 1
            if self.regrow_timer == 0:
                self.present = True

    def eat(self, regrow_time: int) -> None:
        self.present = False
        self.regrow_timer = regrow_time