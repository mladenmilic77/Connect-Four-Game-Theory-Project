from board import Board

class GameController:
    """
    Game controller for Connect Four.
    Manages the game flow on top of a Board:
    - Tracks whose turn it is,
    - Applies moves and switches players,
    - Detects terminal states (win or draw).
    Attributes:
        board (Board): The game board.
        turn (int): Current player (1 or 2).
        winner_cache (int): 0 = no winner, 1 = player 1, 2 = player 2.
        """
    def __init__(self, board = None):
        """
        Initialize the controller with a board.
        Args:
            board (Board | None): Existing board or None for a new one.
        """
        self.board = Board() if board is None else board
        self.turn = 1
        self.winner_cache = 0

    def reset(self):
        """Reset the board, set Player 1 to start, clear winner cache."""
        self.board.reset()
        self.turn = 1
        self.winner_cache = 0

    def current_player(self) -> int:
        """Return the current player (1 or 2)."""
        return self.turn

    def is_terminal(self) -> bool:
        """
        Return True if the game is over (win or draw).
        Caches the winner if one is found.
        """
        w = self.board.winner()
        if w:
            self.winner_cache = w
            return True
        return self.board.is_full()

    def play(self, col) -> str:
        """
        Drop a token in the given column for the current player.
        Returns:
            "Winner: Player X", "Draw", or "Next: Player Y".
        Raises:
            IndexError, ValueError, RuntimeError from Board.drop().
        """
        self.board.drop(col, self.turn)
        if self.is_terminal():
            return f"Winner: Player {self.winner_cache}" if self.winner_cache else "Draw"
        self.turn = 2 if self.turn == 1 else 1
        return f"Next: Player {self.current_player()}"
