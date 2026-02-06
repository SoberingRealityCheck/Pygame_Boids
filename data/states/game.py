import pygame as pg 

from .. import prepare, state_machine

from ..boids_logic import BoidFlock

class Game(state_machine._State):
    """
    This state is updated while the game is running.
    """

    BACKGROUND_COLOR = (0, 0, 0, 180)  # RGBA for semi-transparent background
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
        self.flock = BoidFlock(num_boids=3)
        print("Game started at:", self.start_time)
        self.elements = self.make_elements()
        self.now = now
        self.menu_visible = False

    def make_elements(self):
        group = pg.sprite.LayeredUpdates()
        group.add(BoidCounter(self.flock), layer=1)
        group.add(BoidParameterMenu(self.flock), layer=2)
        return group
    
    def update(self, keys, now, mouse):
        self.now = now
        self.mouse = mouse
        self.flock.update(now)
        if keys[pg.K_SPACE]:
                self.flock.add_boid(self.mouse)

    def get_event(self, event):
        """Handle events for the game state."""
        if event.type == pg.QUIT:
            self.quit = True
        elif event.type == pg.KEYDOWN and event.key == pg.K_TAB:
            self.menu_visible = not self.menu_visible
        elif event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
            self.flock.add_boid(self.mouse)
        else:
            for element in self.elements:
                if hasattr(element, 'handle_event'):
                    element.handle_event(event)
    
    def _apply_bloom(self, surface, intensity=0.5):
        """Apply a screenwide bloom by downsampling, blurring, and blending back."""
        w, h = surface.get_size()
        # Two-pass bloom at different scales for a softer glow
        for divisor in (8, 4):
            small = pg.transform.smoothscale(surface, (w // divisor, h // divisor))
            glow = pg.transform.smoothscale(small, (w, h))

            glow.set_alpha(int(255 * intensity))
            surface.blit(glow, (0, 0), special_flags=pg.BLEND_RGB_ADD)

    def draw(self, surface, interpolate):
        """Draw the game state."""
        surface.fill(prepare.BACKGROUND_COLOR)
        self.flock.draw(surface)
        if self.flock.bloom_on:
            self._apply_bloom(surface)
        for element in self.elements:
            if isinstance(element, BoidParameterMenu):
                element.update_position(surface)
                if self.menu_visible:
                    element.draw(surface)
                else:
                    continue  # Skip drawing the menu if not visible
            if isinstance(element, BoidCounter):
                if self.menu_visible:
                    element.draw(surface)
                else:
                    continue # Skip drawing the counter if not visible
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
        
class BoidParameterMenu(pg.sprite.Sprite):
    """
    A fixed menu in the top right with draggable sliders to adjust BoidFlock parameters.
    """
    WIDTH = 220
    HEIGHT = 250
    TITLE_HEIGHT = 30
    SPACE_BETWEEN_SLIDERS = 30
    SLIDER_WIDTH = 160
    SLIDER_HEIGHT = 20
    TOGGLE_SIZE = 16

    def __init__(self, flock, *groups):
        super().__init__(*groups)
        self.flock = flock
        self.rect = pg.Rect(prepare.SCREEN_SIZE[0] - self.WIDTH - 10, 10, self.WIDTH, self.HEIGHT)
        # List of parameters: (label, attr, min, max, step)
        self.params = [
            ("Mass", "boid_mass", 1.0, 20.0, 0.5),
            ("Separation", "sep_weight", 0.0, 10.0, 0.1),
            ("Alignment", "ali_weight", 0.0, 10.0, 0.1),
            ("Cohesion", "coh_weight", 0.0, 10.0, 0.1),
            ("Centering", "center_weight", 0.0, 1.0, 0.01),
        ]

    def update_position(self, surface):
        """Update menu position to stay in the top right corner."""
        width = surface.get_width()
        self.rect.x = width - self.WIDTH - 10
        # self.rect.y stays at 10 (top)
    
    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            # Check bloom toggle
            toggle_y = self.rect.y + self.TITLE_HEIGHT + len(self.params) * self.SPACE_BETWEEN_SLIDERS + 10
            toggle_rect = pg.Rect(self.rect.x + 10, toggle_y, self.TOGGLE_SIZE, self.TOGGLE_SIZE)
            if toggle_rect.collidepoint(event.pos):
                self.flock.bloom_on = not self.flock.bloom_on
                return
            for i, (label, attr, mn, mxv, step) in enumerate(self.params):
                slider_rect = pg.Rect(self.rect.x + 10, self.rect.y + 40 + i*self.SPACE_BETWEEN_SLIDERS, self.SLIDER_WIDTH, self.SLIDER_HEIGHT)
                if slider_rect.collidepoint(event.pos):
                    rel_x = event.pos[0] - (self.rect.x + 10)
                    rel_x = max(0, min(rel_x, self.SLIDER_WIDTH))
                    value = mn + (mxv - mn) * (rel_x / self.SLIDER_WIDTH)
                    value = round(value / step) * step
                    setattr(self.flock, attr, value)
                    break

    def draw(self, surface):
        # Create a transparent surface for the menu
        menu_surf = pg.Surface((self.WIDTH, self.HEIGHT), pg.SRCALPHA)
        # Draw semi-transparent background (RGBA)
        menu_surf.fill((30, 30, 40, 180))  # 180/255 alpha for slight transparency

        font = prepare.PIXEL_FONT
        # Optional: subtle title
        title = font.render("Boid Params", True, (180, 180, 180))
        menu_surf.blit(title, (10, 8))

        # Draw minimal sliders
        for i, (label, attr, mn, mxv, step) in enumerate(self.params):
            y = self.TITLE_HEIGHT + i * self.SPACE_BETWEEN_SLIDERS
            slider_rect = pg.Rect(10, y, self.SLIDER_WIDTH, self.SLIDER_HEIGHT)
            value = getattr(self.flock, attr)
            pct = (value - mn) / (mxv - mn)
            handle_x = int(slider_rect.x + pct * slider_rect.width)

            # Slider bar (thin, light)
            pg.draw.rect(menu_surf, (100, 100, 120, 180), slider_rect, border_radius=4)
            # Slider fill
            pg.draw.rect(menu_surf, (100, 200, 255, 200), (slider_rect.x, slider_rect.y, handle_x - slider_rect.x, slider_rect.height), border_radius=4)
            # Handle (small circle)
            pg.draw.circle(menu_surf, (255, 255, 180, 220), (handle_x, slider_rect.y + slider_rect.height // 2), 6)
            # Label (small, light)
            label_surf = font.render(f"{label[0]}: {value:.1f}", True, (200, 200, 200))
            menu_surf.blit(label_surf, (slider_rect.right + 8, y - 4))

        # Bloom toggle checkbox
        toggle_y = self.TITLE_HEIGHT + len(self.params) * self.SPACE_BETWEEN_SLIDERS + 10
        toggle_rect = pg.Rect(10, toggle_y, self.TOGGLE_SIZE, self.TOGGLE_SIZE)
        pg.draw.rect(menu_surf, (100, 100, 120, 180), toggle_rect, border_radius=2)
        if self.flock.bloom_on:
            inner = toggle_rect.inflate(-6, -6)
            pg.draw.rect(menu_surf, (100, 200, 255, 220), inner, border_radius=1)
        bloom_label = font.render("Bloom", True, (200, 200, 200))
        menu_surf.blit(bloom_label, (10 + self.TOGGLE_SIZE + 8, toggle_y - 2))

        # Blit the menu surface onto the main surface
        surface.blit(menu_surf, (self.rect.x, self.rect.y))