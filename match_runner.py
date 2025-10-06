from board import Board
from game_controller import GameController

class MatchRunner:
    """
    Runs a full Connect Four game between two agents.
    Attributes:
        agent1: Agent assigned to Player 1.
        agent2: Agent assigned to Player 2.
        game_controller (GameController): Manages the board and turn order.
        echo (bool): If True, prints moves and status messages.
        history (list[tuple[int, int]]): Sequence of (player_id, column) moves.
    """
    def __init__(self, agent1, agent2, board: Board | None = None, echo: bool = True):
        """
        Initialize a match runner with two agents and a game controller.
        Args:
            agent1: Agent instance for Player 1.
            agent2: Agent instance for Player 2.
            board (Board | None): Optional starting board (default: new empty board).
            echo (bool): Whether to print moves/status during the game.
        """
        self.agent1 = agent1
        self.agent2 = agent2
        self.game_controller = GameController(board)
        self.echo = echo
        self.history = []

    def run(self) -> int:
        """
        Play the game until it ends.
        Returns:
            int:
                1 – Player 1 wins
                2 – Player 2 wins
                0 – Draw
        Raises:
            Exception: If an agent produces an invalid move (caught and reported if echo=True).
        """
        while True:
            player_id = self.game_controller.current_player()
            agent = self.agent1 if player_id == 1 else self.agent2

            try:
                col = agent.select_move(self.game_controller.board, player_id)
                status = self.game_controller.play(col)
                self.history.append((player_id, col))

                if self.echo:
                    self.print_board()
                    name = getattr(agent, "name", f"Agent{player_id}")
                    if status.startswith("Winner"):
                        winner_id = self.game_controller.winner_cache
                        winner_agent = self.agent1 if winner_id == 1 else self.agent2
                        winner_name = getattr(winner_agent, "name", f"Agent{winner_id}")
                        status_text = f"Winner: {winner_name} (P{winner_id})"
                    elif status == "Draw":
                        status_text = "Draw"
                    else:
                        next_id = self.game_controller.current_player()
                        next_agent = self.agent1 if next_id == 1 else self.agent2
                        next_name = getattr(next_agent, "name", f"Agent{next_id}")
                        status_text = f"Next: {next_name} (P{next_id})"

                    print(f"{name} (P{player_id}) -> col {col} | {status_text}")

                if status.startswith("Winner"):
                    return self.game_controller.winner_cache
                if status == "Draw":
                    return 0

            except Exception as e:
                if self.echo:
                    print("Error:", e)

    def print_board(self):
        """Print the current board state in a readable CLI format."""
        grid = self.game_controller.board.grid
        rows, cols = self.game_controller.board.rows, self.game_controller.board.cols
        symbols = {0: "⚪", 1: "🔴", 2: "🟡"}
        digit_emoji = {
            '0': '0️⃣', '1': '1️⃣', '2': '2️⃣', '3': '3️⃣', '4': '4️⃣',
            '5': '5️⃣', '6': '6️⃣', '7': '7️⃣', '8': '8️⃣', '9': '9️⃣'
        }

        def num_to_two_rows(n: int):
            t = n // 10
            o = n % 10
            tens = digit_emoji[str(t)]
            ones = digit_emoji[str(o)]
            return tens, ones

        tens_row, ones_row = zip(*(num_to_two_rows(c) for c in range(cols))) # asteriks transpose matrix
        separator = "🔹" * cols

        # print
        print("".join(tens_row))
        print("".join(ones_row))
        print(separator)
        for r in range(rows):
            print("".join(symbols[grid[r][c]] for c in range(cols)))
        print(separator)
        print("".join(tens_row))
        print("".join(ones_row))
        print()