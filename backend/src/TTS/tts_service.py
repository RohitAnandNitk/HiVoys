import pyttsx3
import tempfile
from flask import send_file
import os

# Initialize pyttsx3 engine
tts_engine = pyttsx3.init()
tts_engine.setProperty('rate', 150)  # speech speed

def text_to_speech(text: str) -> str:
    """
    Convert text to speech and return temp audio file path.
    """
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts_engine.save_to_file(text, temp_file.name)
    tts_engine.runAndWait()
    return temp_file.name

def send_audio_file(file_path):
    """
    Helper to send audio file via Flask
    """
    response = send_file(file_path, mimetype="audio/mpeg", as_attachment=True, download_name="response.mp3")
    os.unlink(file_path)  # delete after sending
    return response
