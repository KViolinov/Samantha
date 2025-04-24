# from PyQt5.QtCore import QThread, pyqtSignal, QTimer
# from elevenlabs.client import ElevenLabs
# import speech_recognition as sr
# import pygame
# import io
# import os
# import google.generativeai as genai
# import random
# import logging
#
# # Set up logging to catch errors
# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
#
# class LogicThread(QThread):
#     update_signal = pyqtSignal(str)
#     trigger_algorithm = pyqtSignal()
#     play_startup_sound_signal = pyqtSignal()
#
#     def __init__(self):
#         super().__init__()
#         self.running = True
#         self.is_playing = False
#         self.wake_word_detected = False
#         self.model_answering = False
#         pygame.mixer.init()
#
#         # ElevenLabs setup
#         elevenlabs_api_key = "sk_0dfe95fad3b8b17af02ce8d21ecf0fb1c5c63e97b2688707"
#         self.client = ElevenLabs(api_key=elevenlabs_api_key)
#
#         # Gemini setup
#         gemini_api_key = "AIzaSyBzMQutGJnduWwKcTrmvAvP_QiTj8zaJ3I"
#         genai.configure(api_key=gemini_api_key)
#         self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
#
#         self.recognizer = sr.Recognizer()
#         self.current_model = "Samantha"
#         self.jarvis_responses = [
#             "Hello, I'm Samantha, ready to assist!",
#             "Samantha online, what's up?",
#             "Hey there, Samantha at your service!"
#         ]
#         self.trigger_algorithm.connect(self.run_algorithm_slot)
#         self.play_startup_sound_signal.connect(self.play_startup_sound_slot)
#         self.startup_sound_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Sounds", "mac_os_startup.wav")
#
#     def run(self):
#         try:
#             while self.running:
#                 if not self.is_playing:
#                     if not self.wake_word_detected:
#                         # Listen for wake word
#                         self.update_signal.emit("Listening for wake word...")
#                         result = self.record_text()
#                         if result:
#                             self.process_wake_word(result)
#                     else:
#                         # Listen for command
#                         self.update_signal.emit("Listening for command...")
#                         result = self.record_text()
#                         if result:
#                             self.process_command(result)
#                 self.msleep(100)
#         except Exception as e:
#             logging.error(f"Error in run loop: {str(e)}")
#             self.update_signal.emit(f"Error in run loop: {str(e)}")
#             raise
#
#     def play_startup_sound(self):
#         self.play_startup_sound_signal.emit()
#
#     def play_startup_sound_slot(self):
#         if self.is_playing:
#             self.update_signal.emit("Cannot play startup sound: audio already playing")
#             return
#
#         try:
#             self.is_playing = True
#             if not os.path.exists(self.startup_sound_path):
#                 raise FileNotFoundError(f"Startup sound file not found: {self.startup_sound_path}")
#             sound = pygame.mixer.Sound(self.startup_sound_path)
#             sound.play()
#             duration_ms = int(sound.get_length() * 1000)
#             QTimer.singleShot(duration_ms + 500, self.reset_playing)
#             self.update_signal.emit("Startup sound played")
#         except Exception as e:
#             logging.error(f"Startup sound error: {str(e)}")
#             self.update_signal.emit(f"Startup sound playback failed: {str(e)}")
#             self.is_playing = False
#
#     def record_text(self):
#         """Listen for speech and return the recognized text with retry logic."""
#         max_attempts = 3
#         for attempt in range(max_attempts):
#             try:
#                 with sr.Microphone() as source:
#                     self.recognizer.adjust_for_ambient_noise(source, duration=0.2)  # Reduced duration to match previous project
#                     audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
#                     text = self.recognizer.recognize_google(audio, language="bg-BG")
#                     self.update_signal.emit(f"You said: {text}")
#                     return text.lower()
#             except sr.RequestError as e:
#                 self.update_signal.emit(f"API Request Error: {e}")
#                 logging.error(f"Speech recognition API error: {str(e)}")
#                 return None
#             except sr.UnknownValueError:
#                 self.update_signal.emit("Sorry, I didn't catch that. Please try again.")
#                 if attempt == max_attempts - 1:
#                     return None
#                 self.msleep(500)
#             except sr.WaitTimeoutError:
#                 self.update_signal.emit("Listening timed out. Please speak again.")
#                 if attempt == max_attempts - 1:
#                     return None
#                 self.msleep(500)
#             except Exception as e:
#                 logging.error(f"Unexpected error in record_text: {str(e)}")
#                 self.update_signal.emit(f"Unexpected error in record_text: {str(e)}")
#                 return None
#
#     def process_wake_word(self, user_input):
#         """Process recognized speech for wake words."""
#         if not user_input:
#             return
#
#         try:
#             wake_words = ["саманта", "Саманта", "джервис", "jarvis", "черви"]
#             if any(wake_word in user_input for wake_word in wake_words):
#                 self.wake_word_detected = True
#                 self.model_answering = True
#                 self.play_confirmation_sound()
#                 response = random.choice(self.jarvis_responses)
#                 self.play_audio(response)
#                 self.model_answering = False
#                 self.update_signal.emit("Wake word detected!")
#             elif user_input == "излез":
#                 self.update_signal.emit("Exiting chatbot")
#                 self.play_audio("Goodbye!")
#                 self.stop()
#         except Exception as e:
#             logging.error(f"Error in process_wake_word: {str(e)}")
#             self.update_signal.emit(f"Error in process_wake_word: {str(e)}")
#             self.wake_word_detected = False
#
#     def process_command(self, user_input):
#         """Process the user's command after wake word."""
#         if not user_input:
#             self.wake_word_detected = False
#             return
#
#         try:
#             if user_input == "излез":
#                 self.update_signal.emit("Exiting chatbot")
#                 self.play_audio("Goodbye!")
#                 self.stop()
#                 return
#
#             self.is_playing = True
#             self.model_answering = True
#             prompt = f"You are Samantha, a helpful AI assistant. Respond to the user in a friendly and conversational tone. User input: {user_input}"
#             response = self.gemini_model.generate_content(prompt)
#             response_text = response.text
#             self.update_signal.emit(f"Gemini response: {response_text}")
#             self.play_audio(response_text)
#             self.update_signal.emit("Samantha response played")
#         except Exception as e:
#             logging.error(f"Error in process_command: {str(e)}")
#             self.update_signal.emit(f"Audio playback failed: {str(e)}")
#         finally:
#             self.is_playing = False
#             self.model_answering = False
#             self.wake_word_detected = False
#
#     def play_confirmation_sound(self):
#         """Play a confirmation sound after wake word detection."""
#         try:
#             self.is_playing = True
#             audio_generator = self.client.generate(
#                 text="Beep",
#                 voice="Samantha",
#                 stream=False
#             )
#             audio_bytes = b"".join(audio_generator) if hasattr(audio_generator, '__iter__') else audio_generator
#             audio_stream = io.BytesIO(audio_bytes)
#             sound = pygame.mixer.Sound(audio_stream)
#             sound.play()
#             duration_ms = int(sound.get_length() * 1000)
#             QTimer.singleShot(duration_ms + 1000, self.reset_playing)  # Increased delay
#         except Exception as e:
#             logging.error(f"Confirmation sound error: {str(e)}")
#             self.update_signal.emit(f"Confirmation sound failed: {str(e)}")
#             self.is_playing = False
#
#     def play_audio(self, text):
#         """Play audio for a given text using ElevenLabs."""
#         try:
#             self.is_playing = True
#             audio_generator = self.client.generate(
#                 text=text,
#                 voice="Samantha",
#                 stream=False
#             )
#             audio_bytes = b"".join(audio_generator) if hasattr(audio_generator, '__iter__') else audio_generator
#             audio_stream = io.BytesIO(audio_bytes)
#             sound = pygame.mixer.Sound(audio_stream)
#             sound.play()
#             duration_ms = int(sound.get_length() * 1000)
#             QTimer.singleShot(duration_ms + 2000, self.reset_playing)  # Increased delay to 2 seconds
#         except Exception as e:
#             logging.error(f"Audio playback error: {str(e)}")
#             self.update_signal.emit(f"Audio playback failed: {str(e)}")
#             self.is_playing = False
#
#     def run_algorithm(self):
#         """Manually trigger Samantha to listen for a command."""
#         try:
#             self.wake_word_detected = True
#             self.model_answering = True
#             self.play_confirmation_sound()
#             response = random.choice(self.jarvis_responses)
#             self.play_audio(response)
#             self.model_answering = False
#             self.update_signal.emit("Wake word detected!")
#         except Exception as e:
#             logging.error(f"Error in run_algorithm: {str(e)}")
#             self.update_signal.emit(f"Error in run_algorithm: {str(e)}")
#
#     def run_algorithm_slot(self):
#         self.run_algorithm()
#
#     def reset_playing(self):
#         self.is_playing = False
#
#     def stop(self):
#         self.running = False
#         pygame.mixer.quit()
#         self.quit()
#         self.wait()



from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from elevenlabs.client import ElevenLabs
import speech_recognition as sr
import pygame
import io
import os
import google.generativeai as genai
import logging

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class LogicThread(QThread):
    update_signal = pyqtSignal(str)
    play_startup_sound_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.running = True
        self.is_playing = False
        self.model_answering = False
        pygame.mixer.init()

        # ElevenLabs setup
        self.client = ElevenLabs(api_key="sk_0dfe95fad3b8b17af02ce8d21ecf0fb1c5c63e97b2688707")

        # Gemini setup
        genai.configure(api_key="AIzaSyBzMQutGJnduWwKcTrmvAvP_QiTj8zaJ3I")
        self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')

        self.recognizer = sr.Recognizer()
        self.current_model = "Samantha"
        self.startup_sound_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Sounds", "mac_os_startup.wav")

    def run(self):
        self.play_audio("Hello, I'm Samantha. Let's talk!")
        try:
            while self.running:
                if not self.is_playing:
                    self.update_signal.emit("Listening...")
                    user_input = self.record_text()
                    if user_input:
                        self.respond(user_input)
                self.msleep(100)
        except Exception as e:
            logging.error(f"Error in run loop: {str(e)}")
            self.update_signal.emit(f"Error in run loop: {str(e)}")

    def record_text(self):
        """Listen for speech and return the recognized text with retry logic."""
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                with sr.Microphone() as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.2)
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                    text = self.recognizer.recognize_google(audio, language="bg-BG")
                    self.update_signal.emit(f"You said: {text}")
                    return text.lower()
            except sr.RequestError as e:
                self.update_signal.emit(f"API Request Error: {e}")
                logging.error(f"Speech recognition API error: {str(e)}")
                return None
            except sr.UnknownValueError:
                self.update_signal.emit("Sorry, I didn't catch that. Please try again.")
                if attempt == max_attempts - 1:
                    return None
                self.msleep(500)
            except sr.WaitTimeoutError:
                self.update_signal.emit("Listening timed out. Please speak again.")
                if attempt == max_attempts - 1:
                    return None
                self.msleep(500)
            except Exception as e:
                logging.error(f"Unexpected error in record_text: {str(e)}")
                self.update_signal.emit(f"Unexpected error in record_text: {str(e)}")
                return None

    def respond(self, user_input):
        """Get Gemini's response and speak it."""
        if user_input == "излез":
            self.update_signal.emit("Exiting chatbot")
            self.play_audio("Goodbye!")
            self.stop()
            return

        try:
            self.model_answering = True
            prompt = f"You are Samantha, a friendly and thoughtful AI assistant. The user said: {user_input}"
            response = self.gemini_model.generate_content(prompt)
            response_text = response.text
            self.update_signal.emit(f"Gemini response: {response_text}")
            self.play_audio(response_text)
        except Exception as e:
            logging.error(f"Error in respond: {str(e)}")
            self.update_signal.emit(f"Response error: {str(e)}")
        finally:
            self.model_answering = False

    def play_audio(self, text):
        """Play audio for a given text using ElevenLabs."""
        try:
            self.is_playing = True
            audio_generator = self.client.generate(
                text=text,
                voice="Samantha",
                stream=False
            )
            audio_bytes = b"".join(audio_generator) if hasattr(audio_generator, '__iter__') else audio_generator
            audio_stream = io.BytesIO(audio_bytes)
            sound = pygame.mixer.Sound(audio_stream)
            sound.play()
            duration_ms = int(sound.get_length() * 1000)
            QTimer.singleShot(duration_ms + 2000, self.reset_playing)
        except Exception as e:
            logging.error(f"Audio playback error: {str(e)}")
            self.update_signal.emit(f"Audio playback failed: {str(e)}")
            self.is_playing = False

    def reset_playing(self):
        self.is_playing = False

    def stop(self):
        self.running = False
        pygame.mixer.quit()
        self.quit()
        self.wait()
