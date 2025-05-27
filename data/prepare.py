'''
Initializes the display and creates dictionaries of all the stuff.

Also has a ton of constants used as global configuration variables like screen size and fonts and stuff.
'''

import os
import pygame as pg 

from . import tools



pg.init()

SCREEN_SIZE = (1200, 700)
ORIGINAL_CAPTION = "Boids"
BACKGROUND_COLOR = (20, 20, 20)
SCREEN_RECT = pg.Rect((0, 0), SCREEN_SIZE)
_FONT_PATH = os.path.join("resources", "fonts", "PixelifySans.ttf")
BIG_PIXEL_FONT = pg.font.Font(_FONT_PATH, 80)
PIXEL_FONT = pg.font.Font(_FONT_PATH, 20)
BLOOM_ON = True # Whether to use bloom effect
BOIDS_VISIBLE = True # Whether to draw boids on the screen

# Set up the display
_ICON_PATH = os.path.join("resources", "graphics", "misc", "icon.png")
_Y_OFFSET = (pg.display.Info().current_w - SCREEN_SIZE[0]) // 2
os.environ["SDL_VIDEO_WINDOW_POS"] = f"{_Y_OFFSET}, 25"
pg.display.set_caption(ORIGINAL_CAPTION)
pg.display.set_icon(pg.image.load(_ICON_PATH))
_screen = pg.display.set_mode(SCREEN_SIZE, pg.RESIZABLE)

# Display loading screen until loading is done
_screen.fill(BACKGROUND_COLOR)
_render = PIXEL_FONT.render("Loading...", 0, pg.Color("white"))
_screen.blit(_render, _render.get_rect(center=SCREEN_RECT.center))
pg.display.update()

# General Constants

# Resource Paths
FONTS = tools.load_all_fonts(os.path.join("resources", "fonts"))
MUSIC = tools.load_all_music(os.path.join("resources", "music"))
SFX = tools.load_all_sfx(os.path.join("resources", "sound"))

# Load all graphics from the given directories

def graphics_from_directories(directories):
    """
    Load all graphics from the given directories.
    """
    base_path = os.path.join("resources", "graphics")
    # Load all graphics from the given directories
    GFX = {}
    for directory in directories:
        path = os.path.join(base_path, directory)
        GFX[directory] = tools.load_all_gfx(path)
    return GFX

_SUB_DIRECTORIES = ["backgrounds", "creatures", "misc", "objects"]
GFX = graphics_from_directories(_SUB_DIRECTORIES)