import time
import pygame
from pygame import Vector2
from collections import defaultdict
from Particle import Particle
from Helper import Helper
import threading

# Constants
num_threads = 1
width, height = 900, 900
grid_size = 25
gravity = Vector2(0, 9.81)

class Simulation:
    def __init__(self, width, height, threads):
        # Initialize Pygame
        pygame.init()
        self.width = width
        self.height = height
        self.particles = []
        self.grid_size = grid_size
        self.grid = [[] for _ in range(width // grid_size * height // grid_size)]
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        self.thread_count = threads
        self.elapsed_time = 0

    def add_particle(self, particle):
        self.particles.append(particle)

    def update_grid(self):
        self.grid = [[] for _ in range(width // grid_size * height // grid_size)]
        
        threads = []
        process_amount = len(self.particles) // self.thread_count
        for i in range(self.thread_count):
            start_index = i * process_amount
            end_index = (i + 1) * process_amount if i < self.thread_count - 1 else None
            thread = threading.Thread(target=self.update_grid_thread, args=(start_index, end_index))
            thread.start()
            threads.append(thread)
            
        for thread in threads:
            thread.join()
            
    def update_grid_thread(self, start_index, end_index):
        for particle in self.particles[start_index:end_index]:
            cell_x = int(particle.pos.x // self.grid_size)
            cell_y = int(particle.pos.y // self.grid_size)
            self.grid[cell_x + cell_y * self.grid_size].append(particle)

    

    def solve_collisions(self):
        threads = []
        slices_count = self.thread_count * 2
        slice_size = len(self.grid) // slices_count
        
        # process half of the grid in parallel
        for i in range(self.thread_count):
            start = 2 * i * slice_size
            end = start + slice_size
            thread = threading.Thread(target=self.solve_collisions_thread, args=(start, end))
            thread.start()
            threads.append(thread)
        
        for thread in threads:
            thread.join()
        
        # process the other half of the grid in parallel
        for i in range(self.thread_count, slices_count):
            start = (2 * i + 1) * slice_size
            end = start + slice_size
            thread = threading.Thread(target=self.solve_collisions_thread, args=(start, end))
            thread.start()
            threads.append(thread)
            
        for thread in threads:
            thread.join()
        
    def solve_collisions_thread(self, start, end):
        cell_x = start % self.grid_size
        cell_y = start // self.grid_size
        
    def check_cell_collision(self, particle, cell):
        for other_particle in cell:
            self.resolve_collision(particle, other_particle)
   
            
    def update(self, dt):        
        substeps = 3
        sub_dt = dt / substeps
        for _ in range(substeps):
            self.update_grid()
            self.solve_collisions()
            self.update_particles(sub_dt)
            # Add force if space is pressed
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:
                for particle in self.particles:
                    particle.accelerate(Vector2(0, -2000))
        
    def update_particles(self, dt):
        threads = []
        
        for i in range(self.thread_count):
            start_index = i * len(self.particles) // self.thread_count
            end_index = None if i == self.thread_count - 1 else (i + 1) * len(self.particles) // self.thread_count
            thread = threading.Thread(target=self.update_particles_thread, args=(start_index, end_index, dt))
            thread.start()
            threads.append(thread)
        
        for thread in threads:
            thread.join()
            
    def update_particles_thread(self, start_index, end_index, dt):
        for particle in self.particles[start_index:end_index]:
            particle.accelerate(gravity * 100)
            particle.update(dt)
        
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

    def draw(self):
        for particle in self.particles:
            particle.draw(self.screen)

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

            self.screen.fill((69, 69, 69))
            self.draw()

            pygame.display.flip()


    

if __name__ == "__main__":
    sim = Simulation(width, height, num_threads)
    sim.run()
