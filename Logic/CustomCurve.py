import math
from Geometry.Point3D import Point3D

class CustomCurve:
    def __init__(self, length, radius):
        self.length = length
        self.radius = radius
        self.pi2 = math.pi * 2

    def get_point(self, t):
        x = self.length * math.sin(self.pi2 * t)
        y = self.radius * math.cos(self.pi2 * 3 * t)

        t_val = t % 0.25 / 0.25
        t_val = t % 0.25 - (2 * (1 - t_val) * t_val * -0.0185 + t_val * t_val * 0.25)

        if math.floor(t / 0.25) == 0 or math.floor(t / 0.25) == 2:
            t_val *= -1

        z = self.radius * math.sin(self.pi2 * 2 * (t - t_val))

        return Point3D(x, y, z)