import random
from board import Board

class RandomAgent:
    """
    Simple agent that picks a random valid column in Connect Four.
    """
    def __init__(self, name: str | None = None, seed: int | None = None):
        """
        Create a RandomAgent.
        Args:
            name: Optional name (default: "Marlon Random").
            seed: Random seed for reproducibility (default: None).
            player: Optional player assignment (1 or 2), not used here.
        """
        self.name = "Marlon Random" if name is None else name
        self.rng = random.Random() if seed is None else random.Random(seed)

    def select_move(self, board: Board, player: int) -> int:
        """
        Return a random legal column index.
        Args:
            board: Current game board.
            player: Player number (1 or 2), unused but kept for compatibility.
        Returns:
            int: Column index.
        Raises:
            RuntimeError: If no legal moves exist.
        """
        legal_moves = [c for c, true in enumerate(board.valid_moves()) if true]
        if not legal_moves:
            raise RuntimeError("No legal moves available.")
        return self.rng.choice(legal_moves)

