from OpenGL.GL import *
import math

class Group:
    def __init__(self):
        self.rotation_y = 0
        self.position_z = 0
        self.position_x = 0
        self.children = []

    def add(self, obj):
        self.children.append(obj)

    def render(self):
        glPushMatrix()
        glTranslatef(self.position_x, 0, self.position_z)
        glRotatef(self.rotation_y * 180 / math.pi, 0, 1, 0)

        for child in self.children:
            child.render()

        glPopMatrix()