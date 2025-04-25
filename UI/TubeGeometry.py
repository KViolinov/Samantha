from OpenGL.GL import *
import math

class TubeGeometry:
    def __init__(self, curve, segments, radius, radial_segments, closed):
        self.curve = curve
        self.segments = segments
        self.radius = radius
        self.radial_segments = radial_segments
        self.closed = closed
        self.vertices = []
        self.generate()

    def generate(self):
        self.vertices = []
        for i in range(self.segments + 1):
            t = i / self.segments
            if self.closed and i == self.segments:
                t = 0

            center_point = self.curve.get_point(t)

            for j in range(self.radial_segments):
                angle = j * 2 * math.pi / self.radial_segments

                dx = self.radius * math.cos(angle)
                dy = self.radius * math.sin(angle)

                self.vertices.append((
                    center_point.x + dx,
                    center_point.y + dy,
                    center_point.z
                ))

    def render(self):
        glBegin(GL_TRIANGLES)

        for i in range(self.segments):
            for j in range(self.radial_segments):
                idx1 = i * self.radial_segments + j
                idx2 = i * self.radial_segments + (j + 1) % self.radial_segments
                idx3 = (i + 1) * self.radial_segments + j
                idx4 = (i + 1) * self.radial_segments + (j + 1) % self.radial_segments

                glVertex3f(*self.vertices[idx1])
                glVertex3f(*self.vertices[idx2])
                glVertex3f(*self.vertices[idx3])

                glVertex3f(*self.vertices[idx2])
                glVertex3f(*self.vertices[idx4])
                glVertex3f(*self.vertices[idx3])

        glEnd()