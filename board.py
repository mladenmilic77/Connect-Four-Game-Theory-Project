"""
This class implements the core logic of the Connect Four game
(default board size 6x7, but customizable via constructor).
Methods:
    __init__(rows=6, cols=7):
        Constructor. Initializes an empty board and resets move counter.

    reset() -> None:
        Clears the board and resets the move counter.

    valid_moves() -> list[bool]:
        Returns a boolean list indicating which columns are available for a move.

    drop(col: int, player: int) -> bool:
        Drops a token for the given player (1 or 2) into the specified column.
        Raises:
            ValueError – if player is not 1 or 2, or if the column is full.
            IndexError – if the column index is out of range.
        Returns:
            True if the move was successfully made.

    is_full() -> bool:
        Returns True if the board is completely filled (no more valid moves).

    winner() -> int:
        Checks the board for a winning sequence of 4 in a row.
        Returns:
            0 – no winner,
            1 – player 1 wins,
            2 – player 2 wins.
"""
# TODO Make additional class for constants
ROWS = 6
COLS = 7
class Board:
    def __init__(self, rows = ROWS, cols = COLS):
        self.rows = rows
        self.cols = cols
        self.grid = [[0 for _ in range(cols)] for _ in range(rows)]
        self.moves = 0

    def reset(self):
        self.grid = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.moves = 0

    def valid_moves(self) -> list[bool]:
        return [self.grid[0][c] == 0 for c in range(self.cols)]

    def drop(self, col: int, player: int) -> bool:
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
        return self.moves >= self.rows * self.cols

    def winner(self) -> int:
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
        # down-right chek
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
