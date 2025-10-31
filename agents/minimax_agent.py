from __future__ import annotations
from board import Board
from agents.heuristic_agent import _clone_and_drop, _opp, OffensiveAgent

INF = 10**12


def _ordered_moves(board: Board, legal_cols: list[int]) -> list[int]:
    """
    Return legal columns ordered by proximity to the center column.
    Args:
        board (Board): Current game board.
        legal_cols (list[int]): List of legal column indices.
    Returns:
        list[int]: Columns sorted by distance from the center (center-first order).
    """
    center = board.cols // 2
    return sorted(legal_cols, key = lambda c: abs(c - center))


class MinimaxAgent:
    """
    Depth-limited Minimax agent with alpha-beta pruning and heuristic evaluation.
    The agent searches the game tree up to a given depth and uses a heuristic
    function (OffensiveAgent by default) to evaluate non-terminal positions.
    """
    def __init__(self, name: str | None = None, depth: int = 6, eval_agent: OffensiveAgent | None = None):
        """
        Initialize the Minimax agent.
        Args:
            name (str | None): Display name of the agent.
            depth (int): Maximum search depth for the minimax algorithm.
            eval_agent (OffensiveAgent | None): Heuristic evaluator used for scoring
                leaf positions (default: OffensiveAgent).
        """
        self.name = name or f"Minnie Maxus" # noqa
        self.depth = depth
        self.eval_agent = eval_agent or OffensiveAgent(name = "EvalHeuristic")

    def select_move(self, board: Board, player: int) -> int:
        """
        Choose the best move for the current player using the minimax algorithm
        with alpha-beta pruning and heuristic evaluation.
        Args:
            board (Board): Current game board.
            player (int): Player ID (1 or 2).
        Returns:
            int: The column index of the best move.
        Raises:
            RuntimeError: If no legal moves are available.
        """
        legal = [c for c, ok in enumerate(board.valid_moves()) if ok]
        if not legal:
            raise RuntimeError("No legal moves available.")

        # NOT GREAT moment
        #if all(board.grid[r][c] == 0 for r in range(board.rows) for c in range(board.cols)):
            return board.cols // 2

        # Minimax
        alpha, beta = -INF, INF
        best_value, best_move = -INF, legal[0]

        for m in _ordered_moves(board, legal):
            new_board = _clone_and_drop(board, m, player)
            val = self._minimax(new_board, self.depth - 1, alpha, beta, maximizing = False,
                                    max_player = player, last_col = m)
            if val > best_value:
                best_value, best_move = val, m
            if val > alpha:
                alpha = val
        return best_move

    def _minimax(self, node: Board, depth: int, alpha: int, beta: int, maximizing: bool, max_player: int, last_col: int) -> int:
        """
        Recursive minimax search with alpha-beta pruning.
        Evaluates terminal states directly and applies heuristic scoring
        when depth limit is reached.
        Args:
            node (Board): Current board state being evaluated.
            depth (int): Remaining search depth.
            alpha (int): Alpha bound (best already guaranteed value for maximizer).
            beta (int): Beta bound (best already guaranteed value for minimizer).
            maximizing (bool): True if current layer maximizes the score.
            max_player (int): The original player for whom the search is optimizing.
            last_col (int): Column index of the last played move.
        Returns:
            int: Best score value for this subtree.
        """
        winner = node.winner()
        if winner == max_player:
            return INF // 2 + depth
        elif winner == _opp(max_player):
            return -INF // 2 - depth

        legal = [c for c, ok in enumerate(node.valid_moves()) if ok]
        if depth == 0 or not legal:
            return self.eval_agent.score_position(node, last_col = last_col, player = max_player)

        if maximizing:
            value = -INF
            for m in _ordered_moves(node, legal):
                nb = _clone_and_drop(node, m, max_player)
                child_val = self._minimax(nb, depth - 1, alpha, beta, maximizing = False, max_player = max_player, last_col = m)
                if child_val > value:
                    value = child_val
                if value > alpha:
                    alpha = value
                if alpha >= beta:
                    break
            return value
        else:
            value = INF
            opp = _opp(max_player)
            for m in _ordered_moves(node, legal):
                nb = _clone_and_drop(node, m, opp)
                child_val = self._minimax(nb, depth - 1,alpha, beta, maximizing = True, max_player = max_player, last_col = m)
                if child_val < value:
                    value = child_val
                if value < beta:
                    beta = value
                if alpha >= beta:
                    break
            return value
