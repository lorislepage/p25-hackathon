import pyxel
from typing import Optional

from p25_hackathon.simulation import SimConfig, Simulation


class PyxelApp:
    """Interface Pyxel pour afficher et piloter la simulation."""

    def __init__(self, cfg: SimConfig, seed: Optional[int], cell_px: int, fps: int) -> None:
        self.cfg = cfg
        self.seed = seed
        self.cell_px = cell_px
        self.hud_h = 16  # hauteur bandeau texte
        self.fps = fps
        self.frame_counter = 0
        # Convert delay (seconds) to frames. Ensure at least 1 frame wait.
        self.update_interval = max(1, int(fps * cfg.delay_s))


        self.sim = Simulation(cfg, seed=seed)
        self.sim.initialize()

        w = cfg.grid_size * cell_px
        h = cfg.grid_size * cell_px + self.hud_h

        # Initialisation Pyxel
        pyxel.init(w, h, title="P25 Hackathon — Pyxel", fps=fps)
        pyxel.run(self.update, self.draw)

        # Note: pyxel.run ne retourne pas avant la fermeture de la fenêtre.

    def reset(self) -> None:
        self.sim = Simulation(self.cfg, seed=self.seed)
        self.sim.initialize()

    def update(self) -> None:
        # Quitter
        if pyxel.btnp(pyxel.KEY_ESCAPE):
            pyxel.quit()

        # Pause / step / reset
        if pyxel.btnp(pyxel.KEY_SPACE):
            self.paused = not getattr(self, "paused", False)

        if not hasattr(self, "paused"):
            self.paused = False

        if pyxel.btnp(pyxel.KEY_R):
            self.reset()
            self.paused = False

        # Avancer d'un tour même en pause
        step_once = pyxel.btnp(pyxel.KEY_N)

        # Simulation
        if (not self.paused) or step_once:
            # Control speed: update only if step_once (manual) OR enough frames passed
            self.frame_counter += 1
            if step_once or (self.frame_counter >= self.update_interval):
                self.frame_counter = 0  # Reset
                if not self.sim.should_stop():
                    self.sim.step()
                else:
                    self.paused = True


    def draw(self) -> None:
        # Fond
        pyxel.cls(0)

        self._draw_world()
        self._draw_hud()

    def _draw_world(self) -> None:
        grid = self.sim.grid
        s = self.cell_px

        # Imports locaux (évite d'imposer Pyxel partout)
        from p25_hackathon.livingbeings import Sheep, Wolf  # noqa: PLC0415

        for y in range(self.cfg.grid_size):
            for x in range(self.cfg.grid_size):
                cell = grid.cell(x, y)

                # Couleurs Pyxel (0..15). Choix simples:
                # 0=black, 3=green, 7=white, 8=red, 1=darkblue/dark
                if cell.grass.present:
                    base = 3   # herbe (vert)
                else:
                    base = 4   # vide (marron, requested by user)


                px = x * s
                py_ = y * s

                # Case
                pyxel.rect(px, py_, s, s, base)

                # Animal par-dessus (rectangle plus petit)
                a = cell.animal
                if isinstance(a, Sheep):
                    pyxel.rect(px + s // 4, py_ + s // 4, s // 2, s // 2, 7) # Sheep: White
                elif isinstance(a, Wolf):
                    pyxel.rect(px + s // 4, py_ + s // 4, s // 2, s // 2, 0) # Wolf: Black


    def _draw_hud(self) -> None:
        sheep, wolves, grass = self.sim.grid.count()
        status = "PAUSE" if self.paused else "RUN"
        if self.sim.should_stop():
            status = "STOP"

        y = self.cfg.grid_size * self.cell_px + 2

        line1 = f"Turn {self.sim.turn}/{self.cfg.max_turns} S:{sheep} W:{wolves} G:{grass} {status}"
        line2 = "SPACE pause | N step | R reset | ESC quit"

        pyxel.text(2, y, line1, 7)
        pyxel.text(2, y + 8, line2, 6)


def run_pyxel(cfg: SimConfig, seed: Optional[int], cell_size: int = 8, fps: int = 30) -> int:
    """Point d'entrée Pyxel (semblable à run_pygame)."""
    PyxelApp(cfg=cfg, seed=seed, cell_px=cell_size, fps=fps)
    return 0