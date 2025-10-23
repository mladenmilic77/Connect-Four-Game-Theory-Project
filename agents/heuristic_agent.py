from __future__ import annotations
from board import Board

def _opp(pid: int) -> int:
    """
    Return the opponent's player ID.
    Args:
        pid (int): The player ID.
    Returns:
        int: The opponent's player ID.
    """
    return 2 if pid == 1 else 1

def _clone_and_drop(b: Board, col: int, pid: int) -> Board:
    """
    Simulate dropping a token in a column and return a new board copy.
    Args:
        b (Board): The board to copy.
        col (int): The column index.
        pid (int): The player ID.
    Returns:
        Board: The new board copy.
    """
    nb = Board(b.rows, b.cols, b.connect)
    nb.grid = [row[:] for row in b.grid]
    nb.moves = b.moves
    nb.drop(col, pid)
    return nb

def _immediate_wins(b: Board, pid: int) -> list[int]:
    """
    Return all columns that would result in an immediate win for `pid`.
    Args:
        b (Board): The board.
        pid (int): The player ID.
    Returns:
        list[int]: The columns that would result in an immediate win.
    """
    wins = []
    for c, ok in enumerate(b.valid_moves()):
        if not ok:
            continue
        nb = _clone_and_drop(b, c, pid)
        if nb.winner() == pid:
            wins.append(c)
    return wins

def _creates_double_threat(b: Board, col: int, pid: int) -> bool:
    """
    Check if playing in column `col` creates two or more winning threats.
    Args:
        b (Board): The board.
        col (int): The column index.
        pid (int): The player ID.
    Returns:
        bool: Whether the playing is double threat.
    """
    nb = _clone_and_drop(b, col, pid)
    wins_next = _immediate_wins(nb, pid)
    return len(set(wins_next)) >= 2

def _opponent_has_double_threat(b: Board, pid: int) -> list[int]:
    """
    Return columns where the opponent would create a double threat.
    Args:
        b (Board): The board.
        pid (int): The player ID.
    Returns:
        list[int]: The columns where the opponent would create a double threat.
    """
    opp = _opp(pid)
    cols = []
    for c, ok in enumerate(b.valid_moves()):
        if not ok:
            continue
        if _creates_double_threat(b, c, opp):
            cols.append(c)
    return cols

def _count_potentials(b: Board, pid: int) -> int:
    """
    Sum of squared token counts per window (all k-length segments without opponent tokens).
    Rough heuristic for potential connected lines.
    Args:
        b (Board): The board.
        pid (int): The player ID.
    Returns:
        int: Total score on the board `b` for player `pid`.
    """
    k = b.connect
    rows, cols, grid = b.rows, b.cols, b.grid
    me, opp = pid, _opp(pid)
    total_score = 0

    for c in range(cols):
        for r in range(rows - (k - 1)):
            window = [grid[r + i][c] for i in range(k)]
            if opp in window:
                continue
            my_tokens = window.count(me)
            total_score += my_tokens ** 2

    for r in range(rows):
        for c in range(cols - (k - 1)):
            window = [grid[r][c + i] for i in range(k)]
            if opp in window:
                continue
            my_tokens = window.count(me)
            total_score += my_tokens ** 2

    for r in range(rows - (k - 1)):
        for c in range(cols - (k - 1)):
            window = [grid[r + i][c + i] for i in range(k)]
            if opp in window:
                continue
            my_tokens = window.count(me)
            total_score += my_tokens ** 2

    for r in range(k - 1, rows):
        for c in range(cols - (k - 1)):
            window = [grid[r - i][c + i] for i in range(k)]
            if opp in window:
                continue
            my_tokens = window.count(me)
            total_score += my_tokens ** 2

    return total_score

def _detect_fork_patterns(b: Board, pid: int) -> int:
    """
    Detects latent fork patterns (_XX_ / _OO_) horizontally and diagonally.
    Evaluates positions that could become forks (double threats) in future moves.
    Args:
        b (Board): The board.
        pid (int): The player ID.
    Returns:
        int: Heuristic score adjustment based on potential fork formations.
                Positive if current player has potential forks, negative if opponent does.
    """
    k = b.connect
    rows, cols, grid = b.rows, b.cols, b.grid
    me, opp = pid, _opp(pid)
    bonus_my_fork = 80_000
    penal_opp_fork = 100_000
    score = 0

    def is_playable(_r, _c):
        return grid[_r][_c] == 0 and ((_r == b.rows - 1) or grid[_r + 1][_c] != 0)

    for r in range(rows):
        for c in range(cols - (k - 1)):
            window = [grid[r][c + i] for i in range(k)]
            if window == [0, me * (k - 2), 0]:
                if is_playable(r, c) and is_playable(r , c + (k - 1)):
                    score += bonus_my_fork
            if window == [0, opp * (k - 2), 0]:
                if is_playable(r, c) and is_playable(r , c + (k - 1)):
                    score -= penal_opp_fork

    for r in range(rows - (k - 1)):
        for c in range(cols - (k - 1)):
            window = [grid[r + i][c + i] for i in range(k)]
            if window == [0, me * (k - 2), 0]:
                if is_playable(r, c) and is_playable(r + (k - 1) , c + (k - 1)):
                    score += bonus_my_fork
            elif window == [0, opp * (k - 2), 0]:
                if is_playable(r, c) and is_playable(r + (k - 1) , c + (k - 1)):
                    score -= penal_opp_fork

    for r in range(k - 1, rows):
        for c in range(cols - (k - 1)):
            window = [grid[r - i][c + i] for i in range(k)]
            if window == [0, me * (k - 2), 0]:
                if is_playable(r, c) and is_playable(r - (k - 1) , c + (k - 1)):
                    score += bonus_my_fork
            if window == [0, opp * (k - 2), 0]:
                if is_playable(r, c) and is_playable(r - (k - 1) , c + (k - 1)):
                    score -= penal_opp_fork

    return score

def _center_bonus(b: Board, col: int) -> int:
    """
    Computes a positional bonus based on distance from the center column.
    Encourages playing closer to the center of the board, which offers
    more flexibility for building horizontal and diagonal connections.
    Args:
        b (Board): The board.
        col (int): The column index.
    Returns:
        int: Negative distance from center (higher = closer to middle).
    """
    mid = (b.cols - 1) / 2.0
    dist = abs(col - mid)
    return -int(dist)

class _HeuristicBase:
    """
    Base class for heuristic Connect-N agents.

    Provides a rule-based evaluation framework that balances offensive
    and defensive heuristics, including win/block detection, potential
    line scoring, center bias, and fork (double-threat) analysis.
    """
    def __init__(self, name: str, w_win: int, w_block: int, w_pot: int, w_center: int,
                    w_my_fork: int = 400_000, w_opp_fork: int = 450_000):
        """
        Initialize a heuristic-based Connect-N agent.
        Args:
            name (str): The name of the agent.
            w_win (int): Weight for immediate win situations.
            w_block (int): Weight for blocking opponent's imminent win.
            w_pot (int): Weight for potential connections (positional strength).
            w_center (int): Weight for central column occupation.
            w_my_fork (int): Bonus for creating double-threat (fork) patterns.
            w_opp_fork (int): Penalty for allowing opponent fork formations.
        """
        self.name = name
        self.w_win = w_win
        self.w_block = w_block
        self.w_pot = w_pot
        self.w_center = w_center
        self.w_my_fork = w_my_fork
        self.w_opp_fork = w_opp_fork

    def _score_position(self, board: Board, last_col, player) -> int:
        """
        Evaluate the board position numerically for the given player.

        This function combines multiple heuristic factors:
            - potential connected lines (squared token counts),
            - center column bias,
            - latent fork patterns,
            - direct wins or losses,
            - immediate and next-move double threats.
        Args:
            board (Board): The board.
            last_col (int): The last column index.
            player (int): The player ID.
        Returns:
            int: Cumulative heuristic score for the given player.
        """
        score = 0

        score += self.w_pot * _count_potentials(board, player)
        score += self.w_center * _center_bonus(board, last_col)
        score += _detect_fork_patterns(board, player)

        if board.winner() == player:
            score += self.w_win

        if _immediate_wins(board, _opp(player)):
            score -= self.w_block

        my_wins_next = _immediate_wins(board, player)
        if len(set(my_wins_next)) >= 2:
            score += self.w_my_fork

        opp_wins_next = _immediate_wins(board, _opp(player))
        if len(set(opp_wins_next)) >= 2:
            score -= self.w_opp_fork

        return score

    def select_move(self, board: Board, player: int) -> int:
        """
        Select the best move for the current player based on heuristic evaluation.

        The move-selection priority is:
            1. Play an immediate winning move (if available).
            2. Block opponent’s immediate win.
            3. Create a fork (double-threat) if possible.
            4. Block opponent’s potential fork.
            5. Otherwise, pick the move with the best heuristic score.
        Args:
            board (Board): The board.
            player (int): The player ID.
        Returns:
            int: Column index of the selected move.
        Raises:
            RuntimeError: If there are no legal moves available.
        """
        legal_cols = [c for c, ok in enumerate(board.valid_moves()) if ok]
        if not legal_cols:
            raise RuntimeError("No legal moves available.")

        my_wins = _immediate_wins(board, player)
        if my_wins:
            return my_wins[0]

        opp_wins = _immediate_wins(board, _opp(player))
        if opp_wins:
            best_block, best_score = None, -float('inf')
            for c in opp_wins:
                next_board = _clone_and_drop(board, c, player)
                score = self._score_position(next_board, c, player)
                if score > best_score:
                    best_score, best_block = score, c
            return best_block

        my_forks = [c for c in legal_cols if _creates_double_threat(board, c, player)]
        if my_forks:
            mid = (board.cols - 1) / 2.0
            my_forks.sort(key = lambda x: abs(x - mid))
            return my_forks[0]

        opp_forks_cols = _opponent_has_double_threat(board, player)
        if opp_forks_cols:
            candidates = [c for c in opp_forks_cols if c in legal_cols]
            if candidates:
                best_col, best_score = None, -float('inf')
                for c in candidates:
                    next_board = _clone_and_drop(board, c, player)
                    score = self._score_position(next_board, c, player)
                    if score > best_score:
                        best_score, best_col = score, c
                return best_col

        best_col, best_score = None, -float('inf')
        for c in legal_cols:
            next_board = _clone_and_drop(board, c, player)
            score = self._score_position(next_board, c, player)
            if score > best_score:
                best_score, best_col = score, c
        return best_col

class OffensiveAgent(_HeuristicBase):
    """Aggressive heuristic agent prioritizing offensive play."""
    def __init__(self, name: str | None):
        super().__init__(name or "Rowan Attackinson",
                            w_win = 1_000_000,
                            w_block = 200_000,
                            w_pot = 200,
                            w_center =20,
                            w_my_fork = 450_000,
                            w_opp_fork = 500_000)

class DefensiveAgent(_HeuristicBase):
    """Defensive heuristic agent prioritizing prevention and blocking."""
    def __init__(self, name: str | None):
        super().__init__(name or "Samuel L. Blockson",
                            w_win = 1_000_000,
                            w_block = 200_000,
                            w_pot = 200,
                            w_center =20,
                            w_my_fork = 350_000,
                            w_opp_fork = 600_000)
