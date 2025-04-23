from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QOpenGLWidget
from OpenGL.GL import *
from OpenGL.GLU import *
import math
from Logic.CustomCurve import CustomCurve
from Logic.Group import Group
from Logic.Mesh import Mesh
from Logic.Material import Material
from Geometry.TubeGeometry import TubeGeometry
from Geometry.PlaneGeometry import PlaneGeometry
from Geometry.RingGeometry import RingGeometry

class OpenGLWidget(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Animation parameters
        self.length = 30
        self.radius = 5.6
        self.rotatevalue = 0.035
        self.acceleration = 0
        self.animatestep = 0
        self.toend = False
        self.pi2 = math.pi * 2

        # Scene setup
        self.group = Group()
        self.setup_scene()

        # Animation timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(16)  # ~60 FPS

    def setup_scene(self):
        # Create tube mesh
        curve = CustomCurve(self.length, self.radius)
        tube_geometry = TubeGeometry(curve, 200, 1.1, 8, True)
        tube_material = Material(color=(1.0, 1.0, 1.0))
        self.mesh = Mesh(tube_geometry, tube_material)
        self.group.add(self.mesh)

        # Create ringcover
        ringcover_geometry = PlaneGeometry(50, 15)
        ringcover_material = Material(color=(0.82, 0.41, 0.31), opacity=0, transparent=True)
        self.ringcover = Mesh(ringcover_geometry, ringcover_material)
        self.ringcover.position.x = self.length + 1
        self.ringcover.rotation_y = math.pi / 2
        self.group.add(self.ringcover)

        # Create ring
        ring_geometry = RingGeometry(4.3, 5.55, 32)
        ring_material = Material(color=(1.0, 1.0, 1.0), opacity=0, transparent=True)
        self.ring = Mesh(ring_geometry, ring_material)
        self.ring.position.x = self.length + 1.1
        self.ring.rotation_y = math.pi / 2
        self.group.add(self.ring)

        # Create fake shadows
        for i in range(10):
            plain_geometry = PlaneGeometry(self.length * 2 + 1, self.radius * 3)
            plain_material = Material(color=(0.82, 0.41, 0.31), opacity=0.13, transparent=True)
            plain = Mesh(plain_geometry, plain_material)
            plain.position.z = -2.5 + i * 0.5
            self.group.add(plain)

    def initializeGL(self):
        glClearColor(0.82, 0.41, 0.31, 1.0)  # #d1684e
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    def resizeGL(self, width, height):
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(65, width / height, 1, 10000)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glTranslatef(0, 0, -110)  # Camera position

        self.render()

    def render(self):
        # Update animation parameters
        if self.toend:
            self.animatestep = min(240, self.animatestep + 1)
        else:
            self.animatestep = max(0, self.animatestep - 4)

        self.acceleration = self.easing(self.animatestep, 0, 1, 240)

        if self.acceleration > 0.35:
            progress = (self.acceleration - 0.35) / 0.65
            self.group.rotation_y = -math.pi / 2 * progress
            self.group.position_z = 50 * progress

            self.group.position_x = 0

            progress = max(0, (self.acceleration - 0.97) / 0.03)
            self.mesh.material.opacity = 1 - progress
            self.ringcover.material.opacity = progress
            self.ring.material.opacity = progress
            self.ring.scale.x = self.ring.scale.y = 0.9 + 0.1 * progress
        else:
            self.group.position_x = 0

        self.group.render()

    def animate(self):
        self.mesh.rotation_x += self.rotatevalue + self.acceleration
        self.update()

    def easing(self, t, b, c, d):
        # Fixed version of the easing function
        t_div = t / (d / 2)
        if t_div < 1:
            return c / 2 * t_div * t_div + b
        t_div = t_div - 2
        return c / 2 * (t_div * t_div * t_div + 2) + b

    def active(self):
        self.toend = True

    def chill(self):
        self.toend = False