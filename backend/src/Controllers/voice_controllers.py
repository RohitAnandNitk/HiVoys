from src.Utils.audio_utils import transcribe_audio
from backend.src.LLM.groq_llm import GroqLLM

def process_audio(audio_file):
    # Step 1: Transcribe the uploaded audio
    transcription_text = transcribe_audio(audio_file)

    # Step 2: Get response from LLM (Groq API or similar)
    groq =  GroqLLM()
    groq_model = groq.get_model()
    response = groq_model.invoke(transcription_text)
    llm_response = response.content

    return {
        "message": "Audio processed successfully!",
        "transcription": transcription_text,
        "llm_response": llm_response
    }
