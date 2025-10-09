# backend/deepgram_client.py
import json
import threading
import websocket

class DeepgramStreamClient:
    def __init__(self, api_key, on_transcript):
        """
        on_transcript(transcript_text: str, is_final: bool) -> None
        """
        self.api_key = api_key
        self.on_transcript = on_transcript
        self.ws = None
        self._running = False

    def connect(self):
        """Start WebSocket connection in a separate thread."""
        # Enable interim results and VAD for faster response
        url = "wss://api.deepgram.com/v1/listen?model=nova-2&encoding=linear16&sample_rate=48000&channels=1&interim_results=true&endpointing=300&vad_events=true"
        
        def on_message(ws, message):
            try:
                data = json.loads(message)
                
                # Handle transcript results
                if data.get("type") == "Results":
                    channel = data.get("channel", {})
                    alternatives = channel.get("alternatives", [])
                    if alternatives:
                        transcript = alternatives[0].get("transcript", "")
                        is_final = data.get("is_final", False)
                        if transcript.strip():
                            self.on_transcript(transcript, is_final)
                
                # Handle speech started event
                elif data.get("type") == "SpeechStarted":
                    print("🎤 Speech detected")
                
            except json.JSONDecodeError:
                pass
            except Exception as e:
                print(f"❌ Deepgram message error: {e}")

        def on_error(ws, error):
            print(f"❌ Deepgram WebSocket error: {error}")

        def on_close(ws, close_status_code, close_msg):
            print(f"🔌 Deepgram connection closed: {close_status_code}")
            self._running = False

        def on_open(ws):
            print("✅ Deepgram WebSocket connected")
            self._running = True

        # Create WebSocket connection
        self.ws = websocket.WebSocketApp(
            url,
            header={"Authorization": f"Token {self.api_key}"},
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close
        )

        # Run in separate thread
        wst = threading.Thread(target=self.ws.run_forever, daemon=True)
        wst.start()

    def send_audio(self, chunk_bytes: bytes):
        """Send binary audio chunk to Deepgram websocket."""
        if self.ws and self._running:
            try:
                self.ws.send(chunk_bytes, opcode=websocket.ABNF.OPCODE_BINARY)
            except Exception as e:
                print(f"❌ Error sending audio to Deepgram: {e}")

    def close(self):
        """Close the WebSocket connection."""
        self._running = False
        if self.ws:
            try:
                self.ws.close()
            except Exception as e:
                print(f"❌ Error closing Deepgram connection: {e}")