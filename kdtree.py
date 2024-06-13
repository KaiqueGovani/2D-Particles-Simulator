class KDTree:
    def __init__(self, particles, depth=0):
        if not particles:
            self.axis = 0
            self.particle = None
            self.left = None
            self.right = None
            return

        k = 2  # Dimensionalidade é 2 (para x e y)
        self.axis = depth % k
        particles.sort(key=lambda particle: particle.pos[self.axis])
        median = len(particles) // 2

        self.particle = particles[median]
        self.left = KDTree(particles[:median], depth + 1)
        self.right = KDTree(particles[median + 1:], depth + 1)

    def insert(self, particle, depth=0):
        if self.particle is None:
            self.axis = depth % 2
            self.particle = particle
            self.left = KDTree([], depth + 1)
            self.right = KDTree([], depth + 1)
            return

        axis = depth % 2
        if particle.pos[axis] < self.particle.pos[axis]:
            self.left.insert(particle, depth + 1)
        else:
            self.right.insert(particle, depth + 1)

    def query(self, point, radius, found=None, depth=0):
        if found is None:
            found = []

        if self.particle is None:
            return found

        if self.particle.pos.distance_to(point) <= radius:
            found.append(self.particle)

        axis = depth % 2
        if point[axis] - radius <= self.particle.pos[axis]:
            self.left.query(point, radius, found, depth + 1)
        if point[axis] + radius >= self.particle.pos[axis]:
            self.right.query(point, radius, found, depth + 1)

        return found
