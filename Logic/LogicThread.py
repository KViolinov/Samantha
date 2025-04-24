from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from elevenlabs.client import ElevenLabs
import speech_recognition as sr
import pygame
import io
import os
import random

class LogicThread(QThread):
    update_signal = pyqtSignal(str)
    trigger_algorithm = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.running = True
        self.is_playing = False
        self.wake_word_detected = False
        self.model_answering = False
        pygame.mixer.init()
        api_key = "sk_0dfe95fad3b8b17af02ce8d21ecf0fb1c5c63e97b2688707"
        self.client = ElevenLabs(api_key=api_key)
        self.recognizer = sr.Recognizer()
        self.jarvis_responses = [
            "Hello, I'm Samantha, ready to assist!",
            "Samantha online, what's up?",
            "Hey there, Samantha at your service!"
        ]
        self.current_model = "Jarvis"
        self.trigger_algorithm.connect(self.run_algorithm_slot)

    def run(self):
        while self.running:
            if not self.wake_word_detected and not self.is_playing:
                result = self.record_text()
                if result:
                    self.process_speech(result)
            self.msleep(100)

    def record_text(self):
        """Listen for speech and return the recognized text."""
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.2)
                audio = self.recognizer.listen(source)
                text = self.recognizer.recognize_google(audio, language="bg-BG")
                self.update_signal.emit(f"You said: {text}")
                return text.lower()
        except sr.RequestError as e:
            self.update_signal.emit(f"API Request Error: {e}")
            return None
        except sr.UnknownValueError:
            self.update_signal.emit("Sorry, I didn't catch that. Please try again.")
            return None

    def process_speech(self, user_input):
        """Process recognized speech for wake words or commands."""
        if not user_input:
            return

        # Check for wake words
        wake_words = ["Саманта", "саманта", "джервис", "jarvis", "черви"]
        if any(wake_word in user_input for wake_word in wake_words):
            self.wake_word_detected = True
            self.model_answering = True

            self.play_samantha_response()

        # Check for exit command
        elif user_input == "exit":
            self.update_signal.emit("Exiting chatbot")
            self.stop()

    def play_samantha_response(self):
        if self.is_playing:
            self.update_signal.emit("Audio already playing")
            return

        try:
            self.is_playing = True
            response = random.choice(self.jarvis_responses)
            audio_generator = self.client.generate(
                text=response,
                voice="Samantha",  # Changed to Brian as per old project
                stream=False
            )
            audio_bytes = b"".join(audio_generator) if hasattr(audio_generator, '__iter__') else audio_generator
            audio_stream = io.BytesIO(audio_bytes)
            sound = pygame.mixer.Sound(audio_stream)
            sound.play()
            QTimer.singleShot(3000, self.reset_playing)  # Adjust duration based on response length
            self.update_signal.emit("Jarvis response played")
        except Exception as e:
            self.update_signal.emit(f"Audio playback failed: {str(e)}")
            self.is_playing = False
        finally:
            self.wake_word_detected = False
            self.model_answering = False

    def run_algorithm(self):
        """Placeholder for manual algorithm trigger (if needed)."""
        return self.play_samantha_response()

    def run_algorithm_slot(self):
        result = self.run_algorithm()
        self.update_signal.emit(result)

    def reset_playing(self):
        self.is_playing = False
        self.wake_word_detected = False
        self.model_answering = False

    def stop(self):
        self.running = False
        pygame.mixer.quit()
        self.quit()
        self.wait()