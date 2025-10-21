import pygame
from gui.scene import Scene
from gui.ui_element import Label, TextInput, Dropdown, Button
from typing import Tuple

DEFAULT_ROWS = 6
DEFAULT_COLS = 7
DEFAULT_CONNECT = 4
AGENT_TYPES = ["Human", "Random"]

class MainMenu(Scene):
    """Main menu scene for configuring a Connect-N match and starting/quit actions."""
    def __init__(self):
        """
        Initialize the main menu scene and create all UI elements.

        Sets up labels, inputs, dropdowns, buttons, and internal state used for layout
        and selected configuration.
        """
        super().__init__("Main Menu")
        self._size: Tuple[int, int] = (0, 0)
        self._layout_dirty = True
        self.selected_config = None

        # UI Elements
        self.title = Label(0, 0, "CONNECT-N")

        # First Row
        self.lbl_rows = Label(0, 0, "ROWS:")
        self.in_rows = TextInput(0, 0, 100, 40, text = str(DEFAULT_ROWS), placeholder = "6")
        self.lbl_cols = Label(0, 0, "COLS:")
        self.in_cols = TextInput(0, 0, 100, 40, text = str(DEFAULT_COLS), placeholder = "7")
        self.lbl_conn = Label(0, 0, "CONNECT:")
        self.in_conn = TextInput(0, 0, 100, 40, text = str(DEFAULT_CONNECT), placeholder = "4")

        # Second Row
        self.lbl_p1 = Label(0, 0, "First player name:")
        self.in_p1 = TextInput(0, 0, 320, 44, text = "Paul Human", placeholder = "Player 1")
        self.dd_p1 = Dropdown(0, 0, 180, 44, AGENT_TYPES, selected_index = 0)

        # Third Row
        self.lbl_p2 = Label(0, 0, "Second player name:")
        self.in_p2 = TextInput(0, 0, 320, 44, text = "Marlon Random", placeholder = "Player 2")
        self.dd_p2 = Dropdown(0, 0, 180, 44, AGENT_TYPES, selected_index = 1)

        # Fourth Row
        self.btn_start = Button(0, 0, 200, 52, "START GAME", on_click = self._on_start)
        self.btn_quit = Button(0, 0, 160, 52, "QUIT", on_click = self._on_quit)

        self._elements = [
            self.title,
            self.lbl_rows, self.in_rows, self.lbl_cols, self.in_cols, self.lbl_conn, self.in_conn,
            self.lbl_p1, self.in_p1, self.dd_p1,
            self.lbl_p2, self.in_p2, self.dd_p2,
            self.btn_start, self.btn_quit
        ]

        self.title.font = pygame.font.SysFont(None, 40)

    def _apply_layout(self, width: int, height: int) -> None:
        """
        Compute responsive positions/sizes for all UI elements.
        Args:
            width (int): Current window width in pixels.
            height (int): Current window height in pixels.
        """
        margin_x = max(40, int(width * 0.08)) # Left margin
        top_y = max(40, int(height * 0.06)) # Top margin
        line_h = max(50, int(height * 0.10)) # Height of the rows for UI elements
        gap_y = max(12, int(height * 0.05))
        gap_x = max(12, int(width * 0.012))

        usable_w = width - 2 * margin_x
        center_x = margin_x + usable_w // 2

        self.title.rect.topleft = (margin_x, top_y)
        y = top_y + line_h

        # FIRST ROW: rows, cols, connect (3 Blocks)
        col_w = (usable_w - 2 * gap_x) // 3 # column width for label and it's input
        label_w_buf = 90 # width of the label

        self.lbl_rows.rect.topleft = (margin_x, y + (line_h - self.lbl_rows.rect.h) // 2)
        self.in_rows.rect.update(margin_x + label_w_buf, y + (line_h - self.in_rows.rect.h) // 2, max(80, col_w - label_w_buf),
                                    self.in_rows.rect.h)

        x2 = margin_x + col_w + gap_x
        self.lbl_cols.rect.topleft = (x2, y + (line_h - self.lbl_cols.rect.h) // 2)
        self.in_cols.rect.update(x2 + label_w_buf, y + (line_h - self.in_cols.rect.h) // 2,max(80, col_w - label_w_buf),
                                    self.in_cols.rect.h)

        x3 = margin_x + 2 * (col_w + gap_x)
        self.lbl_conn.rect.topleft = (x3, y + (line_h - self.lbl_conn.rect.h) // 2)
        self.in_conn.rect.update(x3 + label_w_buf, y + (line_h - self.in_conn.rect.h) // 2, max(80, col_w - label_w_buf),
                                    self.in_conn.rect.h)

        # SECOND ROW: label, player name input, dropdown
        y += line_h + gap_y

        left_w = int(usable_w * 0.66)
        right_w = usable_w - left_w - gap_x

        self.lbl_p1.rect.topleft = (margin_x, y)
        y += int(self.lbl_p1.rect.h * 0.8) + gap_y // 2

        self.in_p1.rect.update(margin_x, y, max(240, left_w), self.in_p1.rect.h)
        self.dd_p1.rect.update(margin_x + left_w + gap_x, y, max(140, right_w), self.dd_p1.rect.h)

        # THIRD ROW: label, player name input, dropdown
        y += 44 + gap_y + 8

        self.lbl_p2.rect.topleft = (margin_x, y)
        y += int(self.lbl_p2.rect.h * 0.8) + gap_y // 2

        self.in_p2.rect.update(margin_x, y, max(240, left_w), self.in_p2.rect.h)
        self.dd_p2.rect.update(margin_x + left_w + gap_x, y, max(140, right_w), self.dd_p2.rect.h)

        # FOURTH ROW: start button, quit button
        bottom_y = height - max(30, int(height * 0.06)) - 52

        self.btn_start.rect.update(center_x - 220, bottom_y, self.btn_start.rect.w, self.btn_start.rect.h)
        self.btn_quit.rect.update(center_x + 20, bottom_y, self.btn_quit.rect.w, self.btn_quit.rect.h)

        self._layout_dirty = False

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        """
        Handle window and UI events (resize, clicks, typing, etc.).
        Args:
            events (list[pygame.event.Event]): Events captured from the main loop.
        """
        for e in events:
            if e.type == pygame.VIDEORESIZE:
                self._size = (e.w, e.h)
                self._layout_dirty = True

            for el in self._elements:
                el.handle_event(e)

    def update(self, dt: float) -> None:
        """
        Update UI elements (e.g., caret blink) each frame.
        Args:
            dt (float): Time elapsed since last update.
        """
        for el in self._elements:
            el.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        """
        Render the scene and its UI elements to the target surface.

        Recomputes the layout if the window size changed since last frame.
        Args:
            surface (pygame.Surface): Surface to draw on.
        """
        w, h = surface.get_size()
        if (w, h) != self._size:
            self._size = (w, h)
            self._layout_dirty = True
        if self._layout_dirty:
            self._apply_layout(w, h)


        self._draw_guides(surface)

        for el in self._elements:
            el.draw(surface)

    def start_game(self):
        """Public method to handle Start Game logic."""
        self._on_start()

    def _on_start(self):
        """
        Collect form values, build `selected_config`, and request switch to Game.

        Parses rows/cols/connect and player names/types, stores them in `selected_config`,
        and calls `request_switch("Game")`.
        """
        def _to_int(txt: str, fallback: int) -> int:
            try:
                return max(1, int(txt.strip()))
            except (ValueError, AttributeError):
                return fallback

        rows = _to_int(self.in_rows.text, DEFAULT_ROWS)
        cols = _to_int(self.in_cols.text, DEFAULT_COLS)
        conn = _to_int(self.in_conn.text, DEFAULT_CONNECT)

        p1_name = self.in_p1.text.strip() or "Player 1"
        p2_name = self.in_p2.text.strip() or "Player 2"
        p1_type = AGENT_TYPES[self.dd_p1.selected_index] if self.dd_p1.selected_index is not None else "Human"
        p2_type = AGENT_TYPES[self.dd_p2.selected_index] if self.dd_p2.selected_index is not None else "Random"

        self.selected_config = dict(
            rows = rows, cols = cols, connect = conn,
            p1_name = p1_name, p1_type = p1_type,
            p2_name = p2_name, p2_type = p2_type
        )

        self.request_switch("Game")

    @staticmethod
    def _on_quit():
        """Post a QUIT event to terminate the application."""
        pygame.event.post(pygame.event.Event(pygame.QUIT))

    @staticmethod
    def  _draw_guides(surface: pygame.Surface) -> None:
        """
        Draw subtle horizontal guidelines to visually verify the layout.
        Args:
            surface (pygame.Surface): Surface to draw on.
        """
        w, h = surface.get_size()
        guide_color = (30, 30, 40)

        margin_x = max(40, int(w * 0.08))
        top_y = max(40, int(h * 0.06))
        line_h = max(50, int(h * 0.07))
        gap_y = max(12, int(h * 0.02))

        y1 = top_y + line_h - 8
        y2 = y1 + line_h + gap_y + 52
        y3 = h - max(30, int(h * 0.06)) - 62

        pygame.draw.line(surface, guide_color, (margin_x, y1), (w - margin_x, y1), 6)
        pygame.draw.line(surface, guide_color, (margin_x, y2), (w - margin_x, y2), 6)
        pygame.draw.line(surface, guide_color, (margin_x, y3), (w - margin_x, y3), 6)
