'''
Fundamental control class and resource loading functions.
Control class is used to manage the game loop.
'''

import os
import pygame as pg

# Import State Machine
# from . import state_machine

TIME_PER_UPDATE = 16.0 #Milliseconds


class Control(object):
    """
    Fundamental control class for the game.
    """
    def __init__(self, caption):
        self.screen = pg.display.get_surface()
        self.caption = caption
        self.done = False
        self.clock = pg.time.Clock()
        self.fps = 60.0
        self.fps_visible = True
        self.now = 0.0
        self.keys = pg.key.get_pressed()
        self.mouse = pg.mouse.get_pos()
        # State Machine
    
    def update(self):
        '''
        Update the game state.
        '''
        self.now = pg.time.get_ticks()
        # State Machine
    
    def draw(self, interpolate):
        if not self.done:
            pg.display.update()
            self.show_fps()
    
    def event_loop(self):
        '''
        Handle events and pass them to the state machine.
        f5 toggles the FPS display.
        '''
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.done = True
            elif event.type == pg.KEYDOWN:
                self.keys = pg.key.get_pressed()
                self.toggle_show_fps(event.key)
            elif event.type == pg.KEYUP:
                self.keys = pg.key.get_pressed()
            # State Machine
    
    def toggle_show_fps(self, key):
        '''
        Toggle the FPS display.
        '''
        if key == pg.K_F5:
            self.fps_visible = not self.fps_visible
            if not self.fps_visible:
                pg.display.set_caption(self.caption)
    
    def show_fps(self):
        '''
        Show the FPS in the window handle if fps_visible is True.
        '''
        if self.fps_visible:
            fps = self.clock.get_fps()
            with_fps = f"{self.caption} - FPS: {fps:.2f}"
            pg.display.set_caption(with_fps)
    
    def main(self):
        '''
        Main loop for the entire program.
        '''
        lag = 0.0
        while not self.done:
            lag += self.clock.tick(self.fps)
            self.event_loop()
            while lag >= TIME_PER_UPDATE:
                self.update()
                lag -= TIME_PER_UPDATE
            self.draw(lag/TIME_PER_UPDATE)

# Maybe define an animation class here?


# Resource loading functions
def load_all_gfx(directory, colorkey=(255,0,255), accept=('.png', '.jpg', '.jpeg', '.gif')):
    """
    Load all graphics from the given directory.
    """
    graphics = {}
    for pic in os.listdir(directory):
        name, ext = os.path.splitext(pic)
        if ext.lower() in accept:
            img=  pg.image.load(os.path.join(directory, pic))
            if img.get_alpha():
                img = img.convert_alpha()
            else:
                img = img.convert()
                img.set_colorkey(colorkey)
            graphics[name] = img
    return graphics

def load_all_music(directory, accept=('.ogg', '.wav', '.mp3', '.mdi')):
    '''
    Create a dictionary of paths to all music files in the given directory.
    '''
    songs = {}
    for song in os.listdir(directory):
        name, ext = os.path.splitext(song)
        if ext.lower() in accept:
            songs[name] = os.path.join(directory, song)
    return songs


def load_all_fonts(directory, accept=('.ttf')):
    """
    Create a dictionary of paths to all font files in the given directory.
    """
    return load_all_music(directory, accept)


def load_all_sfx(directory, accept=('.ogg', '.wav', '.mp3', '.mdi')):
    '''
    Load all sound effects from the given directory.
    '''
    effects = {}
    for fx in os.listdir(directory):
        name, ext = os.path.splitext(fx)
        if ext.lower() in accept:
            effects[name] = pg.mixer.Sound(os.path.join(directory, fx))
    return effects