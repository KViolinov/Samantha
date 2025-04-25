from OpenGL.GL import *
import math

class RingGeometry:
    def __init__(self, inner_radius, outer_radius, segments):
        self.inner_radius = inner_radius
        self.outer_radius = outer_radius
        self.segments = segments

    def render(self):
        glBegin(GL_QUADS)

        for i in range(self.segments):
            angle1 = i * 2 * math.pi / self.segments
            angle2 = (i + 1) * 2 * math.pi / self.segments

            cos1, sin1 = math.cos(angle1), math.sin(angle1)
            cos2, sin2 = math.cos(angle2), math.sin(angle2)

            glVertex3f(self.inner_radius * cos1, self.inner_radius * sin1, 0)
            glVertex3f(self.inner_radius * cos2, self.inner_radius * sin2, 0)
            glVertex3f(self.outer_radius * cos2, self.outer_radius * sin2, 0)
            glVertex3f(self.outer_radius * cos1, self.outer_radius * sin1, 0)

        glEnd()