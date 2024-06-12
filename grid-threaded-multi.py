import time
from collections import defaultdict
from Particle import Particle
from Helper import Helper
import multiprocessing

# Constants
num_threads = 8
width, height = 960, 960
grid_size = 30  # width and height // grid_size // 2 * num_threads should be an integer

def add_particle(particles, particle):
    particles.append(particle)

def update_grid(grid, particles, thread_count):
    grid.clear()
    for particle in particles:
        cell_x = int(particle.pos.x // grid_size)
        cell_y = int(particle.pos.y // grid_size)
        grid[(cell_x, cell_y)].append(particle)
        

def get_neighbors(cell_x, cell_y, grid):
    neighbors = []
    for dx in range(-1, 2):
        for dy in range(-1, 2):
            neighbors.extend(grid[(cell_x + dx, cell_y + dy)])
    return neighbors

def solve_collisions(grid, thread_count):
    processes = []
    slices_count = thread_count * 2
    slice_cells = width // grid_size // slices_count

    # Process half of the grid in parallel
    for i in range(thread_count):
        start_cell = (2 * i * slice_cells, 0)
        end_cell = (start_cell[0] + slice_cells, height // grid_size)
        process = multiprocessing.Process(target=solve_collisions_process, args=(start_cell, end_cell, grid))
        process.start()
        processes.append(process)

    for process in processes:
        process.join()

    # Process the other half of the grid in parallel
    for i in range(thread_count):
        start_cell = ((2 * i + 1) * slice_cells, 0)
        end_cell = (start_cell[0] + slice_cells, height // grid_size)
        process = multiprocessing.Process(target=solve_collisions_process, args=(start_cell, end_cell, grid))
        process.start()
        processes.append(process)

    for process in processes:
        process.join()

def solve_collisions_process(start_cell, end_cell, grid):
    for cell_x in range(start_cell[0], end_cell[0]):
        for cell_y in range(start_cell[1], end_cell[1]):
            solve_collisions_cell(cell_x, cell_y, grid)

def solve_collisions_cell(cell_x, cell_y, grid):
    for particle in grid[(cell_x, cell_y)]:
        neighbors = get_neighbors(cell_x, cell_y, grid)
        for other_particle in neighbors:
            resolve_collision(particle, other_particle)

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

def update(particles, grid, dt, thread_count):
    substeps = 3
    sub_dt = dt / substeps
    for _ in range(substeps):
        update_grid(grid, particles, thread_count)
        # solve_collisions(grid, thread_count)
        update_particles(particles, sub_dt, thread_count)
        # Add force if space is pressed
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            for particle in particles:
                particle.accelerate(Vector2(0, -2000))

def update_particles(particles, dt, thread_count):
    processes = []

    for i in range(thread_count):
        start_index = i * len(particles) // thread_count
        end_index = None if i == thread_count - 1 else (i + 1) * len(particles) // thread_count
        process = multiprocessing.Process(target=update_particles_process, args=(start_index, end_index, particles, dt))
        process.start()
        processes.append(process)

    for process in processes:
        process.join()

def update_particles_process(start_index, end_index, particles, dt):
    for particle in particles[start_index:end_index]:
        particle.apply_gravity()
        particle.update(dt)

def draw(particles, screen):
    for particle in particles:
        pygame.draw.circle(screen, particle.color, (int(particle.pos.x), int(particle.pos.y)), particle.radius)


if __name__ == "__main__":
    import pygame
    from pygame import Vector2
    
    def handle_events():
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()
            elif event.type == pygame.QUIT:
                pygame.quit()
                exit()
    
    
    pygame.init()
    
    # Create a multiprocessing manager
    manager = multiprocessing.Manager()
    grid = defaultdict(list)
    particles = manager.list()
    
    # Variables
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((width, height))
    thread_count = num_threads
    elapsed_time = 0

    spawn = True
    while True:
        dt = clock.tick(80) / 1000  # Convert to seconds
        fps = clock.get_fps()
        pygame.display.set_caption(f"FPS: {fps:.2f}, Particles: {len(particles)}, Threads: {thread_count} FrameTime: {dt:.5f}")

        handle_events()

        spawn_delay = 0.05
        elapsed_time += dt
        if elapsed_time >= spawn_delay and spawn and len(particles) < 1000:
            spawn_particle = Particle(20, 20, 10, Helper.get_color(len(particles)), width, height)
            spawn_particle2 = Particle(20, 40, 10, Helper.get_color(len(particles)), width, height)
            spawn_particle3 = Particle(20, 60, 10, Helper.get_color(len(particles)), width, height)
            add_particle(particles, spawn_particle)
            add_particle(particles, spawn_particle2)
            add_particle(particles, spawn_particle3)
            spawn_particle.add_velocity(Vector2(4, 0))
            spawn_particle2.add_velocity(Vector2(4, 0))
            spawn_particle3.add_velocity(Vector2(4, 0))
            elapsed_time -= spawn_delay

        update(particles, grid, dt, thread_count)

        screen.fill((69, 69, 69))
        draw(particles, screen)

        pygame.display.flip()

    