# backend/azure_tts_streaming.py
import os
import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv

load_dotenv()

SPEECH_KEY = os.environ["AZURE_SPEECH_KEY"]
SPEECH_REGION = os.environ["AZURE_SPEECH_REGION"]

def stream_tts_audio(text):
    """
    Generate TTS audio and return complete audio data.
    Optimized for speed with lower quality audio format.
    """
    speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)
    
    # Use fastest voice and optimal format
    speech_config.speech_synthesis_voice_name = "en-US-AriaNeural"
    # Use lower quality for faster generation
    speech_config.set_speech_synthesis_output_format(
        speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3
    )
    
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)
    
    result = synthesizer.speak_text_async(text).get()
    
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        # Return complete audio as single chunk
        yield result.audio_data
            
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        error_msg = f"TTS canceled: {cancellation_details.reason}"
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            error_msg += f" - {cancellation_details.error_details}"
        raise Exception(error_msg)
    else:
        raise Exception(f"TTS failed: {result.reason}")