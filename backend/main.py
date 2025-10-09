import os
import io
import json
import threading
from dotenv import load_dotenv
from flask import Flask, request
from flask_socketio import SocketIO, emit
from deepgram_client import DeepgramStreamClient
from azure_tts import stream_tts_audio
from src.LLM.groq_llm import GroqLLM

load_dotenv()

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading", ping_timeout=60, ping_interval=25)

# -------------------- GLOBALS -------------------- #
groq = GroqLLM()
groq_model = groq.get_model()
DG_API_KEY = os.environ["DEEPGRAM_API_KEY"]
dg_clients = {}  # sid → DeepgramStreamClient


# -------------------- EVENTS -------------------- #

@socketio.on("connect")
def handle_connect(auth=None):
    sid = request.sid
    print(f"✅ Client connected: {sid}")
    emit("server_message", {"text": "Connected to HiVoys WebSocket Server!"})


@socketio.on("start_session")
def handle_start_session(data=None):
    """Start new Deepgram live transcription session."""
    client_sid = request.sid
    print(f"🎤 Starting Deepgram session for: {client_sid}")

    def on_transcript_cb(transcript, is_final):
        socketio.emit("transcript", {"text": transcript, "is_final": is_final}, room=client_sid)

    dg = DeepgramStreamClient(api_key=DG_API_KEY, on_transcript=on_transcript_cb)
    dg.connect()
    dg_clients[client_sid] = dg

    emit("server_message", {"text": "Deepgram session started"})


@socketio.on("audio_chunk")
def handle_audio_chunk(blob):
    client_sid = request.sid
    try:
        dg = dg_clients.get(client_sid)
        if dg is None:
            print(f"⚠️ Creating new Deepgram session for {client_sid}")
            def on_transcript_cb(transcript, is_final):
                socketio.emit("transcript", {"text": transcript, "is_final": is_final}, room=client_sid)
            
            dg = DeepgramStreamClient(api_key=DG_API_KEY, on_transcript=on_transcript_cb)
            dg.connect()
            dg_clients[client_sid] = dg

        chunk_bytes = bytes(blob) if isinstance(blob, (bytes, bytearray)) else blob
        # Debug: print every 50th chunk to avoid spam
        if not hasattr(handle_audio_chunk, 'counter'):
            handle_audio_chunk.counter = 0
        handle_audio_chunk.counter += 1
        if handle_audio_chunk.counter % 50 == 0:
            print(f"📡 Sent {handle_audio_chunk.counter} audio chunks ({len(chunk_bytes)} bytes)")
        
        dg.send_audio(chunk_bytes)

    except Exception as e:
        print("❌ handle_audio_chunk error:", e)


@socketio.on("final_transcript")
def handle_final_transcript(payload):
    """Process transcript with streaming LLM and TTS for ultra-low latency."""
    text = payload.get("text", "")
    client_sid = request.sid

    if not text.strip():
        return

    print(f"🧠 User said: {text}")

    def process_streaming():
        try:
            # Stream LLM response and convert to TTS in real-time
            full_response = ""
            sentence_buffer = ""
            
            # Get streaming response from Groq
            for chunk in groq_model.stream(text):
                full_response += chunk
                sentence_buffer += chunk
                
                # When we have a complete sentence, convert to speech immediately
                if any(punct in sentence_buffer for punct in ['. ', '! ', '? ', '\n']):
                    sentence = sentence_buffer.strip()
                    if len(sentence) > 10:  # Only process meaningful sentences
                        print(f"🎵 Streaming TTS for: {sentence[:50]}...")
                        
                        # Get audio chunks and send them
                        for audio_chunk in stream_tts_audio(sentence):
                            # Ensure it's bytes
                            if isinstance(audio_chunk, bytes):
                                print(f"📤 Sending {len(audio_chunk)} bytes of audio")
                                socketio.emit("tts_chunk", audio_chunk, room=client_sid)
                            else:
                                print(f"⚠️ Warning: audio_chunk is not bytes: {type(audio_chunk)}")
                        
                        sentence_buffer = ""
            
            # Process any remaining text
            if sentence_buffer.strip():
                print(f"🎵 Final TTS chunk: {sentence_buffer[:50]}...")
                for audio_chunk in stream_tts_audio(sentence_buffer.strip()):
                    if isinstance(audio_chunk, bytes):
                        print(f"📤 Sending {len(audio_chunk)} bytes of audio")
                        socketio.emit("tts_chunk", audio_chunk, room=client_sid)
            
            # Signal completion
            socketio.emit("tts_done", {"text": full_response}, room=client_sid)
            print(f"✅ Completed response: {full_response}")
            
        except Exception as e:
            print(f"❌ Streaming error: {e}")
            import traceback
            traceback.print_exc()
            socketio.emit("error", {"message": str(e)}, room=client_sid)
    
    # Process in background
    thread = threading.Thread(target=process_streaming, daemon=True)
    thread.start()


@socketio.on("disconnect")
def handle_disconnect():
    """Cleanup Deepgram connections."""
    client_sid = request.sid
    dg = dg_clients.pop(client_sid, None)
    if dg:
        dg.close()
    print(f"❌ Client disconnected: {client_sid}")


# -------------------- MAIN -------------------- #
if __name__ == "__main__":
    print("🚀 Starting HiVoys WebSocket Server with Streaming...")
    socketio.run(app, host="0.0.0.0", port=5000, debug=False)