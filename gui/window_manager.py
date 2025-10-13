import pygame
from gui.scene import Scene

class WindowManager:
    """
    Manages the main Pygame window and controls scene switching.
    This class:
        - Initializes the main Pygame display and clock.
        - Keeps a registry of all scenes (Menu, Game).
        - Runs the main event loop that updates and draws the active scene.
        - Handles transitions between scenes via Scene.request_switch().
    """
    def __init__(self, width: int = 900, height: int = 700, title: str = "Connect-N"):
        """
        Initialize the Pygame window and prepare the scene manager.
        Args:
            width (int, optional): Width of the Pygame window in pixels.
            height (int, optional): Height of the Pygame window in pixels.
            title (str, optional): Title of the Pygame window.
        """
        self.size = width, height
        self.title = title

        # pygame init
        pygame.init()
        pygame.display.set_caption(self.title)
        self.screen = pygame.display.set_mode(self.size, pygame.SCALED | pygame.RESIZABLE, vsync = 1)
        self.clock = pygame.time.Clock()

        #Scene management
        self.scenes: dict[str, Scene] = {}
        self.active_scene_name: str | None = None
        self.running: bool = False

        #TODO use Theme class here maybe
        self.bg_color = (18,18,18)

    def add_scene(self, name: str, scene: Scene) -> None:
        """
        Register a new scene within the window manager.
        Args:
            name (str): Unique string identifier for the scene.
            scene (Scene): An instance of a class derived from Scene.
        Raises:
            ValueError: If the scene name is empty or not a string.
        """
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Scene name must be a non-empty string.")

        self.scenes[name] = scene
        if self.active_scene_name is None:
            self.active_scene_name = name

    def set_active_scene(self, name: str) -> None:
        """
        Set the current active scene by name.
        Args:
            name (str): Name of the scene to activate.
        Raises:
            ValueError: If the provided scene name does not exist.
        """
        if name not in self.scenes:
            raise KeyError(f"Scene {name} does not exist.")
        self.active_scene_name = name

    def get_active_scene(self) -> Scene | None:
        """
        Retrieve the currently active scene instance.
        Returns:
            The active Scene object, or None if no active scene exists.
        """
        if self.active_scene_name is None:
            return None
        return self.scenes[self.active_scene_name]

    def run(self, fps: int = 60) -> None:
        """
        Start the main Pygame loop and manage scene updates and transitions.
        Args:
            fps (int, optional): Frames per second limit for the main loop.
        Raises:
            RuntimeError: If no active scene is set before calling run().
        """
        if self.active_scene_name is None:
            raise RuntimeError("No active scene set. Add at least one scene before run().")

        self.running = True
        try:
            while self.running:
                dt = self.clock.tick(fps) / 1000.0

                events = pygame.event.get()
                for event in events:
                    if event.type == pygame.QUIT:
                        self.running = False

                scene = self.get_active_scene()
                if scene is None:
                    self.running = False
                    break

                scene.handle_events(events)
                scene.update(dt)

                if getattr(scene, "requested_scene", None):
                    target = scene.requested_scene
                    scene.requested_scene = None
                    if target in self.scenes:
                        self.active_scene_name = target
                        scene = self.get_active_scene()
                    else:
                        print(f"[WindowManager] Unknown scene requested: '{target}'")

                self.screen.fill(self.bg_color)
                scene.draw(self.screen)
                pygame.display.flip()

        finally:
            pygame.quit()

