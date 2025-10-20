import pygame
from typing import Optional, Dict, Tuple
from gui.scene import Scene
from board import Board
from game_controller import GameController
from agents.random_agent import RandomAgent
from gui.board_renderer import BoardRenderer
from gui.ui_element import Label, Button

class GameScene(Scene):
    """
    Pygame Game scena za Connect-N.
    - Responzivno menja raspored pri resize-u
    - Human potez: klik na kolonu
    - Random potez: automatski (sa malim "cooldown" kašnjenjem zbog preglednosti)
    - Dugmad: Back to Menu, Restart
    """

    def __init__(self, name: str = "Game"):
        super().__init__(name)

        # Konfig iz menija (popunjava se preko set_config)
        self.config: Dict = dict(
            rows=6, cols=7, connect=4,
            p1_name="Player 1", p1_type="Human",
            p2_name="Player 2", p2_type="Random"
        )

        # Logika igre
        self.board: Optional[Board] = None
        self.gc: Optional[GameController] = None

        # Agenti (samo Random; Human potez ide kroz mouse)
        self.p1_agent = None
        self.p2_agent = None

        # Renderer
        self.renderer: Optional[BoardRenderer] = None
        self._hover_col: Optional[int] = None

        # UI (hud)
        self.lbl_title = Label(0, 0, "CONNECT-N — Game")
        self.lbl_p1 = Label(0, 0, "")
        self.lbl_p2 = Label(0, 0, "")
        self.lbl_status = Label(0, 0, "Status: Player 1 to move")

        self.btn_back = Button(0, 0, 160, 44, "Back to Menu", on_click=self._on_back)
        self.btn_restart = Button(0, 0, 140, 44, "Restart", on_click=self._on_restart)

        self._elements = [
            self.lbl_title, self.lbl_p1, self.lbl_p2, self.lbl_status,
            self.btn_back, self.btn_restart
        ]

        # Estetika naslova
        self.lbl_title.font = pygame.font.SysFont(None, 36)

        # Veličina prozora i layout flag
        self._size: Tuple[int, int] = (0, 0)
        self._layout_dirty = True

        # AI tempo — malo uspori automatski potez da se vidi
        self._ai_cooldown = 0.0
        self._ai_delay = 0.35  # sekundi

        # Inicijalizuj sa podrazumevanim configom
        self._init_game()

    # -------------------- Public API --------------------

    def set_config(self, config: Dict) -> None:
        """
        Postavi konfiguraciju scene pre starta (poziva se iz MainMenu scene).
        Očekuje ključeve: rows, cols, connect, p1_name, p1_type, p2_name, p2_type
        """
        self.config.update(config or {})
        self._init_game()

    # -------------------- Internal ----------------------

    def _init_game(self) -> None:
        # Napravi board i kontroler po configu
        rows = int(self.config.get("rows", 6))
        cols = int(self.config.get("cols", 7))
        connect = int(self.config.get("connect", 4))

        self.board = Board(rows, cols, connect)
        self.gc = GameController(self.board)

        # Renderer zauzima prostor ispod HUD-a; konkretizujemo u _apply_layout
        self.renderer = None  # kreira se posle kad znamo dimenzije prozora
        self._hover_col = None

        # Agenti
        self.p1_agent = RandomAgent(self.config["p1_name"]) if self.config.get("p1_type") == "Random" else None
        self.p2_agent = RandomAgent(self.config["p2_name"]) if self.config.get("p2_type") == "Random" else None

        # Status traka
        self.lbl_p1.set_text(f"P1: {self.config['p1_name']}  [{self.config['p1_type']}]")
        self.lbl_p2.set_text(f"P2: {self.config['p2_name']}  [{self.config['p2_type']}]")
        self._update_status_text()

        # AI cooldown reset
        self._ai_cooldown = self._ai_delay

    def _apply_layout(self, w: int, h: int) -> None:
        # Margine/HUD proporcije
        margin_x = max(24, int(w * 0.03))
        top = max(16, int(h * 0.03))
        line_h = max(36, int(h * 0.055))
        gap_y = max(6, int(h * 0.012))

        # Naslov i info
        y = top
        self.lbl_title.rect.topleft = (margin_x, y)
        y += line_h

        self.lbl_p1.rect.topleft = (margin_x, y)
        y += int(line_h * 0.9)

        self.lbl_p2.rect.topleft = (margin_x, y)
        y += int(line_h * 0.9)

        self.lbl_status.rect.topleft = (margin_x, y)
        y += int(line_h * 1.0)

        # Dugmad desno gore
        btn_y = top
        self.btn_back.rect.update(w - margin_x - 160, btn_y, 160, 44)
        self.btn_restart.rect.update(w - margin_x - 160 - 12 - 140, btn_y, 140, 44)

        # Prostor za tablu: od y pa naniže do dna
        area_y = y + gap_y
        area_h = max(200, h - area_y - max(16, int(h * 0.03)))
        area_w = w

        # Kreiraj/azuriraj renderer
        if self.renderer is None:
            self.renderer = BoardRenderer(self.board.rows, self.board.cols, area_w, area_h,
                                            margin_x=margin_x, margin_top=area_y, margin_bottom=max(24, int(h * 0.03)))
        else:
            self.renderer.set_area(area_w, area_h)
            self.renderer.margin_x = margin_x
            self.renderer.margin_top = area_y
            self.renderer.margin_bottom = max(24, int(h * 0.03))
            self.renderer._compute_layout()

        self._layout_dirty = False

    def _current_is_human(self) -> bool:
        pid = self.gc.current_player()
        return (pid == 1 and self.p1_agent is None) or (pid == 2 and self.p2_agent is None)

    def _current_agent(self):
        return self.p1_agent if self.gc.current_player() == 1 else self.p2_agent

    def _play_move(self, col: int) -> None:
        # pokuša potez; ignorisi ako je nelegalan
        try:
            status = self.gc.play(col)
            self._update_status_text(status_hint=status)
        except Exception:
            # kolona puna ili out-of-range: ignoriši
            pass

    def _update_status_text(self, status_hint: Optional[str] = None) -> None:
        if status_hint:
            if status_hint.startswith("Winner"):
                winner_id = self.gc.winner_cache
                name = self.config["p1_name"] if winner_id == 1 else self.config["p2_name"]
                self.lbl_status.set_text(f"Status: Winner — {name} (P{winner_id})")
                return
            if status_hint == "Draw":
                self.lbl_status.set_text("Status: Draw")
                return

        # Inače: ko je na potezu
        pid = self.gc.current_player()
        name = self.config["p1_name"] if pid == 1 else self.config["p2_name"]
        ctrl = "Human" if self._current_is_human() else "AI"
        self.lbl_status.set_text(f"Status: {name} (P{pid}) to move — {ctrl}")

    # -------------------- Scene API --------------------

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for e in events:
            if e.type == pygame.VIDEORESIZE:
                self._size = (e.w, e.h)
                self._layout_dirty = True

            # HUD dugmad
            for el in self._elements:
                el.handle_event(e)

            # Interakcija sa tablom (samo kad je human i nije terminal)
            if not self.gc.is_terminal() and self._current_is_human() and self.renderer:
                if e.type == pygame.MOUSEMOTION:
                    self._hover_col = self.renderer.px_to_col(e.pos[0])
                elif e.type == pygame.MOUSEBUTTONUP and e.button == 1:
                    col = self.renderer.px_to_col(e.pos[0])
                    if col is not None:
                        self._play_move(col)

    def update(self, dt: float) -> None:
        for el in self._elements:
            el.update(dt)

        # AI potez (ako nije terminal i trenutni igrač je AI)
        if not self.gc.is_terminal() and not self._current_is_human():
            self._ai_cooldown -= dt
            if self._ai_cooldown <= 0.0:
                agent = self._current_agent()
                if agent:
                    try:
                        col = agent.select_move(self.gc.board, self.gc.current_player())
                        self._play_move(col)
                    finally:
                        # zadrška do sledećeg AI poteza (ako opet dođe na red)
                        self._ai_cooldown = self._ai_delay

    def draw(self, surface: pygame.Surface) -> None:
        w, h = surface.get_size()
        if (w, h) != self._size:
            self._size = (w, h)
            self._layout_dirty = True
        if self._layout_dirty:
            self._apply_layout(w, h)

        # Tabla
        if self.renderer:
            self.renderer.draw_board(surface)
            self.renderer.draw_tokens(surface, self.board.grid)
            # hover disc (samo human i kad nije terminal)
            if not self.gc.is_terminal() and self._current_is_human():
                self.renderer.draw_hover(surface, self._hover_col, self.gc.current_player())

        # HUD
        for el in self._elements:
            el.draw(surface)

    # -------------------- Actions --------------------

    def _on_back(self):
        self.request_switch("MainMenu")

    def _on_restart(self):
        self._init_game()