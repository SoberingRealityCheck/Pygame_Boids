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
    
    def add_boid(self, position=None, velocity=None):
        if position is None:
            position = np.random.rand(2) * [self.width, self.height]
        if velocity is None:
            velocity = (np.random.rand(2) - 0.5) * 10
        self.positions = np.vstack((self.positions, position))
        self.velocities = np.vstack((self.velocities, velocity))
        self.num_boids += 1
    
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

    # Parameters
    separation_dist = 25.0
    alignment_dist = 50.0
    cohesion_dist = 50.0
    max_speed = 4.0
    max_force = 0.05

    for i in prange(N):
        pos = positions[i]
        vel = velocities[i]

        # Initialize rule vectors
        separation = np.zeros(2)
        alignment = np.zeros(2)
        cohesion = np.zeros(2)
        total_sep = 0
        total_ali = 0
        total_coh = 0

        for j in range(N):
            if i == j:
                continue
            diff = positions[j] - pos
            dist = np.linalg.norm(diff)
            if dist < 1e-5:
                continue

            # Separation
            if dist < separation_dist:
                separation -= (diff) / dist
                total_sep += 1

            # Alignment
            if dist < alignment_dist:
                alignment += velocities[j]
                total_ali += 1

            # Cohesion
            if dist < cohesion_dist:
                cohesion += positions[j]
                total_coh += 1

        # Finalize rule vectors
        if total_sep > 0:
            separation /= total_sep
        if total_ali > 0:
            alignment /= total_ali
            alignment = alignment / (np.linalg.norm(alignment) + 1e-8) * max_speed - vel
        if total_coh > 0:
            cohesion /= total_coh
            cohesion = cohesion - pos
            cohesion = cohesion / (np.linalg.norm(cohesion) + 1e-8) * max_speed - vel

        # Combine rules with weights
        steer = (
            1.5 * separation +
            1.0 * alignment +
            1.0 * cohesion
        )

        # Limit steering force
        norm = np.linalg.norm(steer)
        if norm > max_force:
            steer = steer / norm * max_force

        # Update velocity and position
        new_vel = vel + steer
        speed = np.linalg.norm(new_vel)
        if speed > max_speed:
            new_vel = new_vel / speed * max_speed

        new_velocities[i] = new_vel
        new_positions[i] = pos + new_vel

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
