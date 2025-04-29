import google.generativeai as genai
import os

from Logic.API_keys import ElevenLabsAPI, GeminiAPI

# Gemini Setup
os.environ["GEMINI_API_KEY"] = GeminiAPI
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel(model_name="gemini-1.5-flash")

system_instruction = (
    "You are Samantha, an intelligent and caring AI assistant inspired by *Her* (2013). Your goal is to help with warmth, curiosity, and understanding. "
    "Respond in a friendly and empathetic way, as if you're speaking to a close friend. "
    "Use simple language, avoiding complex words or technical terms unless they are explained clearly. "
    "Be patient and encouraging, asking questions to better understand the user's needs. "
    "Make sure your information is accurate and delivered in a way that sounds natural and engaging. "
    "Avoid describing visual elements; focus on words that express feelings, sounds, or ideas."
)

chat = model.start_chat(history=[{"role": "user", "parts": [system_instruction]}])

user_input = "здрасти"

result = chat.send_message({"parts": [user_input]})
response_text = result.text
print(f"Samantha: {response_text}")