from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from elevenlabs.client import ElevenLabs
import speech_recognition as sr
import pygame
import io
import os
import google.generativeai as genai

class LogicThread(QThread):
    update_signal = pyqtSignal(str)
    trigger_algorithm = pyqtSignal()
    play_startup_sound_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.running = True
        self.is_playing = False
        self.wake_word_detected = False
        self.listening_for_command = False
        self.model_answering = False
        pygame.mixer.init()

        # ElevenLabs setup
        elevenlabs_api_key = "sk_0dfe95fad3b8b17af02ce8d21ecf0fb1c5c63e97b2688707"
        self.client = ElevenLabs(api_key=elevenlabs_api_key)

        # Gemini setup
        gemini_api_key = "AIzaSyBzMQutGJnduWwKcTrmvAvP_QiTj8zaJ3I"  # Replace with your Gemini API key
        genai.configure(api_key=gemini_api_key)
        self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')

        self.recognizer = sr.Recognizer()
        self.current_model = "Samantha"
        self.trigger_algorithm.connect(self.run_algorithm_slot)
        self.play_startup_sound_signal.connect(self.play_startup_sound_slot)
        self.startup_sound_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Sounds", "mac_os_startup.wav")

    def run(self):
        while self.running:
            if not self.is_playing:
                if self.listening_for_command:
                    # Listen for the actual command after wake word
                    result = self.record_text()
                    if result:
                        self.process_command(result)
                elif not self.wake_word_detected:
                    # Listen for wake word
                    result = self.record_text()
                    if result:
                        self.process_speech(result)
            self.msleep(100)

    def play_startup_sound(self):
        self.play_startup_sound_signal.emit()

    def play_startup_sound_slot(self):
        if self.is_playing:
            self.update_signal.emit("Cannot play startup sound: audio already playing")
            return

        try:
            self.is_playing = True
            if not os.path.exists(self.startup_sound_path):
                raise FileNotFoundError(f"Startup sound file not found: {self.startup_sound_path}")
            sound = pygame.mixer.Sound(self.startup_sound_path)
            sound.play()
            duration_ms = int(sound.get_length() * 1000)
            QTimer.singleShot(duration_ms, self.reset_playing)
            self.update_signal.emit("Startup sound played")
        except Exception as e:
            self.update_signal.emit(f"Startup sound playback failed: {str(e)}")
            self.is_playing = False

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
        """Process recognized speech for wake words."""
        if not user_input:
            return

        wake_words = ["саманта", "Саманта", "джервис", "jarvis", "черви"]
        if any(wake_word in user_input for wake_word in wake_words):
            self.wake_word_detected = True
            self.listening_for_command = True
            # Play a short response to indicate listening
            self.play_listening_response()
            return

        elif user_input == "exit":
            self.update_signal.emit("Exiting chatbot")
            self.stop()

    def process_command(self, user_input):
        """Process the user's command after wake word."""
        if user_input == "exit":
            self.update_signal.emit("Exiting chatbot")
            self.stop()
            return

        # Send the command to Gemini and play the response
        self.play_samantha_response(user_input)
        self.listening_for_command = False
        self.wake_word_detected = False

    def play_listening_response(self):
        """Play a short response to indicate Samantha is listening."""
        if self.is_playing:
            self.update_signal.emit("Audio already playing")
            return

        try:
            self.is_playing = True
            audio_generator = self.client.generate(
                text="I'm listening, go ahead.",
                voice="Samantha",
                stream=False
            )
            audio_bytes = b"".join(audio_generator) if hasattr(audio_generator, '__iter__') else audio_generator
            audio_stream = io.BytesIO(audio_bytes)
            sound = pygame.mixer.Sound(audio_stream)
            sound.play()
            duration_ms = int(sound.get_length() * 1000)
            QTimer.singleShot(duration_ms, self.reset_playing)
            self.update_signal.emit("Listening response played")
        except Exception as e:
            self.update_signal.emit(f"Listening response failed: {str(e)}")
            self.is_playing = False

    def play_samantha_response(self, user_input):
        if self.is_playing:
            self.update_signal.emit("Audio already playing")
            return

        try:
            self.is_playing = True
            self.model_answering = True
            # Send user input to Gemini 1.5 Flash
            prompt = f"You are Samantha, a helpful AI assistant. Respond to the user in a friendly and conversational tone. User input: {user_input}"
            response = self.gemini_model.generate_content(prompt)
            response_text = response.text

            # Use ElevenLabs to convert Gemini response to speech
            audio_generator = self.client.generate(
                text=response_text,
                voice="Samantha",
                stream=False
            )
            audio_bytes = b"".join(audio_generator) if hasattr(audio_generator, '__iter__') else audio_generator
            audio_stream = io.BytesIO(audio_bytes)
            sound = pygame.mixer.Sound(audio_stream)
            sound.play()
            duration_ms = int(sound.get_length() * 1000)
            QTimer.singleShot(duration_ms, self.reset_playing)
            self.update_signal.emit("Samantha response played")
        except Exception as e:
            self.update_signal.emit(f"Audio playback failed: {str(e)}")
            self.is_playing = False
        finally:
            self.model_answering = False

    def run_algorithm(self):
        """Manually trigger Samantha to listen for a command."""
        self.wake_word_detected = True
        self.listening_for_command = True
        self.play_listening_response()

    def run_algorithm_slot(self):
        self.run_algorithm()

    def reset_playing(self):
        self.is_playing = False

    def stop(self):
        self.running = False
        pygame.mixer.quit()
        self.quit()
        self.wait()