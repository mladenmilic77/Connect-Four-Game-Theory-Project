import pygame
from abc import ABC, abstractmethod

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
    def __init__(self, x: int, y: int, text: str, font: pygame.font.Font | None = None, color: tuple[int, int, int] = (230, 230, 230)):
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

    # noinspection PyUnresolvedReferences,PyTypeHints
    def __init__(self, x: int, y: int, width: int, height: int, text: str, on_click: callable = None, *, font: pygame.font.Font | None = None,
                    color_bg: tuple[int, int, int] = (40, 40, 55), color_bg_hover: tuple[int, int, int] = (55, 55, 80),
                    color_border: tuple[int, int, int] = (80, 80, 80),color_text: tuple[int, int, int] = (235, 235, 235), border_px: int = 2):
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
