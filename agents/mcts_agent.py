from __future__ import annotations
import math
import random
import time
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

def _clone_board(b: Board) -> Board:
    """
    Create a deep copy of the board (since Board has no copy()).
    Args:
        b (Board): The board to copy.
    Returns:
        Board: The copy of the board.
    """
    nb = Board(b.rows, b.cols, b.connect)
    nb.grid = [row[:] for row in b.grid]
    nb.moves = b.moves
    return nb

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
    nb = _clone_board(b)
    nb.drop(col, pid)
    return nb

class _Node:
    """
    Represents a single node (state) in the Monte Carlo search tree.
    Each node stores game statistics (visits, wins) and references to its children.
    Attributes:
        parent (_Node | None): Reference to the parent node (None for the root node).
        move (int | None): Column index (0-based) of the move that led to this node
            from its parent; None for the root node.
        to_play (int): ID of the player whose turn it is at this node (1 or 2).
        children (dict[col, _Node]): Mapping of legal moves (column indices)
            to corresponding child nodes.
        N (int): Total number of visits to this node.
        W (float): Accumulated win score from the perspective of the parent’s player.
    """
    __slots__ = ("parent", "move", "to_play", "children", "N", "W")

    def __init__(self, parent: _Node | None = None, move: int | None = None, to_play: int = 1):
        """
        Initialize a new node in the search tree.
        Args:
            parent (_Node | None): Parent node in the tree (None for root).
            move (int | None): Move (column index) that led to this node from its parent.
            to_play (int): ID of the player who is to play in this node (1 or 2).
        """
        self.parent   = parent   # _Node or None
        self.move     = move     # int column that led here from parent (None at root)
        self.to_play  = to_play  # which player is to play in THIS node
        self.children = {}       # dict[col] -> _Node
        self.N        = 0        # visit count
        self.W        = 0.0      # total wins (from parent's mover perspective)

    def uct_value(self, c: float) -> float:
        """
        Compute UCT (Upper Confidence Bound of Trees) = (W/N) + c * sqrt(log(N_parent) / N)
            - W: total wins from this node
            - N: number of visits
            - c: exploration constant (e.g. sqrt(2))
        Args:
            c (float): exploration constant.
        """
        if self.N == 0:
            return float("inf")
        assert self.parent is not None and self.parent.N > 0
        q = self.W / self.N
        exploration = c * math.sqrt(math.log(self.parent.N) / self.N)
        return q + exploration

class MCTSAgent:
    """
    Monte Carlo Tree Search agent (UCT).
    - selection: UCT down the tree
    - expansion: add all legal children
    - rollout: smart-random playout (instant-win & block checks, then (optionally) center bias)
    - backprop: binary reward (win=1, loss=-1, draw=0) from alternating perspective
    Final move: child with MAX visits.
    """
    def __init__(self, name: str | None = None, simulations_per_move: int = 5000, time_limit_s: float | None = None,
                    exploration_c: float = math.sqrt(2.0), rollout_max_len: int | None = None,
                    center_bias: bool = True, seed: int | None = None):
        """
        Initialize Monte Carlo Tree Search (MCTS) agent.
        Args:
            name (str | None): Optional display name of the agent.
            simulations_per_move (int): Number of Monte Carlo simulations to run
                for each move (ignored if `time_limit_s` is set).
            time_limit_s (float | None): Optional time limit per move (in seconds).
                If provided, search runs until this time expires instead of a fixed number of simulations.
            exploration_c (float): UCT exploration constant that balances
                exploitation (known good moves) and exploration (less visited moves).
            rollout_max_len (int | None): Optional limit for maximum playout length
                during rollout phase. If reached, the rollout is treated as a draw.
            center_bias (bool): Whether to bias random rollout moves toward central columns
                (useful for Connect-N games).
            seed (int | None): Random seed for reproducible behavior.
        """
        self.name = name or "Monty Carlton"
        self.SIM = simulations_per_move
        self.TL  = time_limit_s
        self.C   = exploration_c
        self.rollout_max_len = rollout_max_len
        self.center_bias = center_bias
        self.rng = random.Random(seed)

    def select_move(self, board: Board, player: int) -> int:
        """
        Select the next move using Monte Carlo Tree Search (MCTS).

        Builds a search tree from the current board state by running multiple
        MCTS iterations (Selection → Expansion → Rollout → Backpropagation).
        Args:
            board (Board): Current game board.
            player (int): ID of the player making the move (1 or 2).
        Returns:
            int: The column index of the selected move.
        """
        root = _Node(parent = None, move = None, to_play = player)
        root_state = _clone_board(board)

        if self.TL is not None:
            deadline = time.process_time() + float(self.TL)
            while time.process_time() < deadline:
                self._iterate(root, root_state)
        else:
            sims = int(self.SIM or 0)
            for _ in range(sims):
                self._iterate(root, root_state)

        legal = [c for c, ok in enumerate(board.valid_moves()) if ok]
        if not root.children:
            if not legal:
                raise RuntimeError("No legal moves available.")
            return self.rng.choice(legal)

        # choose child with max visits
        best = max(root.children.values(), key = lambda n: n.N)
        return best.move

    def _iterate(self, root: _Node, root_state: Board) -> None:
        """
        Perform one complete MCTS iteration consisting of:
            1) Selection  – traverse the tree using UCT values,
            2) Expansion  – add new child nodes for unexplored moves,
            3) Rollout    – simulate a random playout from the new state,
            4) Backprop   – propagate the result back up the path.
        Args:
            root (_Node): Root node of the search tree.
            root_state (Board): Copy of the board at the root.
        """
        # Selection
        path, leaf_state = self._select(root, root_state)

        # Expansion
        leaf = path[-1]
        if not self._is_terminal(leaf_state):
            self._expand(leaf, leaf_state)
            if leaf.children:
                child = self.rng.choice(list(leaf.children.values()))
                leaf_state = _clone_and_drop(leaf_state, child.move, leaf.to_play)
                leaf = child
                path.append(leaf)

        # Rollout
        outcome = self._rollout(leaf_state, leaf.to_play)

        # Backprop
        self._backprop(path, outcome)

    def _select(self, root: _Node, root_state: Board) -> tuple[list[_Node], Board]:
        """
        Traverse the tree from root to a leaf using UCT selection.

        At each step, choose the child with the highest UCT value until reaching
        a node that is either unvisited (N == 0) or a terminal state.
        Args:
            root (_Node): The root node of the search tree.
            root_state (Board): The current game state (copied board).
        Returns:
            tuple[list[_Node], Board]: The path from root to selected leaf node,
                and the corresponding board state at that leaf.
        """
        node = root
        state = _clone_board(root_state)
        path = [node]

        while node.children:
            node = max(node.children.values(), key = lambda n: n.uct_value(self.C))
            state = _clone_and_drop(state, node.move, node.parent.to_play)
            path.append(node)
            if node.N == 0 or self._is_terminal(state):
                break
        return path, state

    def _expand(self, node: _Node, state: Board) -> None:
        """
        Expand a node by generating all possible legal child moves.
        Args:
            node (_Node): The node to expand.
            state (Board): The current game state at this node.
        """
        if self._is_terminal(state):
            return
        for col, ok in enumerate(state.valid_moves()):
            if not ok:
                continue
            node.children[col] = _Node(parent = node, move = col, to_play = _opp(node.to_play))

    def _rollout(self, state: Board, to_play: int) -> int:
        """
        Simulate a random (or heuristic) playout until the game ends.
        Continues to apply moves using the rollout policy until a win, draw,
        or maximum rollout length is reached.
        Args:
            state (Board): Current board state from which to simulate.
            to_play (int): ID of the player to make the next move.
        Returns:
            int: Outcome of the rollout (1 = Player 1 win, 2 = Player 2 win, 0 = Draw).
        """
        steps = 0
        while True:
            w = state.winner()
            if w:
                return w
            if state.is_full():
                return 0  # draw

            col = self._policy_move(state, to_play)
            state.drop(col, to_play)
            to_play = _opp(to_play)

            steps += 1
            if self.rollout_max_len and steps >= self.rollout_max_len:
                return 0

    def _policy_move(self, state: Board, pid: int) -> int:
        """
        Rollout policy: choose a semi-random move based on simple heuristics.

        Move priority:
            1) Immediate win if available,
            2) First move that avoids giving opponent a mate-in-1,
            3) Weighted random selection biased toward central columns,
            4) Pure random fallback if none of the above apply.
        Args:
            state (Board): Current game board state.
            pid (int): ID of the player making the move.
        Returns:
            int: The selected column index.
        """
        legal = [c for c, ok in enumerate(state.valid_moves()) if ok]
        # Immediate win
        for c in legal:
            b2 = _clone_and_drop(state, c, pid)
            if b2.winner() == pid:
                return c

        # Block opponent's immediate win
        opp = _opp(pid)
        safe_moves, danger_moves = [], []
        for c in legal:
            b2 = _clone_and_drop(state, c, pid)
            opp_legal = [cc for cc, ok2 in enumerate(b2.valid_moves()) if ok2]
            opponent_has_mate_in_1 = False
            for cc in opp_legal:
                b3 = _clone_and_drop(b2, cc, opp)
                if b3.winner() == opp:
                    opponent_has_mate_in_1 = True
                    break
            (danger_moves if opponent_has_mate_in_1 else safe_moves).append(c)

        pool = safe_moves if safe_moves else legal

        # Center bias
        if self.center_bias and len(pool) > 1:
            mid = (state.cols - 1) / 2.0
            weights = [1.0 / (1.0 + abs(c - mid)) for c in pool]
            s = sum(weights)
            r = self.rng.random() * s
            acc = 0.0
            for c, w in zip(pool, weights):
                acc += w
                if r <= acc:
                    return c
        # Random
        return self.rng.choice(pool)

    @staticmethod
    def _backprop(path: list[_Node], outcome: int) -> None:
        """
        Propagate the rollout result backward through all visited nodes.
        Args:
            path (list[_Node]): The list of nodes visited from root to leaf.
            outcome (int): Final result of the rollout (1, 2, or 0 for draw).
        """
        for node in reversed(path):
            node.N += 1
            if outcome == 0:
                reward = 0
            elif outcome == _opp(node.to_play):
                reward = 1
            else:
                reward = -1
            node.W += reward

    @staticmethod
    def _is_terminal(b: Board) -> bool:
        """
        Check whether the given board state is terminal (One of players has won or board is completely full).
        Args:
            b (Board): The board state.
        Returns:
            bool: True if the game is over (win or draw), False otherwise.
        """
        return bool(b.winner()) or b.is_full()
