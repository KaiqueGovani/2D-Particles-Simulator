from pygame.math import Vector2

class Particle:
    def __init__(self, pos, radius, color, width, height, mass=1):
        self.pos = Vector2(pos)
        self.prev_pos = Vector2(pos)
        self.radius = radius
        self.color = color
        self.mass = mass
        self.acceleration = Vector2(0, 0)
        self.width = width
        self.height = height

    def accelerate(self, force):
        self.acceleration += force / self.mass
        
    def apply_gravity(self):
        self.accelerate(Vector2(0, 9.81) * self.mass)
        
    def add_velocity(self, velocity):
        self.prev_pos -= velocity
        
    def update(self, dt):
        # Calculate velocity
        velocity = self.pos - self.prev_pos
        # Store previous position
        self.prev_pos = self.pos
        # Perform Verlet integration
        self.pos = self.pos + velocity + (self.acceleration - velocity * 40) * (dt * dt)
        # Reset acceleration
        self.acceleration *= 0

        # Check bounds
        self.check_bounds()

    def check_bounds(self):
        margin = 2
        if self.pos.x < self.radius + margin:
            self.pos.x = self.radius + margin

        elif self.pos.x + self.radius > self.width - margin:
            self.pos.x = self.width - self.radius - margin

        if self.pos.y < self.radius + margin:
            self.pos.y = self.radius + margin

        elif self.pos.y + self.radius > self.height - margin:
            self.pos.y = self.height - self.radius - margin
        