# src/Utils/audio_utils.py
import io
import subprocess
import numpy as np
import soundfile as sf
import tempfile
import os

def transcribe_webm_audio(webm_blob, model):
    """
    Convert WebM Blob to WAV and transcribe using the given model.
    `webm_blob` is a bytes-like object.
    """
    temp_webm_path = None
    temp_wav_path = None
    
    try:
        print(f"🔄 Converting {len(webm_blob)} bytes of WebM to WAV...")
        
        # Verify we have data
        if len(webm_blob) < 100:
            print("❌ WebM data too small to be valid audio")
            return None
        
        # Create temporary files
        with tempfile.NamedTemporaryFile(suffix='.webm', delete=False) as temp_webm:
            temp_webm.write(webm_blob)
            temp_webm_path = temp_webm.name
        
        temp_wav_fd, temp_wav_path = tempfile.mkstemp(suffix='.wav')
        os.close(temp_wav_fd)
        
        # Prepare ffmpeg command with better error handling
        ffmpeg_cmd = [
            "ffmpeg",
            "-y",  # overwrite output
            "-hide_banner",
            "-loglevel", "error",
            "-i", temp_webm_path,
            "-ar", "16000",  # sample rate 16kHz
            "-ac", "1",      # mono channel
            "-f", "wav",
            temp_wav_path
        ]

        print(f"🎬 Running ffmpeg conversion...")
        
        # Run ffmpeg
        process = subprocess.run(
            ffmpeg_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=30
        )

        if process.returncode != 0:
            print(f"❌ FFmpeg error (code {process.returncode}):")
            print(process.stderr.decode())
            return None

        # Check if WAV file was created and has content
        if not os.path.exists(temp_wav_path) or os.path.getsize(temp_wav_path) < 100:
            print("❌ WAV file not created or too small")
            return None

        print(f"✅ WAV file created: {os.path.getsize(temp_wav_path)} bytes")

        # Read the WAV file
        audio, sr = sf.read(temp_wav_path)
        
        if sr != 16000:
            print(f"⚠️ Unexpected sample rate: {sr}, expected 16000")
        
        # Check if audio has content
        if len(audio) == 0:
            print("⚠️ Audio array is empty")
            return None
        
        # Ensure audio is 1D array (mono)
        if len(audio.shape) > 1:
            audio = audio.mean(axis=1)
        
        # Check audio amplitude
        max_amplitude = np.abs(audio).max()
        duration = len(audio) / sr
        print(f"📊 Audio stats - Duration: {duration:.2f}s, Samples: {len(audio)}, Max amplitude: {max_amplitude:.4f}")
        
        if max_amplitude < 0.001:
            print("⚠️ Audio amplitude too low, might be silence")
            return None

        # Transcribe using the model
        print("🎯 Transcribing audio...")
        
        # The model.transcribe expects audio as numpy array
        transcription_result = model.transcribe(audio)
        
        # Handle different return types
        if isinstance(transcription_result, dict):
            transcription = transcription_result.get("text", "").strip()
        elif isinstance(transcription_result, str):
            transcription = transcription_result.strip()
        else:
            print(f"⚠️ Unexpected transcription result type: {type(transcription_result)}")
            transcription = str(transcription_result).strip()
        
        print(f"✅ Transcription: '{transcription}'")
        return transcription if transcription else None

    except subprocess.TimeoutExpired:
        print("❌ FFmpeg timeout - audio might be too long")
        return None
    except Exception as e:
        print(f"❌ Error in transcribe_webm_audio: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        # Clean up temp files
        try:
            if temp_webm_path and os.path.exists(temp_webm_path):
                os.unlink(temp_webm_path)
            if temp_wav_path and os.path.exists(temp_wav_path):
                os.unlink(temp_wav_path)
        except Exception as e:
            print(f"⚠️ Error cleaning up temp files: {e}")