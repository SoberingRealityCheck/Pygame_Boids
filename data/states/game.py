import pygame as pg 

from .. import prepare, state_machine

from ..boids_logic import BoidFlock

class Game(state_machine._State):
    """
    This state is updated while the game is running.
    """
    def __init__(self):
        state_machine._State.__init__(self)
        self.next = "TITLE"
        self.done = False
        self.quit = False
        self.start_time = None

    def startup(self, now, persistent):
        """Initialize the game state."""
        self.persist = persistent
        self.start_time = now
        self.flock = BoidFlock(num_boids=100)
        print("Game started at:", self.start_time)
        self.elements = self.make_elements()
        self.now = now

    def make_elements(self):
        """Create the elements for the game state."""
        group = pg.sprite.LayeredUpdates()
        group.add(BoidCounter(self.flock), layer=1)
        return group
    
    def update(self, keys, now):
        """Update the game state."""
        self.now = now
        self.flock.update(now)
        if pg.mouse.get_pressed()[0]:
            mouse_pos = pg.mouse.get_pos()
            self.flock.add_boid(mouse_pos)
        # Game logic goes here

    def draw(self, surface, interpolate):
        """Draw the game state."""
        surface.fill(prepare.BACKGROUND_COLOR)
        self.flock.draw(surface)
        for element in self.elements:
            element.draw(surface)
        # Drawing code goes here

class BoidCounter(pg.sprite.Sprite):
    """
    A simple class to count the number of boids in the flock.
    """
    def __init__(self, flock, *groups):
        pg.sprite.Sprite.__init__(self, *groups)
        self.flock = flock

    def count(self):
        return self.flock.num_boids
    
    def draw(self, surface):
        count_text = f"Boids: {self.count()}"
        text_surface = prepare.PIXEL_FONT.render(count_text, True, pg.Color("white"))
        surface.blit(text_surface, (10, 10))