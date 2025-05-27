'''
This is the main function for the boids simulation.

'''
import os
print(os.getcwd())

from . import tools, prepare
from .states import title, splash, game

def main():
    print("Hello, world!")
    app = tools.Control(prepare.ORIGINAL_CAPTION)
    state_dict = {
                "SPLASH"  : splash.Splash(),
                "TITLE"   : title.Title(),
                "GAME"    : game.Game(),
                }
    app.state_machine.setup_states(state_dict, "SPLASH")
    app.main()