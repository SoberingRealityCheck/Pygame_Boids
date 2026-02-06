import numpy as np
import pygame as pg
from numba import njit, prange
from .prepare import BLOOM_ON, BOIDS_VISIBLE


class BoidFlock:
    def __init__(self, num_boids, weights=None):
        self.num_boids = num_boids
        self.width = 1200
        self.height = 800
        self.positions = np.random.rand(num_boids, 2)
        self.positions[:, 0] *= self.width
        self.positions[:, 1] *= self.height # Scale positions to full world size
        self.velocities = (np.random.rand(num_boids, 2) - 0.5) * 10
        self.scale_x = 1.0
        self.scale_y = 1.0
        # Initialize the weights with starting values
        self.sep_weight = 2.0  # Weight for separation rule
        self.ali_weight = 1.0
        self.coh_weight = 1.0
        # Radius for each rule
        self.sep_radius = 20.0
        self.ali_radius = 50.0
        self.coh_radius = 50.0
        # Maximum speed and force
        self.max_speed = 10.0
        self.max_force = 0.1
        # Mass of each boid
        self.boid_mass = 5.0
        # Weight for centering force (pulls boids toward center of simulation)
        self.center_weight = 0.1
        self.bloom_on = True
        if weights is not None:
            for key in weights:
                if key in ['sep_weight', 'ali_weight', 'coh_weight',
                                    'sep_radius', 'ali_radius', 'coh_radius',
                                    'max_speed', 'max_force', 'boid_mass', 'center_weight']:
                    setattr(self, key, weights[key])
    
    def update(self, now):
        self.positions, self.velocities = boid_update(self.positions, self.velocities, self.sep_weight,
                                                    self.ali_weight, self.coh_weight,
                                                    self.sep_radius, self.ali_radius, self.coh_radius,
                                                    self.max_speed, self.max_force, self.boid_mass,
                                                    self.center_weight, self.width, self.height)
        self.positions = loop_out_of_bounds(self.positions, self.width, self.height)
    
    def add_boid(self, position=None, velocity=None):
        if position is None:
            position = np.random.rand(2) * [self.width, self.height]
        if velocity is None:
            velocity = (np.random.rand(2) - 0.5) * 10
        # Scale position to window size
        scaled_x = position[0] / self.scale_x
        scaled_y = position[1] / self.scale_y
        position = (scaled_x, scaled_y)
        
        self.positions = np.vstack((self.positions, position))
        self.velocities = np.vstack((self.velocities, velocity))
        self.num_boids += 1
    
    def draw(self, surface):
        if not BOIDS_VISIBLE:
            return
        # Get surface dimensions
        current_window_height = surface.get_height()
        current_window_width = surface.get_width()
        
        self.scale_x = current_window_width / self.width
        self.scale_y = current_window_height / self.height
        # Draw the boid on the surface
        
        for pos in self.positions:
            x, y = pos
            render_position = (int(x * self.scale_x), int(y * self.scale_y))
            width, height = self.width, self.height
            ''' 
            if BLOOM_ON:
                    bloom_color = [float(55 * x / width), float(55 * y / height), 20]
                    #print("BLOOM COLOR", bloom_color)
                    pg.draw.circle(surface, bloom_color, render_position, 5)
            '''
                
            boid_color = [float(100 * x / width) + 155, float(100 * y / height) + 155, 255]
            #print("BOID COLOR", boid_color)
            pg.draw.circle(surface, boid_color, render_position, 1)
            pass


@njit(parallel=True)
def boid_update(positions, velocities, sep_weight, ali_weight, coh_weight,
                 separation_dist, alignment_dist, cohesion_dist,
                 max_speed, max_force, boid_mass,
                 center_weight, world_width, world_height):
    """
    Update all boid positions and velocities using the three flocking rules:
    separation, alignment, and cohesion, plus a centering force.
    """
    
    N = positions.shape[0]
    new_positions = positions.copy()
    new_velocities = velocities.copy()

    for i in prange(N):
        pos = positions[i]
        vel = velocities[i]

        # Initialize rule vectors and neighbor counters
        separation = np.zeros(2)
        alignment = np.zeros(2)
        cohesion = np.zeros(2)
        total_sep = 0
        total_ali = 0
        total_coh = 0

        # Loop over all other boids to compute rule effects
        for j in range(N):
            if i == j:
                continue
            diff = positions[j] - pos
            dist = np.linalg.norm(diff)
            if dist < 1e-5:
                continue

            # Separation: steer away from close neighbors
            if dist < separation_dist:
                if dist > 0:
                    separation -= (diff) / (dist * dist)
                else:
                    separation -= 1 # Avoid division by zero
                total_sep += 1

            # Alignment: match velocity with nearby boids
            if dist < alignment_dist:
                alignment += velocities[j]
                total_ali += 1

            # Cohesion: move toward the average position of nearby boids
            if dist < cohesion_dist:
                cohesion += positions[j]
                total_coh += 1

        # Average and finalize rule vectors
        norm_sep = np.linalg.norm(separation)
        if norm_sep > 0:
            separation = separation / norm_sep * max_speed - vel
        if total_ali > 0:
            alignment /= total_ali
            # Desired velocity for alignment
            alignment = alignment / (np.linalg.norm(alignment) + 1e-8) * max_speed - vel
        if total_coh > 0:
            cohesion /= total_coh
            # Desired velocity toward center of mass
            cohesion = cohesion - pos
            cohesion = cohesion / (np.linalg.norm(cohesion) + 1e-8) * max_speed - vel

        # Centering: steer toward the center of the world
        center = np.array([world_width / 2.0, world_height / 2.0])
        to_center = center - pos
        dist_to_center = np.linalg.norm(to_center)
        centering = np.zeros(2)
        if dist_to_center > 0:
            # Desired velocity toward center, scaled by distance from center
            centering = to_center / dist_to_center * max_speed - vel

        # Combine the three rules with weights
        steer = (
            sep_weight * separation +
            ali_weight * alignment +
            coh_weight * cohesion +
            center_weight * centering
        )

        # Limit the steering force to max_force
        norm = np.linalg.norm(steer)
        if norm > max_force:
            steer = steer / norm * max_force
        
        # Scale steering by boid mass
        steer /= boid_mass

        # Update velocity with steering, limit to max_speed
        new_vel = vel + steer
        speed = np.linalg.norm(new_vel)
        if speed > max_speed:
            new_vel = new_vel / speed * max_speed

        # Update arrays with new velocity and position
        new_velocities[i] = new_vel
        new_positions[i] = pos + new_vel

    return new_positions, new_velocities

@njit(parallel=True)
def loop_out_of_bounds(positions, width, height):
    """
    Loop all positions around if they go out of bounds.
    positions: numpy array of shape (N, 2)
    """
    # Use modulo to wrap positions around the world edges
    positions[:, 0] = np.mod(positions[:, 0], width)
    positions[:, 1] = np.mod(positions[:, 1], height)
    return positions
