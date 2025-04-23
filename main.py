# import sys
# import math
# import time
#
# import numpy as np
# from PyQt5.QtCore import Qt, QTimer
# from PyQt5.QtWidgets import QApplication, QMainWindow, QOpenGLWidget
# from PyQt5.QtGui import QColor, QSurfaceFormat
# from OpenGL.GL import *
# from OpenGL.GLU import *
# from PyQt5.QtCore import QThread, pyqtSignal
#
# class Point3D:
#     def __init__(self, x=0, y=0, z=0):
#         self.x = x
#         self.y = y
#         self.z = z
#
#
# class Vector3D:
#     def __init__(self, x=0, y=0, z=0):
#         self.x = x
#         self.y = y
#         self.z = z
#
#
# class CustomCurve:
#     def __init__(self, length, radius):
#         self.length = length
#         self.radius = radius
#         self.pi2 = math.pi * 2
#
#     def get_point(self, t):
#         x = self.length * math.sin(self.pi2 * t)
#         y = self.radius * math.cos(self.pi2 * 3 * t)
#
#         t_val = t % 0.25 / 0.25
#         t_val = t % 0.25 - (2 * (1 - t_val) * t_val * -0.0185 + t_val * t_val * 0.25)
#
#         if math.floor(t / 0.25) == 0 or math.floor(t / 0.25) == 2:
#             t_val *= -1
#
#         z = self.radius * math.sin(self.pi2 * 2 * (t - t_val))
#
#         return Point3D(x, y, z)
#
#
# class Group:
#     def __init__(self):
#         self.rotation_y = 0
#         self.position_z = 0
#         self.position_x = 0  # Added position_x
#         self.children = []
#
#     def add(self, obj):
#         self.children.append(obj)
#
#     def render(self):
#         glPushMatrix()
#         glTranslatef(self.position_x, 0, self.position_z)  # Added position_x
#         glRotatef(self.rotation_y * 180 / math.pi, 0, 1, 0)
#
#         for child in self.children:
#             child.render()
#
#         glPopMatrix()
#
#
# class Mesh:
#     def __init__(self, geometry, material):
#         self.geometry = geometry
#         self.material = material
#         self.rotation_x = 0
#         self.rotation_y = 0
#         self.position = Point3D(0, 0, 0)
#         self.scale = Point3D(1, 1, 1)
#
#     def render(self):
#         glPushMatrix()
#         glTranslatef(self.position.x, self.position.y, self.position.z)
#         glRotatef(self.rotation_x * 180 / math.pi, 1, 0, 0)
#         glRotatef(self.rotation_y * 180 / math.pi, 0, 1, 0)
#         glScalef(self.scale.x, self.scale.y, self.scale.z)
#
#         color = self.material.color
#         glColor4f(color[0], color[1], color[2], self.material.opacity)
#
#         self.geometry.render()
#
#         glPopMatrix()
#
#
# class TubeGeometry:
#     def __init__(self, curve, segments, radius, radial_segments, closed):
#         self.curve = curve
#         self.segments = segments
#         self.radius = radius
#         self.radial_segments = radial_segments
#         self.closed = closed
#         self.vertices = []
#         self.generate()
#
#     def generate(self):
#         self.vertices = []
#         for i in range(self.segments + 1):
#             t = i / self.segments
#             if self.closed and i == self.segments:
#                 t = 0
#
#             center_point = self.curve.get_point(t)
#
#             for j in range(self.radial_segments):
#                 angle = j * 2 * math.pi / self.radial_segments
#
#                 # Simple approximation of the tube - in real implementation
#                 # we would compute a proper Frenet frame
#                 dx = self.radius * math.cos(angle)
#                 dy = self.radius * math.sin(angle)
#
#                 # Add vertex
#                 self.vertices.append((
#                     center_point.x + dx,
#                     center_point.y + dy,
#                     center_point.z
#                 ))
#
#     def render(self):
#         glBegin(GL_TRIANGLES)
#
#         for i in range(self.segments):
#             for j in range(self.radial_segments):
#                 idx1 = i * self.radial_segments + j
#                 idx2 = i * self.radial_segments + (j + 1) % self.radial_segments
#                 idx3 = (i + 1) * self.radial_segments + j
#                 idx4 = (i + 1) * self.radial_segments + (j + 1) % self.radial_segments
#
#                 # Triangle 1
#                 glVertex3f(*self.vertices[idx1])
#                 glVertex3f(*self.vertices[idx2])
#                 glVertex3f(*self.vertices[idx3])
#
#                 # Triangle 2
#                 glVertex3f(*self.vertices[idx2])
#                 glVertex3f(*self.vertices[idx4])
#                 glVertex3f(*self.vertices[idx3])
#
#         glEnd()
#

# class PlaneGeometry:
#     def __init__(self, width, height):
#         self.width = width
#         self.height = height
#
#     def render(self):
#         half_width = self.width / 2
#         half_height = self.height / 2
#
#         glBegin(GL_QUADS)
#         glVertex3f(-half_width, -half_height, 0)
#         glVertex3f(half_width, -half_height, 0)
#         glVertex3f(half_width, half_height, 0)
#         glVertex3f(-half_width, half_height, 0)
#         glEnd()
#
#
# class RingGeometry:
#     def __init__(self, inner_radius, outer_radius, segments):
#         self.inner_radius = inner_radius
#         self.outer_radius = outer_radius
#         self.segments = segments
#
#     def render(self):
#         glBegin(GL_QUADS)
#
#         for i in range(self.segments):
#             angle1 = i * 2 * math.pi / self.segments
#             angle2 = (i + 1) * 2 * math.pi / self.segments
#
#             cos1, sin1 = math.cos(angle1), math.sin(angle1)
#             cos2, sin2 = math.cos(angle2), math.sin(angle2)
#
#             # Inner radius vertices
#             glVertex3f(self.inner_radius * cos1, self.inner_radius * sin1, 0)
#             glVertex3f(self.inner_radius * cos2, self.inner_radius * sin2, 0)
#
#             # Outer radius vertices
#             glVertex3f(self.outer_radius * cos2, self.outer_radius * sin2, 0)
#             glVertex3f(self.outer_radius * cos1, self.outer_radius * sin1, 0)
#
#         glEnd()
#
#
# class Material:
#     def __init__(self, color=(1.0, 1.0, 1.0), opacity=1.0, transparent=False):
#         self.color = color
#         self.opacity = opacity
#         self.transparent = transparent
#
#
# class LogicThread(QThread):
#     update_signal = pyqtSignal(str)  # Signal to communicate with GUI
#
#     def __init__(self):
#         super().__init__()
#         self.running = True
#
#     def run(self):
#         while self.running:
#             # 🔽 🔽 🔽 PUT YOUR ALGORITHM HERE 🔽 🔽 🔽
#             # Example 1: Simulate AI Logic
#             result = self.run_algorithm()
#
#             # Example 2: Send result to GUI (optional)
#             self.update_signal.emit(result)
#
#             # Optional: pause for a bit (so you don't overload CPU)
#             time.sleep(1)
#
#     def run_algorithm(self):
#         # 👉 THIS IS WHERE YOUR ALGORITHM LOGIC GOES 👈
#         # Replace the code below with your actual Logic
#         # For example, speech recognition, ML model inference, etc.
#
#         print("Running algorithm...")
#         # Simulated result
#         return "Algorithm finished step"
#
#     def stop(self):
#         self.running = False
#
#
# class OpenGLWidget(QOpenGLWidget):
#     def __init__(self, parent=None):
#         super().__init__(parent)
#
#         # Animation parameters
#         self.length = 30
#         self.radius = 5.6
#         self.rotatevalue = 0.035
#         self.acceleration = 0
#         self.animatestep = 0
#         self.toend = False
#         self.pi2 = math.pi * 2
#
#         # Scene setup
#         self.group = Group()
#         self.setup_scene()
#
#         # Animation timer
#         self.timer = QTimer(self)
#         self.timer.timeout.connect(self.animate)
#         self.timer.start(16)  # ~60 FPS
#
#     def setup_scene(self):
#         # Create tube mesh
#         curve = CustomCurve(self.length, self.radius)
#         tube_geometry = TubeGeometry(curve, 200, 1.1, 8, True)
#         tube_material = Material(color=(1.0, 1.0, 1.0))
#         self.mesh = Mesh(tube_geometry, tube_material)
#         self.group.add(self.mesh)
#
#         # Create ringcover
#         ringcover_geometry = PlaneGeometry(50, 15)
#         ringcover_material = Material(color=(0.82, 0.41, 0.31), opacity=0, transparent=True)
#         self.ringcover = Mesh(ringcover_geometry, ringcover_material)
#         self.ringcover.position.x = self.length + 1
#         self.ringcover.rotation_y = math.pi / 2
#         self.group.add(self.ringcover)
#
#         # Create ring
#         ring_geometry = RingGeometry(4.3, 5.55, 32)
#         ring_material = Material(color=(1.0, 1.0, 1.0), opacity=0, transparent=True)
#         self.ring = Mesh(ring_geometry, ring_material)
#         self.ring.position.x = self.length + 1.1
#         self.ring.rotation_y = math.pi / 2
#         self.group.add(self.ring)
#
#         # Create fake shadows
#         for i in range(10):
#             plain_geometry = PlaneGeometry(self.length * 2 + 1, self.radius * 3)
#             plain_material = Material(color=(0.82, 0.41, 0.31), opacity=0.13, transparent=True)
#             plain = Mesh(plain_geometry, plain_material)
#             plain.position.z = -2.5 + i * 0.5
#             self.group.add(plain)
#
#     def initializeGL(self):
#         glClearColor(0.82, 0.41, 0.31, 1.0)  # #d1684e
#         glEnable(GL_DEPTH_TEST)
#         glEnable(GL_BLEND)
#         glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
#
#     def resizeGL(self, width, height):
#         glViewport(0, 0, width, height)
#         glMatrixMode(GL_PROJECTION)
#         glLoadIdentity()
#         gluPerspective(65, width / height, 1, 10000)
#         glMatrixMode(GL_MODELVIEW)
#
#     def paintGL(self):
#         glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
#         glLoadIdentity()
#         glTranslatef(0, 0, -110)  # Camera position
#
#         self.render()
#
#     def render(self):
#         # Update animation parameters
#         if self.toend:
#             self.animatestep = min(240, self.animatestep + 1)
#         else:
#             self.animatestep = max(0, self.animatestep - 4)
#
#         self.acceleration = self.easing(self.animatestep, 0, 1, 240)
#
#         if self.acceleration > 0.35:
#             progress = (self.acceleration - 0.35) / 0.65
#             self.group.rotation_y = -math.pi / 2 * progress
#             self.group.position_z = 50 * progress
#
#             self.group.position_x = 0
#
#             progress = max(0, (self.acceleration - 0.97) / 0.03)
#             self.mesh.material.opacity = 1 - progress
#             self.ringcover.material.opacity = progress
#             self.ring.material.opacity = progress
#             self.ring.scale.x = self.ring.scale.y = 0.9 + 0.1 * progress
#         else:
#             self.group.position_x = 0
#
#         self.group.render()
#
#     def animate(self):
#         self.mesh.rotation_x += self.rotatevalue + self.acceleration
#         self.update()
#
#     def easing(self, t, b, c, d):
#         # Fixed version of the easing function
#         t_div = t / (d / 2)
#         if t_div < 1:
#             return c / 2 * t_div * t_div + b
#         t_div = t_div - 2
#         return c / 2 * (t_div * t_div * t_div + 2) + b
#
#     # def mousePressEvent(self, event):
#     #     self.toend = True
#     #
#     # def mouseReleaseEvent(self, event):
#     #     self.toend = False
#
#     def active(self):
#         self.toend = True
#
#     def chill(self):
#         self.toend = False
#
# class MainWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("OS-1 - Samantha")
#         self.setStyleSheet("background-color: #d1684e;")
#
#         self.toend = False  # Manage toend here
#
#         format = QSurfaceFormat()
#         format.setDepthBufferSize(24)
#         format.setSamples(4)
#         QSurfaceFormat.setDefaultFormat(format)
#
#         self.opengl_widget = OpenGLWidget(self)
#         self.setCentralWidget(self.opengl_widget)
#
#         self.resize(500, 500)
#         self.setMinimumSize(500, 500)
#
#         # Trigger animation sequence
#         self.opengl_widget.active()
#         QTimer.singleShot(3000, self.opengl_widget.chill)
#     def keyPressEvent(self, event):
#         if event.key() == Qt.Key_Space:
#             self.opengl_widget.active()
#         elif event.key() == Qt.Key_R:
#             self.opengl_widget.chill()
#
#
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = MainWindow()
#     window.show()
#
#     sys.exit(app.exec_())

from UI.MainWindow import MainWindow
from PyQt5.QtWidgets import QApplication
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


#test
#test