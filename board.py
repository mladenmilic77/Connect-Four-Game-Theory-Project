# TODO Make additional class for constants and make limits for DEFAULT_CONNECT variable

DEFAULT_CONNECT = 4
MIN_RC = 3
MAX_RC = 30
ROWS = 6
COLS = 7

class Board:
    """
    Connect-N board and rules.
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
    def __init__(self, rows: int = ROWS, cols: int = COLS, connect: int = DEFAULT_CONNECT):
        """
        Initialize an empty board of size rows x cols.
        Args:
        rows (int): Number of rows (default 6).
        cols (int): Number of columns (default 7).
        connect (int): N-in-a-row needed to win (default 4).
        """
        if not (MIN_RC <= rows <= MAX_RC):
            raise ValueError(f"Rows must be in [{MIN_RC}, {MAX_RC}] (got: {rows})")
        if not (MIN_RC <= cols <= MAX_RC):
            raise ValueError(f"Cols must be in [{MIN_RC}, {MAX_RC}] (got: {cols})")
        if connect < 3:
            raise ValueError(f"Connect must be >= 3 (got: {connect}).")
        if max(rows, cols) < connect:
            raise ValueError(f"Board too small for Connect-{connect}.")

        self.rows = rows
        self.cols = cols
        self.connect = connect
        self.grid = [[0 for _ in range(cols)] for _ in range(rows)]
        self.moves = 0

    def reset(self) -> None:
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
        Check the board for any k-in-a-row (vertical, horizontal, or diagonal).
        Returns:
            0 if no winner,
            1 if player 1 has k-in-a-row,
            2 if player 2 has k-in-a-row.
        """
        rows, cols, grid, k = self.rows, self.cols, self.grid, self.connect
        # up-down check
        for c in range(cols):
            for r in range(rows - (k - 1)):
                p = grid[r][c]
                if p and all(grid[r + i][c] == p for i in range(k)):
                    return p
        # left-right check
        for r in range(rows):
            for c in range(cols - (k - 1)):
                p = grid[r][c]
                if p and all(grid[r][c + i] == p for i in range(k)):
                    return p
        # down-right check
        for r in range(rows - (k - 1)):
            for c in range(cols - (k - 1)):
                p = grid[r][c]
                if p and all(grid[r + i][c + i] == p for i in range(k)):
                    return p
        # up-right check
        for r in range((k - 1), rows):
            for c in range(cols - (k - 1)):
                p = grid[r][c]
                if p and all(grid[r - i][c + i] == p for i in range(k)):
                    return p
        return 0
