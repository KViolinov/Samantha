from OpenGL.GL import *

class PlaneGeometry:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def render(self):
        half_width = self.width / 2
        half_height = self.height / 2

        glBegin(GL_QUADS)
        glVertex3f(-half_width, -half_height, 0)
        glVertex3f(half_width, -half_height, 0)
        glVertex3f(half_width, half_height, 0)
        glVertex3f(-half_width, half_height, 0)
        glEnd()