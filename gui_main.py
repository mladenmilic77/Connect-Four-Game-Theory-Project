from gui.window_manager import WindowManager
from gui.main_menu import MainMenu
from gui.game_scene import GameScene

def main() -> int:
    wm = WindowManager(900, 700, "Connect-N")

    # Scene
    menu = MainMenu()
    game = GameScene()



    def on_start_and_switch():
        menu.start_game()
        if menu.selected_config:
            game.set_config(menu.selected_config)

    menu.btn_start.on_click = on_start_and_switch

    wm.add_scene("MainMenu", menu)
    wm.add_scene("Game", game)

    wm.set_active_scene("MainMenu")

    wm.run()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
