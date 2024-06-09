import time
import pygame
from pygame import Vector2
import random
import threading
import sys

# Constants
num_threads = 4
width, height = 700, 700
gravity = Vector2(0, 9.81)

class Helper:
    @classmethod
    def get_color(cls, iteration, step=16):
        factor = (iteration * step) % (256 * 6)
        stage = factor // 256
        r = 255 if stage < 2 else 255 - (factor % 256) if stage < 3 else 0 if stage < 5 else (factor % 256)
        g = 0 if stage < 1 else factor % 256 if stage < 2 else 255 if stage < 4 else 255 - (factor % 256) if stage < 5 else 0
        b = 255 - (factor % 256) if stage < 1 else 0 if stage < 3 else factor % 256 if stage < 4 else 255
        return (r, g, b)

class Particle:
    def __init__(self, pos, radius, color, mass=1):
        self.pos = Vector2(pos)
        self.prev_pos = Vector2(pos)
        self.radius = radius
        self.color = color
        self.mass = mass
        self.acceleration = Vector2(0, 0)

    def accelerate(self, force):
        self.acceleration += force / self.mass

    def update(self, dt):
        # Calculate velocity
        velocity = self.pos - self.prev_pos
        # Store previous position
        self.prev_pos = self.pos
        # Perform Verlet integration
        self.pos = self.pos + velocity + self.acceleration * dt * dt
        # Reset acceleration
        self.acceleration *= 0

        # Check bounds
        self.check_bounds()

    def check_bounds(self):
        if self.pos.x - self.radius < 0:
            self.pos.x = self.radius
            self.prev_pos.x = self.pos.x + (self.pos.x - self.prev_pos.x) * -0.5

        if self.pos.x + self.radius > width:
            self.pos.x = width - self.radius
            self.prev_pos.x = self.pos.x + (self.pos.x - self.prev_pos.x) * -0.5

        if self.pos.y - self.radius < 0:
            self.pos.y = self.radius
            self.prev_pos.y = self.pos.y + (self.pos.y - self.prev_pos.y) * -0.5

        if self.pos.y + self.radius > height:
            self.pos.y = height - self.radius
            self.prev_pos.y = self.pos.y + (self.pos.y - self.prev_pos.y) * -0.5

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.pos.x), int(self.pos.y)), self.radius)

    def resolve_collision(self, other):
        if self is other:
            return

        distance = self.pos.distance_to(other.pos)
        if distance < self.radius + other.radius:
            distance_vec = self.pos - other.pos
            if not distance_vec.length() == 0:
                overlap = 0.5 * (distance - self.radius - other.radius)
                self.pos -= overlap * distance_vec.normalize()
                other.pos += overlap * distance_vec.normalize()


class Simulation:
    def __init__(self, width, height, threads = 1):
        # Initialize Pygame
        pygame.init()
        self.width = width
        self.height = height
        self.particles = []
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        self.thread_count = threads

    def add_particles(self, particles):
        self.particles.extend(particles)

    def update(self, dt):
        for i, particle in enumerate(self.particles):
            particle.accelerate(gravity*100)
            particle.update(dt)
            for other_particle in self.particles[i+1:]:
                particle.resolve_collision(other_particle)


    def draw(self):
        for particle in self.particles:
            particle.draw(self.screen)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            elif event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

    def run(self):
        running = True
        spawn_delay = 0.1
        while running:
            dt = self.clock.tick() / 1000.0 # Convert to seconds
            self.fps = self.clock.get_fps()

            pygame.display.set_caption(f"FPS: {self.fps:.2f}, Particles: {len(self.particles)}")

            self.handle_events()
            # Add force if space is pressed
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:
                for particle in self.particles:
                    particle.accelerate(Vector2(0, -2000))


            spawn_delay -= dt
            particles_limit = 100
            if spawn_delay < 0 and len(self.particles) < particles_limit:
                spawn_particle = Particle((random.randint(0, width), random.randint(0, height)), 10, Helper.get_color(len(self.particles)))
                self.add_particles([spawn_particle])
                spawn_delay = 0.1


            self.update(dt)

            self.screen.fill((0, 0, 0))
            self.draw()

            pygame.display.flip()


    

if __name__ == "__main__":
    sim = Simulation(width, height, num_threads)
    spawn_particle = Particle((width/2, height-5), 10, (255, 255, 255))
    sim.add_particles([spawn_particle])
    sim.run()
