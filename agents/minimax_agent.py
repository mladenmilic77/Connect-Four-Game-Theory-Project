from __future__ import annotations
from typing import Optional, Tuple
from board import Board
from agents.heuristic_agent import _clone_and_drop, _opp, OffensiveAgent

INF = 10**12


def _ordered_moves(board: Board, legal_cols):
    """"""
    center = board.cols // 2
    return sorted(legal_cols, key=lambda c: abs(c - center))


class MinimaxAgent:
    """"""
    def __init__(self, name: Optional[str] = None, depth: int = 6, eval_agent: Optional[OffensiveAgent] = None):
        self.name = name or f"Minnie Maxus" # noqa
        self.depth = int(depth)
        self.eval_agent = eval_agent or OffensiveAgent(name = "EvalHeuristic")

    def select_move(self, board: Board, player: int) -> int:
        player = int(player)
        legal = [c for c, ok in enumerate(board.valid_moves()) if ok]
        if not legal:
            raise RuntimeError("No legal moves available.")

        # NOT GREAT moment
        if all(board.grid[r][c] == 0 for r in range(board.rows) for c in range(board.cols)):
            return board.cols // 2

        # Minimax
        alpha, beta = -INF, INF
        best_value, best_move = -INF, legal[0]

        for m in _ordered_moves(board, legal):
            new_board = _clone_and_drop(board, m, player)
            val, _ = self._minimax(new_board, self.depth - 1, alpha, beta, maximizing = False,
                                    max_player = player, last_col = m)
            if val > best_value:
                best_value, best_move = val, m
            if val > alpha:
                alpha = val
        return best_move

    def _minimax(self, node: Board, depth: int, alpha: int, beta: int, maximizing: bool, max_player: int, last_col: int) -> Tuple[int, Optional[int]]:
        winner = node.winner()
        if winner == max_player:
            return INF // 2 + depth, None
        elif winner == _opp(max_player):
            return -INF // 2 - depth, None

        legal = [c for c, ok in enumerate(node.valid_moves()) if ok]
        if depth == 0 or not legal:
            score = self.eval_agent.score_position(node, last_col = last_col, player = max_player)
            return score, None

        if maximizing:
            value = -INF
            best_move = None
            for m in _ordered_moves(node, legal):
                nb = _clone_and_drop(node, m, max_player)
                child_val, _ = self._minimax(nb, depth - 1, alpha, beta, maximizing = False, max_player = max_player, last_col = m)
                if child_val > value:
                    value, best_move = child_val, m
                if value > alpha:
                    alpha = value
                if alpha >= beta:
                    break
            return value, best_move
        else:
            value = INF
            best_move = None
            opp = _opp(max_player)
            for m in _ordered_moves(node, legal):
                nb = _clone_and_drop(node, m, opp)
                child_val, _ = self._minimax(nb, depth - 1,alpha, beta, maximizing = True, max_player = max_player, last_col = m)
                if child_val < value:
                    value, best_move = child_val, m
                if value < beta:
                    beta = value
                if alpha >= beta:
                    break
            return value, best_move
