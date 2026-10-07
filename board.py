import random
from collections import namedtuple

DEFAULT_ROWS = 6
DEFAULT_COLS = 6
DEFAULT_MINES = 6

# Difficulty presets kept in memory: name -> (rows, cols, mines)
DIFFICULTIES = {
    "easy": (6, 6, 6),
    "medium": (9, 9, 10),
    "hard": (16, 16, 40),
}

# Outcome of ONE player reveal action (not of internal flood-fill steps).
# status: "ok" | "mine" | "flagged" | "already_revealed" | "invalid"
RevealResult = namedtuple("RevealResult", "status cells_revealed hit_mine")


class Board:
    def __init__(self, rows=DEFAULT_ROWS, cols=DEFAULT_COLS, mines=DEFAULT_MINES):
        if rows < 1 or cols < 1 or not 0 <= mines < rows * cols:
            raise ValueError("Invalid board size or mine count.")
        self.rows = rows
        self.cols = cols
        self.mine_total = mines
        self.mines = self._build_mines()
        self.revealed = set()
        self.flags = set()

    @classmethod
    def from_difficulty(cls, name):
        rows, cols, mines = DIFFICULTIES[name.lower()]
        return cls(rows, cols, mines)

    def _build_mines(self):
        cells = [(r, c) for r in range(self.rows) for c in range(self.cols)]
        return set(random.sample(cells, self.mine_total))

    def in_bounds(self, r, c):
        return 0 <= r < self.rows and 0 <= c < self.cols

    def neighbors(self, r, c):
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if self.in_bounds(nr, nc):
                    yield nr, nc

    def adjacent_mines(self, r, c):
        return sum(pos in self.mines for pos in self.neighbors(r, c))

    def reveal(self, start):
        """Reveal `start` (flood-filling zero regions) and return one RevealResult."""
        if not self.in_bounds(*start):
            return RevealResult("invalid", 0, False)
        if start in self.flags:
            return RevealResult("flagged", 0, False)
        if start in self.revealed:
            return RevealResult("already_revealed", 0, False)
        stack = [start]
        hit_mine = False
        cells_revealed = 0
        while stack:
            pos = stack.pop()
            if pos in self.revealed or pos in self.flags:
                continue
            r, c = pos
            self.revealed.add(pos)
            if pos in self.mines:
                hit_mine = True
                continue
            cells_revealed += 1
            if self.adjacent_mines(r, c) == 0:
                stack.extend(n for n in self.neighbors(r, c) if n not in self.revealed)
        status = "mine" if hit_mine else "ok"
        return RevealResult(status, cells_revealed, hit_mine)

    def toggle_flag(self, pos):
        if not self.in_bounds(*pos) or pos in self.revealed:
            return False
        if pos in self.flags:
            self.flags.remove(pos)
        else:
            self.flags.add(pos)
        return True

    def won(self):
        # Win only when every non-mine cell has been revealed and no mine has.
        safe_cells = {
            (r, c)
            for r in range(self.rows)
            for c in range(self.cols)
            if (r, c) not in self.mines
        }
        return safe_cells <= self.revealed and not (self.mines & self.revealed)
