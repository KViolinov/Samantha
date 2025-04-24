from elevenlabs import play
from elevenlabs.client import ElevenLabs
import pygame

client = ElevenLabs(api_key="sk_0dfe95fad3b8b17af02ce8d21ecf0fb1c5c63e97b2688707")

audio = client.generate(text = "Hello Sam, How are you doing?", voice = "Samantha")
play(audio)
