class Helper:
    @classmethod
    def get_color(cls, iteration, step=2):
        factor = (iteration * step) % (256 * 6)
        stage = factor // 256
        r = 255 if stage < 2 else 255 - (factor % 256) if stage < 3 else 0 if stage < 5 else (factor % 256)
        g = 0 if stage < 1 else factor % 256 if stage < 2 else 255 if stage < 4 else 255 - (factor % 256) if stage < 5 else 0
        b = 255 - (factor % 256) if stage < 1 else 0 if stage < 3 else factor % 256 if stage < 4 else 255
        return (r, g, b)
    
    @classmethod
    def create_grid(cls, width, height, grid_size):
        grid = []
        