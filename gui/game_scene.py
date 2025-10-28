import pygame
from typing import Optional, Dict, Tuple
from gui.scene import Scene
from board import Board
from game_controller import GameController
from agents.random_agent import RandomAgent
from agents.minimax_agent import MinimaxAgent
from agents.heuristic_agent import OffensiveAgent
from agents.mcts_agent import MCTSAgent
from gui.board_renderer import BoardRenderer
from gui.ui_element import Label, Button

class GameScene(Scene):
    """Handles the Connect-N gameplay scene, including rendering, input, and agent control."""

    AGENTS = {
        "Human": lambda name: None,
        "Random": lambda name: RandomAgent(name),
        "Heuristic": lambda name: OffensiveAgent(name),
        "Minimax": lambda name: MinimaxAgent(name),
        "Monte Carlo": lambda name: MCTSAgent(name),
    }
    def __init__(self, name: str = "Game"):
        """
        Initialize the game scene and create all UI elements.
        Args:
            name (str, optional): Name of the scene.
        """
        super().__init__(name)

        self.config: Dict = dict(
            rows = 6, cols = 7, connect = 4,
            p1_name = "Player 1", p1_type = "Human",
            p2_name = "Player 2", p2_type = "Random"
        )

        self.board: Optional[Board] = None
        self.gc: Optional[GameController] = None

        self.p1_agent = None
        self.p2_agent = None

        self.renderer: Optional[BoardRenderer] = None
        self._hover_col: Optional[int] = None

        # UI elements
        self.lbl_title = Label(0, 0, "CONNECT-N Game")
        self.lbl_p1 = Label(0, 0, "")
        self.lbl_p2 = Label(0, 0, "")
        self.lbl_status = Label(0, 0, "Status: Player 1 to move")

        self.btn_back = Button(0, 0, 160, 44, "Back to Menu", on_click = self._on_back)
        self.btn_restart = Button(0, 0, 140, 44, "Restart", on_click = self._on_restart)

        self._elements = [
            self.lbl_title, self.lbl_p1, self.lbl_p2, self.lbl_status,
            self.btn_back, self.btn_restart
        ]

        self.lbl_title.font = pygame.font.SysFont(None, 36)

        self._size: Tuple[int, int] = (0, 0)
        self._layout_dirty = True

        self._ai_cooldown = 0.0
        self._ai_delay = 0.55  # seconds

        self._init_game()

    def set_config(self, config: Dict) -> None:
        """
        Update scene configuration and reinitialize the game.
        Args:
            config (dict): A dictionary containing the game configuration.
        """
        self.config.update(config or {})
        self._init_game()

    def _make_agent(self, kind: str, name: str):
        """
        Build an agent instance by kind string. 'Human' returns None (no AI).
        Args:
            kind (str): Agent type key (e.g., 'Human', 'Random', 'Minimax', 'MCTS', ...).
            name (str): Display name for the agent.
        Returns:
            object | None: Agent instance or None for Human.
        Raises:
            ValueError: If kind is unknown.
        """
        if kind is None:
            return None
        factory = self.AGENTS.get(kind)
        if factory is None:
            raise ValueError(f"Unknown agent type: {kind!r}")
        return factory(name)

    def _init_game(self) -> None:
        """Initialize or reset the game state, board, controller, and agents."""
        rows = int(self.config.get("rows", 6))
        cols = int(self.config.get("cols", 7))
        connect = int(self.config.get("connect", 4))

        self.board = Board(rows, cols, connect)
        self.gc = GameController(self.board)

        self.renderer = None
        self._hover_col = None

        # Agents
        self.p1_agent = self._make_agent(self.config.get("p1_type", "Human"), self.config.get("p1_name", "Player 1"))
        self.p2_agent = self._make_agent(self.config.get("p2_type", "Random"), self.config.get("p2_name", "Player 2"))

        # Status
        self.lbl_p1.set_text(f"P1: {self.config['p1_name']}  [{self.config['p1_type']}]")
        self.lbl_p2.set_text(f"P2: {self.config['p2_name']}  [{self.config['p2_type']}]")
        self._update_status_text()

        self._ai_cooldown = self._ai_delay
        self._layout_dirty = True

    def _apply_layout(self, w: int, h: int) -> None:
        """
        Recalculate UI element positions and board area based on current window size.
        Args:
            w (int): Current window width.
            h (int): Current window height
        """
        margin_x_ui = max(24, int(w * 0.03))
        top = max(16, int(h * 0.03))
        line_h = max(36, int(h * 0.055))
        gap_y = max(6, int(h * 0.012))

        y = top
        self.lbl_title.rect.topleft = (margin_x_ui, y); y += line_h
        self.lbl_p1.rect.topleft = (margin_x_ui, y);    y += int(line_h * 0.9)
        self.lbl_p2.rect.topleft = (margin_x_ui, y);    y += int(line_h * 0.9)
        self.lbl_status.rect.topleft = (margin_x_ui, y); y += int(line_h * 1.0)

        btn_y = top
        self.btn_back.rect.update(w - margin_x_ui - 160, btn_y, self.btn_back.rect.w, self.btn_back.rect.h)
        self.btn_restart.rect.update(w - margin_x_ui - 160 - 12 - 140, btn_y, self.btn_restart.rect.w, self.btn_restart.rect.h)

        status_bottom = self.lbl_status.rect.bottom
        hover_zone_px = max(140, int(0.18 * h))

        board_y = status_bottom + gap_y + hover_zone_px
        area_w, area_h = w, h

        if self.renderer is None:
            self.renderer = BoardRenderer(self.board.rows, self.board.cols, area_w, area_h,
                                            margin_x=0, margin_top=board_y, margin_bottom=0)
        else:
            r = self.renderer
            r.margin_x = 0
            r.margin_top = board_y
            r.margin_bottom = 0
            r.set_area(area_w, area_h)

        r = self.renderer
        safe_gap = 8
        r.hover_min_cy = status_bottom + safe_gap + r.radius
        r.hover_max_cy = int(r.grid_y - r.radius - 2)
        self._layout_dirty = False

    def _current_is_human(self) -> bool:
        """
        Check if the current player is human.
        Returns:
            bool: True if the current player is human, False otherwise.
        """
        pid = self.gc.current_player()
        return (pid == 1 and self.p1_agent is None) or (pid == 2 and self.p2_agent is None)

    def _current_agent(self) -> Optional[object]:
        """
        Return the active agent instance for the current player.
        Returns:
            object | None: Active agent if current player is AI, otherwise None.
        """
        return self.p1_agent if self.gc.current_player() == 1 else self.p2_agent

    def _play_move(self, col: int) -> None:
        """
        Execute a move in the given column and update the game status.
        Args:
            col (int): Column index where the token should be placed.
        Raises:
            Exception: If the move is invalid or column is full.
        """
        try:
            status = self.gc.play(col)
            self._update_status_text(status_hint = status)
        except (ValueError, IndexError):
            pass

    def _update_status_text(self, status_hint: Optional[str] = None) -> None:
        """
        Update the status label based on the current game state or a provided hint.
        Args:
            status_hint (Optional[str]): Optional status message such as 'Winner' or 'Draw'.
        """
        if status_hint:
            if status_hint.startswith("Winner"):
                winner_id = self.gc.winner_cache
                name = self.config["p1_name"] if winner_id == 1 else self.config["p2_name"]
                self.lbl_status.set_text(f"Status: Winner — {name} (P{winner_id})")
                return
            if status_hint == "Draw":
                self.lbl_status.set_text("Status: Draw")
                return

        pid = self.gc.current_player()
        name = self.config["p1_name"] if pid == 1 else self.config["p2_name"]
        self.lbl_status.set_text(f"Status: {name} (P{pid}) to move")

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        """
        Handle user and system events including window resize and mouse input.
        Args:
            events (list[pygame.event.Event]): List of pygame events captured in the main loop.
        """
        for e in events:
            if e.type == pygame.VIDEORESIZE:
                self._size = (e.w, e.h)
                self._layout_dirty = True

            for el in self._elements:
                el.handle_event(e)

            if not self.gc.is_terminal() and self._current_is_human() and self.renderer:
                if e.type == pygame.MOUSEMOTION:
                    self._hover_col = self.renderer.px_to_col(e.pos[0])
                elif e.type == pygame.MOUSEBUTTONUP and e.button == 1:
                    col = self.renderer.px_to_col(e.pos[0])
                    if col is not None:
                        self._play_move(col)

    def update(self, dt: float) -> None:
        """
        Update scene logic including AI timing and UI element updates.
        Args:
            dt (float): Time elapsed since the last update.
        """
        for el in self._elements:
            el.update(dt)

        if not self.gc.is_terminal() and not self._current_is_human():
            self._ai_cooldown -= dt
            if self._ai_cooldown <= 0.0:
                agent = self._current_agent()
                if agent:
                    try:
                        col = agent.select_move(self.gc.board, self.gc.current_player())
                        self._play_move(col)
                    finally:
                        self._ai_cooldown = self._ai_delay

    def draw(self, surface: pygame.Surface) -> None:
        """
        Render the board, tokens, hover preview, and all UI elements.
        Args:
            surface (pygame.Surface): Target surface where the scene is drawn.
        """
        w, h = surface.get_size()
        if (w, h) != self._size:
            self._size = (w, h)
            self._layout_dirty = True
        if self._layout_dirty:
            self._apply_layout(w, h)

        if self.renderer:
            self.renderer.draw_board(surface)
            self.renderer.draw_tokens(surface, self.board.grid)
            if not self.gc.is_terminal() and self._current_is_human():
                self.renderer.draw_hover(surface, self._hover_col, self.gc.current_player())

        for el in self._elements:
            el.draw(surface)

    def _on_back(self):
        """Request scene switch back to the main menu."""
        self.request_switch("MainMenu")

    def _on_restart(self):
        """Restart the current game and reset all states."""
        self._init_game()