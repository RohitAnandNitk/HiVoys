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
    
    # Use lower bitrate for faster generation
    speech_config.set_speech_synthesis_output_format(
        speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3
    )

    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)

    # 🔹 Build SSML for speed and style
    ssml = f"""
        <speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis'
            xmlns:mstts='https://www.w3.org/2001/mstts' xml:lang='en-US'>
        <voice name='en-US-DavisNeural'>
            <mstts:express-as style='friendly'>
            <prosody rate='+15%'>
                Hi Rohit, nice to meet you. 
                <break time='200ms'/> 
                I'm Kavita, and I'll be conducting this interview today. 
                <break time='250ms'/> 
                Let's get started. 
                <break time='200ms'/> 
                Can you please tell me a little bit about your educational background? 
                Where did you start your academic journey?
            </prosody>
            </mstts:express-as>
        </voice>
        </speak>
        """

    # 🔹 Use the SSML synthesis method
    result = synthesizer.speak_ssml_async(ssml).get()
    
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        yield result.audio_data
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        error_msg = f"TTS canceled: {cancellation_details.reason}"
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            error_msg += f" - {cancellation_details.error_details}"
        raise Exception(error_msg)
    else:
        raise Exception(f"TTS failed: {result.reason}")
