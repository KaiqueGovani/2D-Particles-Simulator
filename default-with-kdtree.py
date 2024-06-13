import pygame
from pygame import Vector2
from collections import defaultdict
from Particle import Particle
from Helper import Helper
from kdtree import KDTree

# Constants
num_threads = 1
width, height = 900, 900
grid_size = 30
gravity = Vector2(0, 9.81)

class Simulation:
    def __init__(self, width, height, threads=1):
        # Initialize Pygame
        pygame.init()
        self.width = width
        self.height = height
        self.particles = []
        self.grid = defaultdict(list)
        self.grid_size = grid_size
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        self.thread_count = threads
        self.elapsed_time = 0

    def add_particle(self, particle):
        self.particles.append(particle)

    def solve_collisions(self):
        kdtree = KDTree(self.particles)
        collision_pairs = []
        
        for particle in self.particles:
            nearby_particles = kdtree.query(particle.pos, particle.radius * 2)
            for other in nearby_particles:
                if other != particle:
                    collision_pairs.append((particle, other))

        # Usando uma pilha para resolver as colisões
        collision_stack = collision_pairs[:]
        while collision_stack:
            p1, p2 = collision_stack.pop()
            self.resolve_collision(p1, p2)

    def resolve_collision(self, p1: Particle, p2: Particle):
        if p1 is p2:
            return

        distance = p1.pos.distance_to(p2.pos)
        if distance < p1.radius + p2.radius:
            distance_vec = p1.pos - p2.pos
            if not distance_vec.length() == 0:
                half_overlap = (0.5 * (distance - p1.radius - p2.radius)) * distance_vec.normalize()
                p1.pos -= half_overlap
                p2.pos += half_overlap

    def update(self, dt):        
        substeps = 3
        sub_dt = dt / substeps
        for _ in range(substeps):
            self.solve_collisions()
            self.update_particles(sub_dt)
            # Add force if space is pressed
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:
                for particle in self.particles:
                    particle.accelerate(Vector2(0, -2000))

    def update_particles(self, dt):
        for particle in self.particles:
            particle.accelerate(gravity * 100)
            particle.update(dt)

    def draw(self):
        for particle in self.particles:
            pygame.draw.circle(self.screen, particle.color, (int(particle.pos.x), int(particle.pos.y)), particle.radius)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
            elif event.type == pygame.QUIT:
                pygame.quit()

    def run(self):
        running = True
        spawn = True
        while running:
            dt = self.clock.tick(80) / 1000  # Convert to seconds
            self.fps = self.clock.get_fps()
            pygame.display.set_caption(f"FPS: {self.fps:.2f}, Particles: {len(self.particles)}, Threads: {self.thread_count} FrameTime: {dt:.5f}")

            self.handle_events()

            spawn_delay = 0.05
            self.elapsed_time += dt
            if self.elapsed_time >= spawn_delay and self.fps > 60 and spawn:
                spawn_particle = Particle((20, 20), 10, Helper.get_color(len(self.particles)), width, height)
                spawn_particle2 = Particle((20, 40), 10, Helper.get_color(len(self.particles)), width, height)
                spawn_particle3 = Particle((20, 60), 10, Helper.get_color(len(self.particles)), width, height)
                self.add_particle(spawn_particle)
                self.add_particle(spawn_particle2)
                self.add_particle(spawn_particle3)
                spawn_particle.add_velocity(Vector2(4, 0))
                spawn_particle2.add_velocity(Vector2(4, 0))
                spawn_particle3.add_velocity(Vector2(4, 0))
                self.elapsed_time -= spawn_delay
            elif self.fps < 60 and dt > 0.016:
                spawn = False

            self.update(dt)

            self.screen.fill((0, 0, 0))
            self.draw()

            pygame.display.flip()

if __name__ == "__main__":
    sim = Simulation(width, height, num_threads)
    sim.run()
