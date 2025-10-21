import pygame

class BoardRenderer:
    """Handles rendering of the Connect-N board, tokens, and hover indicator."""
    def __init__(self, rows: int, cols: int, area_width: int, area_height: int, *, margin_x: int = 40,
                    margin_top: int = 80, margin_bottom: int = 40, color_board: tuple = (20, 70, 155),
                    color_hole: tuple = (15, 30 ,50), color_p1: tuple = (235, 60, 60), color_p2: tuple = (240, 220, 60)):
        """
        Initialize board renderer and compute initial layout.
        Args:
            rows (int): Number of rows in the board.
            cols (int): Number of columns in the board.
            area_width (int): Total available drawing width.
            area_height (int): Total available drawing height.
            margin_x (int): Horizontal margin on both sides.
            margin_top (int): Top margin for positioning the grid.
            margin_bottom (int): Bottom margin below the grid.
            color_board (tuple[int, int, int]): RGB color of the board surface.
            color_hole (tuple[int, int, int]): RGB color of the holes.
            color_p1 (tuple[int, int, int]): RGB color of the first player tokens.
            color_p2 (tuple[int, int, int]): RGB color of the second player tokens.
        """
        self.rows = rows
        self.cols = cols
        self.area_width = area_width
        self.area_height = area_height

        self.margin_x = margin_x
        self.margin_top = margin_top
        self.margin_bottom = margin_bottom

        self.color_board = color_board
        self.color_hole = color_hole
        self.color_p1 = color_p1
        self.color_p2 = color_p2

        self._compute_layout()

    def _compute_layout(self) -> None:
        """Recalculate layout parameters for cell size, grid dimensions, and token radius."""
        inner_w = self.area_width - 2 * self.margin_x
        inner_h = self.area_height - (self.margin_top + self.margin_bottom)

        cell_width = inner_w / self.cols
        cell_height = inner_h / self.rows
        self.cell = int(min(cell_width, cell_height))

        self.grid_w = self.cell * self.cols
        self.grid_h = self.cell * self.rows
        self.grid_x = (self.area_width - self.grid_w) // 2
        self.grid_y = self.margin_top

        self.radius = int(self.cell * 0.42)

    def grid_to_px(self, row: int, col: int) -> tuple[int, int]:
        """
        Convert grid coordinates to pixel coordinates of the cell center.
        Args:
            row (int): Row index on the board.
            col (int): Column index on the board.
        Returns:
            tuple[int, int]: Pixel coordinates (x, y) of the cell center.
        """
        cx = self.grid_x + col * self.cell + self.cell // 2
        cy = self.grid_y + row * self.cell + self.cell // 2
        return cx, cy

    def px_to_col(self, x: int) -> int | None:
        """
        Convert a pixel x-coordinate to a board column index.
        Args:
            x (int): Pixel x-coordinate on the screen.
        Returns:
            int | None: Column index if within board bounds, otherwise None.
        """
        if x < self.grid_x or x > self.grid_x + self.grid_w:
            return None
        c = int((x - self.grid_x) // self.cell)
        return c if 0 <= c < self.cols else None

    def draw_board(self, surface: pygame.Surface) -> None:
        """
        Draw the board background and empty holes.
        Args:
            surface (pygame.Surface): Target surface for rendering.
        """
        pygame.draw.rect(surface, self.color_board, pygame.Rect(self.grid_x, self.grid_y, self.grid_w, self.grid_h), border_radius = 12)

        for r in range(self.rows):
            for c in range(self.cols):
                cx, cy = self.grid_to_px(r, c)
                pygame.draw.circle(surface, self.color_hole, (cx, cy), self.radius)

    def draw_tokens(self, surface: pygame.Surface, board: list[list[int]]) -> None:
        """
        Render player tokens based on the current board grid.
        Args:
            surface (pygame.Surface): Target surface for rendering.
            board (list[list[int]]): 2D grid representing board state.
        """
        for r in range(self.rows):
            for c in range(self.cols):
                v = board[r][c]
                if v == 0:
                    continue
                cx, cy = self.grid_to_px(r, c)
                color = self.color_p1 if v == 1 else self.color_p2
                pygame.draw.circle(surface, color, (cx, cy), self.radius)

    def draw_hover(self, surface: pygame.Surface, col: int | None, player: int = 1) -> None:
        """
        Draw a preview token above the board indicating possible move position.
        Args:
            surface (pygame.Surface): Target surface for rendering.
            col (int | None): Hovered column index.
            player (int): Current player ID (1 or 2).
        """
        if col is None or not (0 <= col < self.cols):
            return
        color = self.color_p1 if player == 1 else self.color_p2
        cx = self.grid_x + col * self.cell + self.cell // 2
        cy = self.grid_y - int(self.cell * 0.5)
        pygame.draw.circle(surface, color, (cx, cy), self.radius)

    def set_area(self, width: int, height: int) -> None:
        """
        Update drawing area dimensions and recompute layout.
        Args:
            width (int): New available width.
            height (int): New available height.
        """
        self.area_width = width
        self.area_height = height
        self._compute_layout()


