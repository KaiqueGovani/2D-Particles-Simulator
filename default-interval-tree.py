import time
import pygame
from pygame import Vector2
from collections import defaultdict
from Particle import Particle  # Assuming you have a Particle class defined elsewhere
from Helper import Helper  # Assuming you have a Helper class defined elsewhere
import threading

# Constants
num_threads = 1
width, height = 900, 900
grid_size = 30  # Grid size must divide width in half
gravity = Vector2(0, 9.81)

def build_tree(width, grid_size):
    return IntervalTree(width, grid_size)

class NodeTree:
    def __init__(self, start, end):
        self.start = start
        self.end = end
        self.particles = []
        self.left = None 
        self.right = None

class IntervalTree:
    def __init__(self, width, grid_size, screen):
        self.screen = screen
        self.root = self.build(0, width, grid_size)

    def build(self, start, end, grid_size):
        if end - start <= grid_size:
            return NodeTree(start, end)

        mid = (start + end) // 2
        node = NodeTree(start, end)
        node.left = self.build(start, mid, grid_size)
        node.right = self.build(mid, end, grid_size)
        return node
    
    def draw(self, node):
        if node is None:
            return
        pygame.draw.line(self.screen, (255, 255, 255), (node.start, 0), (node.start, height))
        pygame.draw.line(self.screen, (255, 255, 255), (node.end, 0), (node.end, height))
        self.draw(node.left)
        self.draw(node.right)

    def insert_particle(self, node, particle, parent=None):
        if node is None:
            return
        if node.start <= particle.pos.x < node.end:
            # If is leaf node insert particle
            if node.left is None and node.right is None:
                # if particle.pos.x < 225:
                #     particle.color = (255, 0, 0)
                # elif particle.pos.x < 450:
                #     particle.color = (0, 255, 0)
                # elif particle.pos.x < 675:
                #     particle.color = (0, 0, 255)
                # else:
                #     particle.color = (255, 255, 255)
                
                node.particles.append(particle)
            else:
                # Otherwise pass to children
                self.insert_particle(node.left, particle, node)
                self.insert_particle(node.right, particle, node)
            
            

    def query_neighbors(self, node, particle):
        if node is None:
            return []
        neighbors = []

        if node.start <= particle.pos.x < node.end:
            # If is leaf node
            if node.left is None and node.right is None:
                neighbors.extend(node.particles)
                
                # if close to edge, try to get neighbors from next cell using fake particle
                if particle.pos.x - particle.radius < node.start:
                    fake_particle = Particle((node.start - 1, particle.pos.y), 0, (0, 0, 0), 0, 0)
                    neighbors.extend(self.query_neighbors(self.root, fake_particle))
                elif particle.pos.x + particle.radius > node.end:
                    fake_particle = Particle((node.end + 1, particle.pos.y), 0, (0, 0, 0), 0, 0)
                    neighbors.extend(self.query_neighbors(self.root, fake_particle))
                
            else:
                neighbors.extend(self.query_neighbors(node.left, particle))
                neighbors.extend(self.query_neighbors(node.right, particle))
                
        return neighbors

    def clear(self, node):
        if node is None:
            return
        # If is leaf node
        node.particles = []
        self.clear(node.left)
        self.clear(node.right)

class Simulation:
    def __init__(self, width, height, threads=1):
        pygame.init()
        self.width = width
        self.height = height
        self.particles = []
        self.screen = pygame.display.set_mode((width, height))
        self.interval_tree = IntervalTree(width, grid_size, self.screen)
        self.clock = pygame.time.Clock()
        self.thread_count = threads
        self.elapsed_time = 0

    def add_particle(self, particle):
        self.particles.append(particle)

    def update_interval_tree(self):
        self.interval_tree.clear(self.interval_tree.root)
        for particle in self.particles:
            self.interval_tree.insert_particle(self.interval_tree.root, particle)

    def get_neighbors(self, particle):
        return self.interval_tree.query_neighbors(self.interval_tree.root, particle)

    def solve_collisions(self):
        self.update_interval_tree()
        for particle in self.particles:
            neighbors = self.get_neighbors(particle)
            for other_particle in neighbors:
                self.resolve_collision(particle, other_particle)

    def resolve_collision(self, p1, p2):
        if p1 is p2:
            return

        distance = p1.pos.distance_to(p2.pos)
        if distance < p1.radius + p2.radius:
            distance_vec = p1.pos - p2.pos
            if distance_vec.length() != 0:
                half_overlap = (0.5 * (distance - p1.radius - p2.radius)) * distance_vec.normalize()
                p1.pos -= half_overlap
                p2.pos += half_overlap

    def update(self, dt):
        substeps = 2
        sub_dt = dt / substeps
        for _ in range(substeps):
            self.solve_collisions()
            self.update_particles(sub_dt)
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
        self.interval_tree.draw(self.interval_tree.root)

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
            dt = self.clock.tick(80) / 1000
            self.fps = self.clock.get_fps()
            pygame.display.set_caption(f"FPS: {self.fps:.2f}, Particles: {len(self.particles)}, Threads: {self.thread_count} FrameTime: {dt:.5f}")

            self.handle_events()

            spawn_delay = 0.05
            self.elapsed_time += dt
            if self.elapsed_time >= spawn_delay and self.fps > 60 and spawn:
                spawn_particle = Particle((20, 20), 10, Helper.get_color(len(self.particles)), self.width, self.height)
                spawn_particle2 = Particle((20, 40), 10, Helper.get_color(len(self.particles)), self.width, self.height)
                spawn_particle3 = Particle((20, 60), 10, Helper.get_color(len(self.particles)), self.width, self.height)
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
            self.screen.fill((69, 69, 69))
            self.draw()
            pygame.display.flip()

if __name__ == "__main__":
    sim = Simulation(width, height, num_threads)
    sim.run()
