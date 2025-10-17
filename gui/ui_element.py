import pygame
from abc import ABC, abstractmethod
from collections.abc import Callable

class UIElement(ABC):
    """
    Base class for all user interface elements (buttons, labels, inputs...).
    Provides:
        - Position and size (self.rect)
        - Visibility and enabled state
        - Common interface: handle_event(), update(), draw()
    """
    def __init__(self, x: int, y: int, width: int, height: int, *, visible: bool = True, enabled: bool = True):
        """
        Initialize a UI element with its position and geometry.
        Args:
            x (int): X coordinate of the element (top-left corner).
            y (int): Y coordinate of the element (top-left corner).
            width (int): Width of the element in pixels.
            height (int): Height of the element in pixels.
            visible (bool): Whether the element is visible or not (default: True).
            enabled (bool): Whether the element is enabled or not (default: True).
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.visible = visible
        self.enabled = enabled

    def handle_event(self, event: pygame.event.Event) -> None:
        """
        Called once for each pygame event.
        Override in subclasses that need to react to clicks or keys.
        """
        pass

    def update(self, dt: float) -> None:
        """
        Called every frame with delta time (in seconds).
        Override in subclasses for animations, cursor blinking, etc.
        """
        pass

    @abstractmethod
    def draw(self, surface: pygame.Surface) -> None:
        """
        Render the element on the given surface.
        Must be implemented by every subclass.
        """
        raise NotImplementedError()

    def contains_point(self, pos: tuple[int, int]) -> bool:
        """
        Check if the given (x, y) position is inside the element.
        Useful for detecting mouse hover or clicks.
        """
        return self.rect.collidepoint(pos)

    def show(self) -> None:
        """Make the element visible."""
        self.visible = True

    def hide(self) -> None:
        """Make the element not visible."""
        self.visible = False

    def enable(self) -> None:
        """Make the element enabled."""
        self.enabled = True

    def disable(self) -> None:
        """Make the element disabled."""
        self.enabled = False

class Label(UIElement):
    """
    Simple non-interactive text element.
    Used for displaying static text (titles, info, hints, etc.).
    """
    def __init__(self, x: int, y: int, text: str, font: pygame.font.Font | None = None,
                    color: tuple[int, int, int] = (230, 230, 230)):
        """
        Initialize a label at given position.
        Args:
            x (int): X coordinate of the label.
            y (int): Y coordinate of the label.
            text (str): Text of the label.
            font (pygame.font.Font | None): Optional pygame Font object. Default system font if None.
            color (tuple[int, int, int]): RGB Color of the label.
        """
        self.font = font or pygame.font.SysFont(None, 28)
        self.text = text
        self.color = color
        
        text_surface =  self.font.render(self.text, True, self.color)
        width, height = text_surface.get_size()
        
        super().__init__(x, y, width, height)

    def set_text(self, text: str) -> None:
        """
        Change the label text and recalculate its size.
        Args:
            text (str): New text of the label.
        """
        self.text = text
        text_surface = self.font.render(self.text, True, self.color)
        width, height = text_surface.get_size()
        self.rect.size = width, height

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the label onto the given surface.
        Args:
            surface (pygame.Surface): Surface to draw the label on.
        """
        if not self.visible:
            return
        text_surface = self.font.render(self.text, True, self.color)
        surface.blit(text_surface, self.rect.topleft)

class Button(UIElement):
    """Clickable rectangular button with a text label and optional callback."""
    def __init__(self, x: int, y: int, width: int, height: int, text: str, on_click: Callable | None = None, *,
                    font: pygame.font.Font | None = None, color_bg: tuple[int, int, int] = (40, 40, 55),
                    color_bg_hover: tuple[int, int, int] = (55, 55, 80), color_border: tuple[int, int, int] = (80, 80, 80),
                    color_text: tuple[int, int, int] = (235, 235, 235), border_px: int = 2):
        """
        Initialize a button.
        Args:
            x (int): X coordinate of top-left corner of the button.
            y (int): Y coordinate of top-left corner of the button.
            width (int): Width of the button in pixels.
            height (int): Height of the button in pixels.
            text (str): Caption text of the button.
            on_click (callable | None): Optional callback function that will be called when the button is clicked.
            font (pygame.font.Font | None): Optional pygame Font object.
            color_bg (tuple[int, int, int]): RGB Color of the button.
            color_bg_hover (tuple[int, int, int]): RGB Color of the button when hovering.
            color_border (tuple[int, int, int]): RGB Color of the button border.
            color_text (tuple[int, int, int]): RGB Color of the button text.
            border_px (int): Button border thickness in pixels.
        """
        super().__init__(x, y, width, height)

        # Appearance
        self.text = text
        self.font = font or pygame.font.SysFont(None, 28)
        self.color_bg = color_bg
        self.color_bg_hover = color_bg_hover
        self.color_border = color_border
        self.color_text = color_text
        self.border_px = border_px

        # Behavior
        self.on_click = on_click
        self._hovered = False
        self._pressed = False

    def handle_event(self, event: pygame.event.Event) -> None:
        """
        React to mouse hover and clicks.
        Args:
            event (pygame.event.Event): Event to handle.
        """
        if not (self.visible and self.enabled):
            return
        if event.type == pygame.MOUSEMOTION:
            self._hovered = self.contains_point(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.contains_point(event.pos):
                self._pressed = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self._pressed and self.contains_point(event.pos):
                if callable(self.on_click):
                    self.on_click()
            self._pressed = False

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the button background, border, and text.
        Args:
            surface (pygame.Surface): Surface to draw the button on.
        """
        if not self.visible:
            return

        bg_color = self.color_bg_hover if self._hovered else self.color_bg
        pygame.draw.rect(surface, bg_color, self.rect, border_radius = 6)
        pygame.draw.rect(surface, self.color_border, self.rect, width = self.border_px, border_radius = 6)

        text_surface = self.font.render(self.text, True, self.color_text)
        text_rect = text_surface.get_rect(center = self.rect.center)
        surface.blit(text_surface, text_rect)

class TextInput(UIElement):
    """
    Single-line text input field.
    Supports:
        - Click-to-focus
        - Text typing and deletion
        - Caret movement (Left, Right, Home, End)
        - Caret blinking while focused
        - Placeholder text when empty and unfocused
        - Callbacks for text submission (Enter) and text change
    """
    def __init__(self, x: int, y: int, width: int, height: int, text: str = "", placeholder: str = "", *,
                    font: pygame.font.Font | None = None, color_bg: tuple[int, int, int] = (35, 35, 45),
                    color_bg_active: tuple[int, int, int] = (45, 45, 60), color_border: tuple[int, int, int] = (90, 90, 120),
                    color_text: tuple[int, int, int] = (235, 235, 235), color_placeholder: tuple[int, int, int] = (150, 150, 150),
                    caret_color: tuple[int, int, int] = (255, 255, 255), border_px: int = 2, padding: int = 8,
                    max_length: int | None = None, on_submit: Callable | None = None, on_change: Callable = None):
        """
        Initialize a text input field.
        Args:
            x (int): X coordinate of top-left corner.
            y (int): Y coordinate of top-left corner.
            width (int): Width of the input box in pixels.
            height (int): Height of the input box in pixels.
            text (str): Initial text value.
            placeholder (str): Text shown when the input is empty and unfocused.
            font (pygame.font.Font | None): Optional pygame Font object.
            color_bg (tuple[int, int, int]): RGB Color of the background when input box is not focused.
            color_bg_active (tuple[int, int, int]): RGB Color of the background when input box is focused.
            color_border (tuple[int, int, int]): RGB Color of the border.
            color_text (tuple[int, int, int]): RGB Color of the text.
            color_placeholder (tuple[int, int, int]): RGB Color of the placeholder text.
            caret_color (tuple[int, int, int]): RGB Color of the blinking caret.
            border_px (int): Input box border thickness in pixels.
            padding (int): Inner horizontal text padding.
            max_length (int): Optional maximum allowed text length.
            on_submit (callable | None): Optional callback function that will be called when the text is submitted.
            on_change (callable | None): Optional callback function that will be called when the text changes.
        """
        super().__init__(x, y, width, height)
        self.font = font or pygame.font.SysFont(None, 26)

        # Appearance
        self.color_bg = color_bg
        self.color_bg_active = color_bg_active
        self.color_border = color_border
        self.color_text = color_text
        self.color_placeholder = color_placeholder
        self.caret_color = caret_color
        self.border_px = border_px
        self.padding = padding

        # Behavior
        self.text = text
        self.placeholder = placeholder
        self.max_length = max_length
        self.on_submit = on_submit
        self.on_change = on_change

        self.active = False
        self.caret_pos = len(self.text)
        self._blink_timer = 0.0
        self._caret_visible = True

        # Selection
        self.sel_start: int | None = None
        self.sel_end: int | None = None

    def set_text(self, text: str) -> None:
        """
        Set the text programmatically and reset the caret to the end.
        Args:
            text: New text string to set.
        """
        self.text = text
        self.caret_pos = len(self.text)
        self._emit_change()

    def set_active(self, active: bool) -> None:
        """
        Activate (focus) or deactivate (blur) the text input.
        Args:
            active (bool): True to focus or False to blur.
        """
        self.active = active
        if not active:
            self.sel_start = self.sel_end = None

    def _emit_change(self) -> None:
        """Trigger the on_change callback if one is defined."""
        if callable(self.on_change):
            self.on_change(self.text)

    def _clamp_caret(self) -> None:
        """Ensure the caret position stays within valid bounds [0, len(text)]."""
        self.caret_pos = max(0, min(self.caret_pos, len(self.text)))

    def _insert_text(self, text: str) -> None:
        """
        Insert a given string at the current caret position.
        Args:
            text (str): New text string to insert.
        """
        if not text:
            return
        if self.max_length is not None and len(self.text) >= self.max_length:
            return

        self.text = self.text[:self.caret_pos] + text + self.text[self.caret_pos:]
        self.caret_pos += len(text)
        self._emit_change()

    def _delete_left(self) -> None:
        """Delete the character immediately before the caret position (Backspace)."""
        if self.caret_pos > 0:
            self.text = self.text[:self.caret_pos - 1] + self.text[self.caret_pos:]
            self.caret_pos -= 1
            self._emit_change()

    def _delete_right(self) -> None:
        """Delete the character immediately after the caret position (Delete)."""
        if self.caret_pos < len(self.text):
            self.text = self.text[:self.caret_pos] + self.text[self.caret_pos + 1:]
            self._emit_change()

    #==============================================================#

    def handle_event(self, event: pygame.event.Event) -> None:
        """
        Handle keyboard and mouse input for the text box.
        Handles:
            - Mouse click: toggles focus when clicking inside the box.
            - Keyboard typing: inserts printable characters.
            - Backspace/Delete: removes characters.
            - Arrow keys, Home, End: move caret.
            - Enter: triggers on_submit callback.
        Args:
            event (pygame.event.Event): Input event.
        """
        if not (self.visible and self.enabled):
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.set_active(self.contains_point(event.pos))

        if not self.active:
            return

        if event.type == pygame.KEYDOWN:
            # Submit
            if event.key == pygame.K_RETURN:
                if callable(self.on_submit):
                    self.on_submit(self.text)
                return

            # Navigation
            if event.key == pygame.K_LEFT:
                self.caret_pos -= 1
                self._clamp_caret()
                return
            if event.key == pygame.K_RIGHT:
                self.caret_pos += 1
                self._clamp_caret()
                return
            if event.key == pygame.K_HOME:
                self.caret_pos = 0
                return
            if event.key == pygame.K_END:
                self.caret_pos = len(self.text)
                return

            # Editing
            if event.key == pygame.K_BACKSPACE:
                self._delete_left()
                return
            if event.key == pygame.K_DELETE:
                self._delete_right()
                return

            # Print character
            ch = event.unicode
            if ch and ch.isprintable():
                self._insert_text(ch)

    def update(self, dt: float) -> None:
        """
        Update caret blink timing. Called once per frame.
        Args:
            dt (float): Delta time since last frame in seconds.
        """
        if self.active:
            self._blink_timer += dt
            if self._blink_timer >= 0.5:
                self._blink_timer = 0.0
                self._caret_visible = not self._caret_visible
        else:
            self._blink_timer = 0.0
            self._caret_visible = False

    def draw(self, surface: pygame.Surface) -> None:
        """
        Render the text input box, including background, text, placeholder, and caret.
        Args:
            surface: Pygame surface to draw on.
        """
        if not self.visible:
            return

        # Background & Border
        bg = self.color_bg_active if self.active else self.color_bg
        pygame.draw.rect(surface, bg, self.rect, border_radius = 6)
        pygame.draw.rect(surface, self.color_border, self.rect, width = self.border_px, border_radius = 6)

        # Choose text/placeholder
        display_text = self.text if (self.text or self.active) else self.placeholder
        color = self.color_text if (self.text or self.active) else self.color_placeholder

        # Render text
        text_surface = self.font.render(display_text, True, color)
        tx = self.rect.x + self.padding
        ty = self.rect.y + (self.rect.h - text_surface.get_height()) // 2
        surface.blit(text_surface, (tx, ty))

        if self.active and self._caret_visible:
            prefix = self.text[:self.caret_pos]
            prefix_surf = self.font.render(prefix, True, self.color_text)
            cx = tx + prefix_surf.get_width()
            cy1 = self.rect.y + self.padding // 2
            cy2 = self.rect.y + self.rect.h - self.padding // 2
            pygame.draw.line(surface, self.caret_color, (cx, cy1), (cx, cy2), width = 1)

class Dropdown(UIElement):
    """
    Dropdown (select) component for choosing one option from a predefined list.
    Supports:
        - Click to open and close the list
        - Hover highlight over options
        - Click on an option to select it
        - Optional callback on selection change
    """
    def __init__(self, x: int, y: int, width: int, height: int, options: list[str], selected_index: int = 0, *,
                    font: pygame.font.Font | None = None, color_bg: tuple[int, int, int] = (40, 40, 55),
                    color_bg_open: tuple[int, int, int] = (50, 50, 70), color_hover: tuple[int, int, int] = (70, 70, 100),
                    color_border: tuple[int, int, int] = (90, 90, 120), color_text: tuple[int, int, int] = (235, 235, 235),
                    border_px: int = 2, on_change: Callable | None = None):
        """
        Initialize a dropdown selector UI element.
        Args:
            x (int): X coordinate of the top-left corner.
            y (int): Y coordinate of the top-left corner.
            width (int): Width of the dropdown box in pixels.
            height (int): Height of the dropdown box in pixels.
            options (list[str]): List of options to choose from.
            selected_index (int): Index of the initially selected option.
            font (pygame.font.Font | None): Optional pygame Font object. Default system font if None.
            color_bg (tuple[int, int, int]): RGB Background color when closed.
            color_bg_open (tuple[int, int, int]): RGB Background color when opened.
            color_hover (tuple[int, int, int]): RGB Background color for hovered option.
            color_border (tuple[int, int, int]): RGB Border color.
            color_text (tuple[int, int, int]): RGB Text color for displayed text and options.
            border_px (int): Border thickness in pixels.
            on_change (Callable | None): Optional callback triggered when selection changes.
        """
        super().__init__(x, y, width, height)
        self.font = font or pygame.font.SysFont(None, 26)
        self.options = options
        self.selected_index = max(0, min(selected_index, len(options) - 1))
        self.color_bg = color_bg
        self.color_bg_open = color_bg_open
        self.color_hover = color_hover
        self.color_border = color_border
        self.color_text = color_text
        self.border_px = border_px
        self.on_change = on_change

        #internal state
        self.open = False
        self.hover_index: int | None = None

    def _header_rect(self) -> pygame.Rect:
        """
        Return the rectangle area of the dropdown's header (the visible closed part).
        Returns:
            pygame.Rect: The rectangle area of the dropdown's header.
        """
        return self.rect

    def _list_rect(self) -> pygame.Rect:
        """
        Return the rectangle area covering the full list of visible options.
        Returns:
            pygame.Rect: The rectangle area covering the full list of options.
        """
        return pygame.Rect(self.rect.x, self.rect.y + self.rect.h, self.rect.w, self.rect.h * len(self.options))

    def _option_at(self, pos: tuple[int, int]) -> int | None:
        """
        Return the index of the option located at a given mouse position.
        Args:
            pos (tuple[int, int]): Mouse position coordinate.
        Returns:
            int | None: Index of the option under the mouse, or None if none.
        """
        x, y = pos
        if x < self.rect.x or x > self.rect.x + self.rect.width:
            return None
        if y < self.rect.y + self.rect.h or y > self.rect.y + self.rect.h * (len(self.options) + 1):
            return None

        rel_y = y - (self.rect.y + self.rect.h)
        idx = int(rel_y // self.rect.h)
        return idx if 0 <= idx < len(self.options) else None


    def handle_event(self, event: pygame.event.Event) -> None:
        """
        Handle mouse events for dropdown behavior.

        Handles:
            - Left-click on header → toggles open/close state.
            - Mouse hover → highlights the hovered option (when open).
            - Left-click on an option → selects it and triggers on_change callback.
            - Click outside → closes dropdown if open.
        Args:
            event (pygame.event.Event): pygame.Event instance representing user input.
        """
        if not (self.visible and self.enabled):
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._header_rect().collidepoint(event.pos):
                self.open = not self.open
                if not self.open:
                    self.hover_index = None
            elif self.open and self._list_rect().collidepoint(event.pos):
                self.hover_index = self._option_at(event.pos)
            else:
                self.open = False
                self.hover_index = None

        elif event.type == pygame.MOUSEMOTION:
            if self.open:
                self.hover_index = self._option_at(event.pos)

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.open and self._list_rect().collidepoint(event.pos):
                idx = self._option_at(event.pos)
                if idx is not None and idx != self.selected_index:
                    self.selected_index = idx
                    if callable(self.on_change):
                        self.on_change(self.selected_index)
                self.open = False
                self.hover_index = None
            else:
                if not self._header_rect().collidepoint(event.pos):
                    self.open = False
                    self.hover_index = None

    def draw(self, surface: pygame.Surface) -> None:
        """
        Render the dropdown box and its contents onto the given surface.

        When closed:
            - Displays the selected option and a ▼ arrow.
        When opened:
            - Displays all available options in a vertical list with hover highlight.
        Args:
            surface (pygame.Surface): Pygame surface to draw the dropdown onto.
        """
        if not self.visible:
            return

        bg_color = self.color_bg_open if self.open else self.color_bg
        pygame.draw.rect(surface, bg_color, self.rect, border_radius = 6)
        pygame.draw.rect(surface, self.color_border, self.rect, width = self.border_px, border_radius = 6)

        text = self.options[self.selected_index] if self.options else "<empty>"
        text_surface = self.font.render(text, True, self.color_text)
        text_rect = text_surface.get_rect(midleft = (self.rect.x + 10, self.rect.centery))
        surface.blit(text_surface, text_rect)

        # ▼ indicator
        tri_x = self.rect.right - 16
        tri_y = self.rect.centery
        pygame.draw.polygon(surface, self.color_text, [(tri_x, tri_y - 4), (tri_x + 8, tri_y - 4), (tri_x + 4, tri_y + 4)])

        if self.open:
            for i, option in enumerate(self.options):
                opt_rect = pygame.Rect(self.rect.x, self.rect.y + self.rect.h * (i + 1), self.rect.w, self.rect.h)
                hover = (i == self.hover_index)
                color = self.color_hover if hover else self.color_bg_open
                pygame.draw.rect(surface, color, opt_rect)
                pygame.draw.rect(surface, self.color_border, opt_rect, width = 1)
                opt_surf = self.font.render(option, True, self.color_text)
                opt_rect_text = opt_surf.get_rect(midleft = (opt_rect.x + 10, opt_rect.centery))
                surface.blit(opt_surf, opt_rect_text)
