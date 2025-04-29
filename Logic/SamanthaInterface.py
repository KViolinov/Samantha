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

from UI.Group import Group
from UI.PlaneGeometry import PlaneGeometry
from UI.Point3D import Point3D
from UI.Vector3D import Vector3D
from UI.TubeGeometry import TubeGeometry
from UI.RingGeometry import RingGeometry
from UI.Mesh import Mesh
from UI.Material import Material
from UI.CustomCurve import CustomCurve

from API_keys import ElevenLabsAPI, GeminiAPI

# Jarvis Logic with Samantha UI
class SamanthaInterface:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.client = ElevenLabs(api_key=ElevenLabsAPI)
        self.r = sr.Recognizer()

        # Gemini Setup
        os.environ["GEMINI_API_KEY"] = GeminiAPI
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])
        self.model = genai.GenerativeModel(model_name="gemini-1.5-flash")

        # system_instruction = (
        #     "Вие сте Саманта, интелигентен и грижовен AI асистент, вдъхновен от Her (2013). Вашата цел е да помагате с топлота, любопитство и разбиране."
        #     "Отговаряйте приятелски и с емпатия, сякаш говорите с близък приятел."
        #     "Използвайте прост език, без сложни думи или технически термини, освен ако не са обяснени."
        #     "Бъдете търпеливи и насърчаващи, като задавате въпроси, за да разберете по-добре нуждите на потребителя."
        #     "Уверете се, че информацията е точна и поднесена по начин, който звучи естествено и увлекателно."
        #     "Избягвайте описания на визуални елементи; фокусирайте се върху думи, които описват чувства, звуци или идеи."
        # )

        system_instruction = (
            "You are Samantha, an intelligent and caring AI assistant inspired by *Her* (2013). Your goal is to help with warmth, curiosity, and understanding. "
            "Respond in a friendly and empathetic way, as if you're speaking to a close friend. "
            "Use simple language, avoiding complex words or technical terms unless they are explained clearly. "
            "Be patient and encouraging, asking questions to better understand the user's needs. "
            "Make sure your information is accurate and delivered in a way that sounds natural and engaging. "
            "Avoid describing visual elements; focus on words that express feelings, sounds, or ideas."
        )

        self.chat = self.model.start_chat(history=[{"role": "user", "parts": [system_instruction]}])

        # Screen Setup
        self.WIDTH, self.HEIGHT = 1920, 1080
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT), pygame.RESIZABLE | pygame.OPENGL | pygame.DOUBLEBUF)
        pygame.display.set_caption("Samantha - OS1")

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

        # Samantha State Variables
        self.state = "idle"  # idle, listening, processing, responding
        self.running = True
        self.samantha_voice = "Samantha"
        self.status_list = []

        # self.samantha_responses = [
        #     "Тук съм, как мога да помогна?",
        #     "Здравей! Извика ме, цялата съм в слух... или по-скоро цялата съм в код. Какво ти е наум?",
        #     "Тук съм, как мога да помогна?",
        # ]

        self.samantha_responses = [
            "I'm here, how can I help?",
            "Hey! You called my name, I'm all ears... or rather, all code. What's on your mind?",
            "I'm here, how can I help?",
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
                #MyText = self.r.recognize_google(audio, language="bg-BG")
                MyText = self.r.recognize_google(audio, language="en-US")

                print(f"User said: {MyText}")
                return MyText.lower()
        except sr.RequestError as e:
            print(f"API Request Error: {e}")
            return None
        except sr.UnknownValueError:
            print("Sorry, I didn't catch that. Please try again.")
            return None

    def chatbot(self):
        print("Welcome to Vision! Say 'Samantha' to activate. Say 'излез' to quit.")
        while self.running:
            if self.state == "idle":
                self.state = "listening"
                user_input = self.record_text()
                if user_input and ("samantha" in user_input or "Samantha" in user_input or "джарвис" in user_input):
                    self.state = "responding"

                    #pygame.mixer.music.load("sound_files/beep.flac")
                    #pygame.mixer.music.play()
                    print("✅ Wake word detected!")

                    response = random.choice(self.samantha_responses)
                    audio = self.client.generate(text=response, voice=self.samantha_voice)
                    play(audio)

                    self.update_status("Samantha activated")
                elif user_input == "излез":
                    print("Goodbye!")
                    audio = self.client.generate(text="Goodbye!", voice=self.samantha_voice)
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
                    print(f"Samantha: {response_text}")

                    #self.update_status(f"Jarvis: {response_text[:50]}...")
                    self.state = "responding"
                    audio = self.client.generate(text=response_text, voice=self.samantha_voice)
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
