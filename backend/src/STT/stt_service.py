from faster_whisper import WhisperModel
import tempfile
import os

# Load Whisper model once
model = WhisperModel("small")  # small, medium, large

def transcribe_audio(file_obj) -> str:
    """
    Transcribe uploaded audio file to text.
    file_obj: file-like object (e.g., Flask file)
    """
    # Save temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    file_obj.save(temp_file.name)

    # Transcribe
    segments, info = model.transcribe(temp_file.name)
    text = " ".join([segment.text for segment in segments])

    # Delete temp file
    os.unlink(temp_file.name)
    return text
