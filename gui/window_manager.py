import pygame
from gui.scene import Scene

class WindowManager:
    """"""
    def __init__(self, width: int = 900, height: int = 700, title: str = "Connect-N"):
        """"""
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
        """"""
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Scene name must be a non-empty string.")

        self.scenes[name] = scene
        if self.active_scene_name is None:
            self.active_scene_name = name

    def set_active_scene(self, name: str) -> None:
        """"""
        if name not in self.scenes:
            raise KeyError(f"Scene {name} does not exist.")
        self.active_scene_name = name

    def get_active_scene(self) -> Scene | None:
        """"""
        if self.active_scene_name is None:
            return None
        return self.scenes[self.active_scene_name]

    def run(self, fps: int = 60) -> None:
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

