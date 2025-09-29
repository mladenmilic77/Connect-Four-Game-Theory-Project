# TODO Make additional class for constants
ROWS = 6
COLS = 7
class Board:
    """
    Connect Four board and rules.
    Attributes:
        rows (int): Number of rows in the board (default 6).
        cols (int): Number of columns in the board (default 7).
        grid (list[list[int]]): 2D list representing the board.
            0 = empty cell, 1 = player 1, 2 = player 2.
        moves (int): Total number of moves played so far.
    Returns convention:
        winner() -> int:
            0 : no winner
            1 : player 1 wins
            2 : player 2 wins
    """
    def __init__(self, rows = ROWS, cols = COLS):
        """
        Initialize an empty board of size rows x cols.
        Args:
        rows (int): Number of rows (default 6).
        cols (int): Number of columns (default 7).
        """
        self.rows = rows
        self.cols = cols
        self.grid = [[0 for _ in range(cols)] for _ in range(rows)]
        self.moves = 0

    def reset(self):
        """
        Clear the board and reset the move counter.
        After calling this method, all cells are set to 0
        and moves is reset to 0.
        """
        self.grid = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.moves = 0

    def valid_moves(self) -> list[bool]:
        """
        Return a boolean mask per column indicating if a move is legal.
        Returns:
        list[bool]: True for each column where the top cell is empty,
        False where the column is full.
        """
        return [self.grid[0][c] == 0 for c in range(self.cols)]

    def drop(self, col: int, player: int) -> bool:
        """
        Drop a token for `player` (must be 1 or 2) into column `col`.
        Args:
            col (int): Index of the column (0-based).
            player (int): Player number (1 or 2).
        Raises:
            ValueError: if player is not 1 or 2, or if the column is full.
            IndexError: if `col` is out of range [0, cols-1].
        Returns:
            True when the piece is successfully placed.
        """
        if player not in (1, 2):
            raise ValueError(f"Invalid player {player}. Player must be 1 or 2.")
        if not (0 <= col < self.cols):
            raise IndexError(f"Column {col} is out of range (0-{self.cols-1})")
        if self.grid[0][col] != 0:
            raise ValueError(f"Column {col} is full")

        for r in range(self.rows - 1, -1, -1):
            if self.grid[r][col] == 0:
                self.grid[r][col] = player
                self.moves += 1
                return True

        raise RuntimeError("No empty cell found despite top-cell check")

    def is_full(self) -> bool:
        """Return True if the board is completely filled (no more valid moves)."""
        return self.moves >= self.rows * self.cols

    def winner(self) -> int:
        """
        Check the board for any 4-in-a-row (vertical, horizontal, or diagonal).
        Returns:
            0 if no winner,
            1 if player 1 has four in a row,
            2 if player 2 has four in a row.
        """
        # up-down check
        for c in range(self.cols):
            for r in range(self.rows - 3):
                winner = self.grid[r][c]
                if winner and winner == self.grid[r + 1][c] == self.grid[r + 2][c] == self.grid[r + 3][c]:
                    return winner
        # left-right check
        for r in range(self.rows):
            for c in range(self.cols - 3):
                winner = self.grid[r][c]
                if winner and winner == self.grid[r][c + 1] == self.grid[r][c + 2] == self.grid[r][c + 3]:
                    return winner
        # down-right check
        for r in range(self.rows - 3):
            for c in range(self.cols - 3):
                winner = self.grid[r][c]
                if winner and winner == self.grid[r + 1][c + 1] == self.grid[r + 2][c + 2] == self.grid[r + 3][c + 3]:
                    return winner
        # up-right check
        for r in range(3, self.rows):
            for c in range(self.cols - 3):
                winner = self.grid[r][c]
                if winner and winner == self.grid[r - 1][c + 1] == self.grid[r - 2][c + 2] == self.grid[r - 3][c + 3]:
                    return winner
        return 0
