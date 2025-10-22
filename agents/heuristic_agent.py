from __future__ import annotations
from board import Board

def _opp(pid: int) -> int:
    """"""
    return 2 if pid == 1 else 1

def _clone_and_drop(b: Board, col: int, pid: int) -> Board:
    """"""
    nb = Board(b.rows, b.cols, b.connect)
    nb.grid = [row[:] for row in b.grid]
    nb.moves = b.moves
    nb.drop(col, pid)
    return nb

def _immediate_wins(b: Board, pid: int) -> list[int]:
    """"""
    wins = []
    for c, ok in enumerate(b.valid_moves()):
        if not ok:
            continue
        nb = _clone_and_drop(b, c, pid)
        if nb.winner() == pid:
            wins.append(c)
    return wins

def _count_potentials(b: Board, pid: int) -> int:
    """"""
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

def _center_bonus(b: Board, col: int) -> int:
    """"""
    mid = (b.cols - 1) / 2.0
    dist = abs(col - mid)
    return -int(dist)

class _HeuristicBase:
    """"""
    def __init__(self, name: str, w_win: int, w_block: int, w_pot: int, w_center: int):
        """"""
        self.name = name
        self.w_win = w_win
        self.w_block = w_block
        self.w_pot = w_pot
        self.w_center = w_center

    def _score_position(self, board: Board, player: int, last_col: int) -> int:
        """"""
        score = 0

        score += self.w_pot * _count_potentials(board, player)
        score += self.w_center * _center_bonus(board, last_col)

        if board.winner() == player:
            score += self.w_win

        if _immediate_wins(board, _opp(player)):
            score -= self.w_block

        return score

    def select_move(self, board: Board, player: int) -> int:
        """"""
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
                score = self._score_position(next_board, player, c)
                if score > best_score:
                    best_score, best_block = score, c
            return best_block

        best_col, best_score = None, -float('inf')
        for c in legal_cols:
            next_board = _clone_and_drop(board, c, player)
            score = self._score_position(next_board, player, c)
            if score > best_score:
                best_score, best_col = score, c
        return best_col

class OffensiveAgent(_HeuristicBase):
    """"""
    def __init__(self, name: str | None):
        """"""
        super().__init__(name or "Rowan Attackinson",
                            w_win = 1_000_000,
                            w_block = 200_000,
                            w_pot = 200,
                            w_center =20)

class DefensiveAgent(_HeuristicBase):
    """"""
    def __init__(self, name: str | None):
        """"""
        super().__init__(name or "Samuel L. Blockson",
                            w_win = 1_000_000,
                            w_block =2_000_000,
                            w_pot = 120,
                            w_center = 25)
