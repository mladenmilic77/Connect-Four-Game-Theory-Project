from board import Board

class HumanAgent:
    """
    CLI-backed human player: asks for a column in the terminal.
    """
    def __init__(self, name: str | None = None):
        """
        Args:
            name: Optional display name (default: "Paul Human").
        """
        self.name = "Paul Human" if not name else name

    def select_move(self, board: Board, player: int) -> int:
        """
        Ask the user to choose a valid column.
        Args:
            board: Current game board.
            player: Player number (1 or 2).
        Returns:
            int: Column index chosen by the user.
        """
        legal_moves = [c for c, true in enumerate(board.valid_moves()) if true]
        print(f"{self.name} (P{player}) — valid columns: {legal_moves}")
        while True:
            try:
                col = int(input("Choose column: "))
                return col
            except Exception:
                print("Invalid input, try again.")