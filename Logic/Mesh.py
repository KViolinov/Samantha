from OpenGL.GL import *
from Geometry.Point3D import Point3D
import math

class Mesh:
    def __init__(self, geometry, material):
        self.geometry = geometry
        self.material = material
        self.rotation_x = 0
        self.rotation_y = 0
        self.position = Point3D(0, 0, 0)
        self.scale = Point3D(1, 1, 1)

    def render(self):
        glPushMatrix()
        glTranslatef(self.position.x, self.position.y, self.position.z)
        glRotatef(self.rotation_x * 180 / math.pi, 1, 0, 0)
        glRotatef(self.rotation_y * 180 / math.pi, 0, 1, 0)
        glScalef(self.scale.x, self.scale.y, self.scale.z)

        color = self.material.color
        glColor4f(color[0], color[1], color[2], self.material.opacity)

        self.geometry.render()

        glPopMatrix()