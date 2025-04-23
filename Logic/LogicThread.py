from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from elevenlabs.client import ElevenLabs
import pygame
import io
import os

class LogicThread(QThread):
    update_signal = pyqtSignal(str)
    trigger_algorithm = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.running = True
        self.is_playing = False
        pygame.mixer.init()
        api_key = "sk_0dfe95fad3b8b17af02ce8d21ecf0fb1c5c63e97b2688707"
        self.client = ElevenLabs(api_key=api_key)
        self.trigger_algorithm.connect(self.run_algorithm_slot)

    def run(self):
        while self.running:
            self.msleep(100)

    def run_algorithm(self):
        if self.is_playing:
            return "Audio already playing"
        try:
            self.is_playing = True
            # Generate audio and concatenate generator output into bytes
            audio_generator = self.client.generate(
                text="Hello Sam, How are you doing?",
                voice="Samantha",
                stream=False  # Ensure non-streaming for simplicity
            )
            audio_bytes = b"".join(audio_generator) if hasattr(audio_generator, '__iter__') else audio_generator
            audio_stream = io.BytesIO(audio_bytes)
            sound = pygame.mixer.Sound(audio_stream)
            sound.play()
            # Reset is_playing after approximate audio duration (2 seconds)
            QTimer.singleShot(2000, self.reset_playing)
            return "Audio playback started"
        except Exception as e:
            self.is_playing = False
            return f"Audio playback failed: {str(e)}"

    def run_algorithm_slot(self):
        result = self.run_algorithm()
        self.update_signal.emit(result)

    def reset_playing(self):
        self.is_playing = False

    def stop(self):
        self.running = False
        pygame.mixer.quit()