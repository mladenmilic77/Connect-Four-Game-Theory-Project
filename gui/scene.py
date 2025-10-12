import pygame
from abc import ABC, abstractmethod

class Scene(ABC):
    """
    Abstract class that defines the scene interface.
    """
    def __init__(self, name: str):
        """
        Initialize a scene with a unique name and default state.
        Args:
            name (str): Name of the scene.
        Raises:
            ValueError: If provided name is not a non-empty string.
        """
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Scene name must be a non-empty string.")
        self.name = name
        self.is_active = True
        self.requested_scene = None

    @abstractmethod
    def handle_events(self, event: list[pygame.event.Event]) -> None:
        """
        Handle events received from the scene.
        Args:
            event (list[pygame.event.Event]): List of events received from the scene.
        """
        raise NotImplementedError()

    @abstractmethod
    def update(self, dt: float) -> None:
        """
        Update the scene state.
        Args:
            dt (float): Elapsed time in seconds since the previous frame.
        """
        raise NotImplementedError()

    @abstractmethod
    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the scene to the surface.
        Args:
            surface (pygame.Surface): Surface to draw to.
        """
        raise NotImplementedError()

    @abstractmethod
    def request_switch(self, next_scene_name:str) -> None:
        """
        Ask the WindowManager to switch to another scene.
        Args:
            next_scene_name (str): Name of the target scene.
        Raises:
            ValueError: If provided name is not a non-empty string.
        """
        if not isinstance(next_scene_name, str) or not next_scene_name.strip():
            raise ValueError("Next scene name must be a non-empty string.")
        self.requested_scene = next_scene_name
