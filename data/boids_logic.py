import numpy as np
import pygame as pg
from numba import njit, prange
from .prepare import BLOOM_ON, BOIDS_VISIBLE

class Boid:
    def __init__(self, position, velocity):
        self.position = position  # Vector2
        self.velocity = velocity  # Vector2

    def update(self, boids):
        # Apply boid rules to adjust velocity
        self.flock(boids)
        self.position += self.velocity

    def flock(self, boids):
        # Calculate and apply separation, alignment, cohesion
        pass

    

class BoidFlock:
    def __init__(self, num_boids, width=800, height=600):
        self.num_boids = num_boids
        self.width = width
        self.height = height
        self.positions = np.random.rand(num_boids, 2)  # Example screen size
        self.positions[:, 0] *= width
        self.positions[:, 1] *= height # Scale positions to screen size
        self.velocities = (np.random.rand(num_boids, 2) - 0.5) * 10

    def update(self, now):
        self.positions, self.velocities = boid_update(
            self.positions, self.velocities
        )
        self.positions = loop_out_of_bounds(self.positions, self.width, self.height)
    
    def draw(self, surface):
        if not BOIDS_VISIBLE:
            return
        # Draw the boid on the surface
        for pos in self.positions:
            x, y = pos
            render_position = (int(x), int(y))
            width, height = self.width, self.height
            if BLOOM_ON:
                    bloom_color = [float(55 * x / width), float(55 * y / height), 20]
                    #print("BLOOM COLOR", bloom_color)
                    pg.draw.circle(surface, bloom_color, render_position, 5)
                
            boid_color = [float(255 * x / width), float(255 * y / height), 200]
            #print("BOID COLOR", boid_color)
            pg.draw.circle(surface, boid_color, render_position, 1)
            pass


@njit(parallel=True)
def boid_update(positions, velocities):
    N = positions.shape[0]
    new_positions = positions.copy()
    new_velocities = velocities.copy()
    # Example: simple movement, replace with flocking logic
    for i in prange(N):
        # Compute separation, alignment, cohesion here using array ops
        new_positions[i] += new_velocities[i]
    return new_positions, new_velocities

@njit(parallel=True)
def loop_out_of_bounds(positions, width, height):
    """
    Loop all positions around if they go out of bounds.
    positions: numpy array of shape (N, 2)
    """
    positions[:, 0] = np.mod(positions[:, 0], width)
    positions[:, 1] = np.mod(positions[:, 1], height)
    return positions
