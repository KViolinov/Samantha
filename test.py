import io
import re
import math
import pygame
import random
import threading
from OpenGL.GL import *
from OpenGL.GLU import *
import speech_recognition as sr
from elevenlabs import ElevenLabs, play
import os
import google.generativeai as genai

# from jarvis_functions.gemini_vision_method import *
# from jarvis_functions.call_phone_method import *
# from jarvis_functions.whatsapp_messaging_method import *
# from jarvis_functions.ocr_model_method import *
# from jarvis_functions.shazam_method import *
# from api_keys.api_keys import ELEVEN_LABS_API, GEMINI_KEY, SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET

# Samantha Geometry and Utility Classes
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

class Point3D:
    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z

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

class Vector3D:
    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z

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

class Material:
    def __init__(self, color=(1.0, 1.0, 1.0), opacity=1.0, transparent=False):
        self.color = color
        self.opacity = opacity
        self.transparent = transparent

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

# Jarvis Interface with Samantha UI
class JarvisInterface:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.client = ElevenLabs(api_key="sk_0dfe95fad3b8b17af02ce8d21ecf0fb1c5c63e97b2688707")
        self.r = sr.Recognizer()

        # Gemini Setup
        os.environ["GEMINI_API_KEY"] = "AIzaSyBzMQutGJnduWwKcTrmvAvP_QiTj8zaJ3I"
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])
        self.model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        system_instruction = (
            "Вие сте Джарвис, полезен и информативен AI асистент. "
            "Винаги отговаряйте професионално и кратко, но също се дръж приятелски. "
            "Поддържайте отговорите кратки, но информативни. "
            "Осигурете, че всички отговори са фактологически точни и лесни за разбиране. "
            "При представяне на информацията, да се има на предвид и да се адаптира за дете или тинейджър със сериозни зрителни проблеми"
        )
        self.chat = self.model.start_chat(history=[{"role": "user", "parts": [system_instruction]}])

        # Screen Setup
        self.WIDTH, self.HEIGHT = 1920, 1080
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT), pygame.RESIZABLE | pygame.OPENGL | pygame.DOUBLEBUF)
        pygame.display.set_caption("Jarvis Interface")

        # Colors
        self.WHITE = (255, 255, 255)
        self.CYAN = (0, 255, 255)

        # Fonts
        self.font_large = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 32)

        # Clock
        self.clock = pygame.time.Clock()

        # Samantha Scene Setup
        self.length = 30
        self.radius = 5.6
        self.rotatevalue = 0.035
        self.acceleration = 0
        self.animatestep = 0
        self.toend = False
        self.pi2 = math.pi * 2
        self.group = Group()
        self.setup_scene()

        # Jarvis State Variables
        self.state = "idle"  # idle, listening, processing, responding
        self.running = True
        self.jarvis_voice = "Brian"
        self.status_list = []
        self.jarvis_responses = [
            "Тук съм, как мога да помогна?",
            "Слушам, как мога да Ви асистирам?",
            "Тук съм, как мога да помогна?",
            "С какво мога да Ви бъда полезен?",
            "Слушам шефе, как да помогна?"
        ]

    def setup_scene(self):
        curve = CustomCurve(self.length, self.radius)
        tube_geometry = TubeGeometry(curve, 200, 1.1, 8, True)
        tube_material = Material(color=(1.0, 1.0, 1.0))
        self.mesh = Mesh(tube_geometry, tube_material)
        self.group.add(self.mesh)

        ringcover_geometry = PlaneGeometry(50, 15)
        ringcover_material = Material(color=(0.82, 0.41, 0.31), opacity=0, transparent=True)
        self.ringcover = Mesh(ringcover_geometry, ringcover_material)
        self.ringcover.position.x = self.length + 1
        self.ringcover.rotation_y = math.pi / 2
        self.group.add(self.ringcover)

        ring_geometry = RingGeometry(4.3, 5.55, 32)
        ring_material = Material(color=(1.0, 1.0, 1.0), opacity=0, transparent=True)
        self.ring = Mesh(ring_geometry, ring_material)
        self.ring.position.x = self.length + 1.1
        self.ring.rotation_y = math.pi / 2
        self.group.add(self.ring)

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
        gluPerspective(65, width / height if height != 0 else 1, 1, 10000)
        glMatrixMode(GL_MODELVIEW)

    def easing(self, t, b, c, d):
        t_div = t / (d / 2)
        if t_div < 1:
            return c / 2 * t_div * t_div + b
        t_div = t_div - 2
        return c / 2 * (t_div * t_div * t_div + 2) + b

    def draw_text(self, surface, text, position, font, color):
        text_surface = font.render(text, True, color)
        surface.blit(text_surface, position)

    def update_status(self, new_status):
        self.status_list.append(new_status)
        if len(self.status_list) > 5:
            self.status_list.pop(0)

    def record_text(self):
        try:
            with sr.Microphone() as source:
                self.r.adjust_for_ambient_noise(source, duration=0.2)
                audio = self.r.listen(source)
                MyText = self.r.recognize_google(audio, language="bg-BG")
                print(f"You said: {MyText}")
                return MyText.lower()
        except sr.RequestError as e:
            print(f"API Request Error: {e}")
            return None
        except sr.UnknownValueError:
            print("Sorry, I didn't catch that. Please try again.")
            return None

    def chatbot(self):
        print("Welcome to Vision! Say 'Джарвис' to activate. Say 'излез' to quit.")
        while self.running:
            if self.state == "idle":
                self.state = "listening"
                user_input = self.record_text()
                if user_input and ("джарвис" in user_input or "джарви" in user_input or "джервис" in user_input):
                    self.state = "responding"
                    #pygame.mixer.music.load("sound_files/beep.flac")
                    #pygame.mixer.music.play()
                    print("✅ Wake word detected!")
                    response = random.choice(self.jarvis_responses)
                    audio = self.client.generate(text=response, voice=self.jarvis_voice)
                    play(audio)
                    self.update_status("Jarvis activated")
                elif user_input == "излез":
                    print("Goodbye!")
                    audio = self.client.generate(text="Goodbye!", voice=self.jarvis_voice)
                    play(audio)
                    self.running = False
                    break
                else:
                    self.state = "idle"
            elif self.state == "responding":
                self.state = "listening"
                user_input = self.record_text()
                if user_input:
                    self.state = "processing"
                    print(f"Processing: {user_input}")
                    result = self.chat.send_message({"parts": [user_input]})
                    response_text = result.text
                    print(f"Jarvis: {response_text}")
                    self.update_status(f"Jarvis: {response_text[:50]}...")
                    self.state = "responding"
                    audio = self.client.generate(text=response_text, voice=self.jarvis_voice)
                    play(audio)
                    self.state = "idle"
                else:
                    self.state = "idle"

    def render(self):
        # Update animation based on state
        if self.state in ["processing", "responding"]:
            self.toend = True
            self.animatestep = min(240, self.animatestep + 1)
        else:
            self.toend = False
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

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glTranslatef(0, 0, -110)
        self.group.render()

    def run(self):
        self.initializeGL()
        self.resizeGL(self.WIDTH, self.HEIGHT)

        chatbot_thread = threading.Thread(target=self.chatbot)
        chatbot_thread.start()

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.VIDEORESIZE:
                    self.WIDTH, self.HEIGHT = event.size
                    self.resizeGL(self.WIDTH, self.HEIGHT)

            self.render()

            glMatrixMode(GL_PROJECTION)
            glPushMatrix()
            glLoadIdentity()
            glOrtho(0, self.WIDTH, 0, self.HEIGHT, -1, 1)
            glMatrixMode(GL_MODELVIEW)
            glPushMatrix()
            glLoadIdentity()
            glDisable(GL_DEPTH_TEST)

            self.draw_text(self.screen, "Vision Interface", (10, 10), self.font_large, self.WHITE)
            self.draw_text(self.screen, f"System Status: {self.state.capitalize()}", (10, 60), self.font_small, self.CYAN)
            for index, status in enumerate(self.status_list):
                self.draw_text(self.screen, status, (10, 90 + index * 30), self.font_small, self.WHITE)

            glEnable(GL_DEPTH_TEST)
            glMatrixMode(GL_PROJECTION)
            glPopMatrix()
            glMatrixMode(GL_MODELVIEW)
            glPopMatrix()

            pygame.display.flip()
            self.clock.tick(60)
            self.mesh.rotation_x += self.rotatevalue + self.acceleration

        pygame.quit()

if __name__ == "__main__":
    app = JarvisInterface()
    app.run()