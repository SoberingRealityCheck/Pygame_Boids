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
        self.flock = BoidFlock(num_boids=100, width=prepare.SCREEN_RECT.width, height=prepare.SCREEN_RECT.height)
        print("Game started at:", self.start_time)
        self.now = now

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
        # Drawing code goes here