"""
State for the Title scene.
"""

import pygame as pg

from .. import prepare, state_machine, main
SPACE_COLOR = (10, 10, 20)
SPACE_RECT = pg.Rect(0, 0, 1200, 700)


class Title(state_machine._State):
    """ 
    This state is updated while the game is in the title screen.
    """
    def __init__(self):
        state_machine._State.__init__(self)
        self.elements = self.make_elements()
    
    def startup(self, now, persistent):
        self.persist = persistent
        self.start_time = now
        self.elements = self.make_elements()
    
    def update(self, keys, now, mouse):
        self.now = now
        self.elements.update(now, mouse)
        for element in self.elements:
            if element.done:
                self.done = True
                self.next = element.next
                break
    
    def draw(self, surface, interpolate):
        surface.fill(SPACE_COLOR, SPACE_RECT)
        _titletext = prepare.BIG_PIXEL_FONT.render("BOIDS", 0, pg.Color("white"))
        surface.blit(_titletext, _titletext.get_rect(center=(SPACE_RECT.center[0], SPACE_RECT.center[1]-50)))
        _subtitletext = prepare.PIXEL_FONT.render("A Clay Goldsmith Game", 0, pg.Color("white"))
        surface.blit(_subtitletext, _subtitletext.get_rect(center=(SPACE_RECT.center[0], SPACE_RECT.center[1])))
        self.elements.draw(surface)
    
    def make_elements(self):
        """ 
        Create the elements for the title screen.
        """
        group = pg.sprite.LayeredUpdates()
        group.add(StartButton(), layer=1)
        return group

class StartButton(pg.sprite.Sprite):
    def __init__(self, *groups):
        pg.sprite.Sprite.__init__(self, *groups)
        self.raw_image = render_font("PixelifySans", 30, "Start", (0, 255, 255))
        self.hover_image = render_font("PixelifySans", 30, "Start", (255, 255, 0))
        self.null_image = pg.Surface((1,1)).convert_alpha()
        self.null_image.fill((0,0,0,0))
        self.image = self.raw_image
        center = (prepare.SCREEN_RECT.centerx, prepare.SCREEN_RECT.centery+50)
        self.rect = self.image.get_rect(center=center)
        self.hover = False
        self.done = False
        self.next = "GAME"
    
    def check_hover(self, mouse):
        """
        Check if the mouse is hovering over the button.
        """
        self.hover = self.rect.collidepoint(mouse)
    
    def check_click(self):
        if self.hover and pg.mouse.get_pressed()[0]:
            self.done = True
            
    
    def update(self, now, mouse, *args):
        self.check_hover(mouse)
        self.image = self.raw_image if self.hover else self.hover_image
        self.check_click()

def render_font(font, size, msg, color=(255,255,255)):
        """
        Takes the name of a loaded font, the size, and the color and returns
        a rendered surface of the msg given.
        """
        selected_font = pg.font.Font(prepare.FONTS[font], size)
        return selected_font.render(msg, 1, color)