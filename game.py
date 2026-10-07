from board import Board, DIFFICULTIES


class Minesweeper:
    def __init__(self, difficulty=None):
        self.board = Board.from_difficulty(difficulty) if difficulty else None

    def choose_difficulty(self):
        names = list(DIFFICULTIES)
        print("Choose difficulty:")
        for i, name in enumerate(names, 1):
            rows, cols, mines = DIFFICULTIES[name]
            print(f"  {i}. {name.capitalize()} ({rows}x{cols}, {mines} mines)")
        while True:
            raw = input("Difficulty [1-3 or name, default 1]: ").strip().lower()
            if raw == "q":
                return None
            if raw == "":
                return names[0]
            if raw in DIFFICULTIES:
                return raw
            if raw.isdigit() and 1 <= int(raw) <= len(names):
                return names[int(raw) - 1]
            print("Please enter 1, 2, 3, easy, medium, hard or q.")

    def display(self, reveal_mines=False):
        b = self.board
        w = len(str(b.cols))
        print("\n   " + " ".join(f"{c + 1:>{w}}" for c in range(b.cols)))
        for r in range(b.rows):
            cells = []
            for c in range(b.cols):
                pos = (r, c)
                if reveal_mines and pos in b.mines:
                    ch = "*"
                elif pos in b.flags:
                    ch = "F"
                elif pos not in b.revealed:
                    ch = "#"
                elif pos in b.mines:
                    ch = "*"
                else:
                    ch = str(b.adjacent_mines(r, c))
                cells.append(f"{ch:>{w}}")
            print(f"{r + 1:2} " + " ".join(cells))

    def run(self):
        print("Minesweeper")
        if self.board is None:
            choice = self.choose_difficulty()
            if choice is None:
                return
            self.board = Board.from_difficulty(choice)
        print("Commands: r row col | f row col | q")
        while True:
            self.display()
            raw = input("> ").strip().lower()
            if raw == "q":
                return
            parts = raw.split()
            if len(parts) != 3 or parts[0] not in {"r", "f"}:
                print("Use r row col or f row col.")
                continue
            try:
                r, c = int(parts[1]) - 1, int(parts[2]) - 1
            except ValueError:
                print("Coordinates must be numbers.")
                continue
            if not self.board.in_bounds(r, c):
                print("Outside the board.")
                continue

            if parts[0] == "f":
                if self.board.toggle_flag((r, c)):
                    state = "placed" if (r, c) in self.board.flags else "removed"
                    print(f"Flag {state} at ({r + 1}, {c + 1}).")
                else:
                    print("Cannot flag a revealed cell.")
                continue

            result = self.board.reveal((r, c))
            if result.status == "flagged":
                print("That cell is flagged. Remove the flag (f row col) before revealing.")
                continue
            if result.status == "already_revealed":
                print("That cell is already revealed.")
                continue
            if result.hit_mine:
                self.display(reveal_mines=True)
                print("BOOM! You hit a mine.")
                return
            print(self.reveal_feedback(r, c, result))
            if self.board.won():
                self.display()
                print("You cleared the board!")
                return

    def reveal_feedback(self, r, c, result):
        """One concise line per reveal command, however far the flood-fill spread."""
        n = result.cells_revealed
        if n == 1:
            adj = self.board.adjacent_mines(r, c)
            detail = "no adjacent mines" if adj == 0 else f"{adj} adjacent mine{'s' if adj != 1 else ''}"
            return f"Revealed 1 cell ({detail})."
        return f"Revealed {n} cells."
