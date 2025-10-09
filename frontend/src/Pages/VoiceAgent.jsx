// src/pages/VoiceAgent.jsx
import React, { useEffect, useRef, useState } from "react";
import io from "socket.io-client";

const SOCKET_URL = "http://localhost:5000"; // change to your backend URL

const VoiceAgent = () => {
  const socketRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioContextRef = useRef(null);
  const [isRecording, setIsRecording] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [aiReply, setAiReply] = useState("");
  const [isSpeaking, setIsSpeaking] = useState(false);

  useEffect(() => {
    // Initialize socket connection
    socketRef.current = io(SOCKET_URL, {
      transports: ["websocket"],
    });

    socketRef.current.on("connect", () => {
      console.log("✅ Connected to backend WebSocket");
      socketRef.current.emit("start_session");
    });

    socketRef.current.on("server_message", (data) => {
      console.log("Server:", data.text);
    });

    socketRef.current.on("transcript", (data) => {
      console.log("Transcript:", data.text, "Final:", data.is_final);

      if (data.is_final) {
        setTranscript((prev) => prev + "\n" + data.text);
        // Send to backend immediately for LLM + TTS
        socketRef.current.emit("final_transcript", { text: data.text });
      }
      // Remove interim display for faster response
    });

    socketRef.current.on("tts_chunk", (chunk) => {
      console.log(
        "Received TTS chunk - Type:",
        typeof chunk,
        "Constructor:",
        chunk?.constructor?.name
      );
      console.log("Is ArrayBuffer:", chunk instanceof ArrayBuffer);
      console.log("Is Uint8Array:", chunk instanceof Uint8Array);
      console.log("Is Blob:", chunk instanceof Blob);
      console.log("Raw chunk:", chunk);

      if (!chunk) {
        console.error("Received empty chunk");
        return;
      }

      // Stop recording when AI starts speaking
      if (isRecording) {
        stopRecording();
      }

      // Play audio immediately
      try {
        let audioBlob;

        // Handle different data types
        if (chunk instanceof Blob) {
          audioBlob = chunk;
        } else if (
          chunk instanceof ArrayBuffer ||
          chunk instanceof Uint8Array
        ) {
          audioBlob = new Blob([chunk], { type: "audio/mpeg" });
        } else if (typeof chunk === "string") {
          // If it's base64 string, decode it
          const binaryString = atob(chunk);
          const bytes = new Uint8Array(binaryString.length);
          for (let i = 0; i < binaryString.length; i++) {
            bytes[i] = binaryString.charCodeAt(i);
          }
          audioBlob = new Blob([bytes], { type: "audio/mpeg" });
        } else {
          console.error("Unknown chunk type:", typeof chunk);
          return;
        }

        console.log("Created blob:", audioBlob.size, "bytes");
        const audioUrl = URL.createObjectURL(audioBlob);
        const audio = new Audio(audioUrl);

        setIsSpeaking(true);

        audio.onended = () => {
          URL.revokeObjectURL(audioUrl);
          setIsSpeaking(false);
        };

        audio.onerror = (err) => {
          console.error("Audio playback error:", err);
          console.error("Audio src:", audio.src);
          console.error("Audio error code:", audio.error?.code);
          console.error("Audio error message:", audio.error?.message);
          URL.revokeObjectURL(audioUrl);
          setIsSpeaking(false);
        };

        audio.play().catch((err) => {
          console.error("Error playing audio:", err);
          setIsSpeaking(false);
        });
      } catch (err) {
        console.error("Error creating audio:", err);
      }
    });

    socketRef.current.on("tts_done", (data) => {
      console.log("AI Reply complete:", data.text);
      setAiReply(data.text);
    });

    socketRef.current.on("error", (data) => {
      console.error("Server error:", data.message);
    });

    return () => {
      socketRef.current.disconnect();
      stopRecording();
    };
  }, []);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: 1,
          sampleRate: 48000,
          echoCancellation: true,
          noiseSuppression: true,
        },
      });

      // Create audio context for processing
      audioContextRef.current = new (window.AudioContext ||
        window.webkitAudioContext)({
        sampleRate: 48000,
      });

      const source = audioContextRef.current.createMediaStreamSource(stream);
      const processor = audioContextRef.current.createScriptProcessor(
        2048,
        1,
        1
      );

      source.connect(processor);
      processor.connect(audioContextRef.current.destination);

      let chunkCount = 0;
      processor.onaudioprocess = (e) => {
        if (!socketRef.current || !socketRef.current.connected) return;

        const inputData = e.inputBuffer.getChannelData(0);
        // Convert Float32Array to Int16Array (PCM)
        const pcmData = new Int16Array(inputData.length);
        for (let i = 0; i < inputData.length; i++) {
          const s = Math.max(-1, Math.min(1, inputData[i]));
          pcmData[i] = s < 0 ? s * 0x8000 : s * 0x7fff;
        }

        // Send binary data immediately without buffering
        socketRef.current.emit("audio_chunk", pcmData.buffer);

        // Debug logging
        chunkCount++;
        if (chunkCount % 50 === 0) {
          console.log(`📤 Sent ${chunkCount} audio chunks`);
        }
      };

      mediaRecorderRef.current = { processor, source, stream };
      setIsRecording(true);
      setTranscript(""); // Clear previous transcript
      console.log("🎙️ Recording started...");
    } catch (error) {
      console.error("❌ Error starting recording:", error);
      alert("Microphone access denied or error occurred");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current) {
      const { processor, source, stream } = mediaRecorderRef.current;

      if (processor) processor.disconnect();
      if (source) source.disconnect();
      if (stream) stream.getTracks().forEach((track) => track.stop());

      if (audioContextRef.current) {
        audioContextRef.current.close();
      }

      mediaRecorderRef.current = null;
      setIsRecording(false);
      console.log("🛑 Recording stopped.");
    }
  };

  const playNextChunk = () => {
    if (audioQueueRef.current.length === 0) {
      isPlayingRef.current = false;
      setIsSpeaking(false);
      return;
    }

    isPlayingRef.current = true;
    const chunk = audioQueueRef.current.shift();

    // Create blob with MP3 type (matching backend)
    const audioBlob = new Blob([chunk], { type: "audio/mpeg" });
    const audioUrl = URL.createObjectURL(audioBlob);
    const audio = new Audio(audioUrl);

    audio.onended = () => {
      URL.revokeObjectURL(audioUrl);
      // Play next chunk immediately when current finishes
      playNextChunk();
    };

    audio.onerror = (err) => {
      console.error("Audio playback error:", err);
      URL.revokeObjectURL(audioUrl);
      // Continue with next chunk even if error
      playNextChunk();
    };

    audio.play().catch((err) => {
      console.error("Error playing audio:", err);
      URL.revokeObjectURL(audioUrl);
      playNextChunk();
    });
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-900 text-white p-6">
      <h1 className="text-3xl font-bold mb-4">
        🎧 HiVoys - Voice Interview Agent
      </h1>

      <div className="w-full max-w-lg bg-gray-800 p-6 rounded-2xl shadow-md space-y-4">
        <div className="flex justify-center">
          {!isRecording ? (
            <button
              onClick={startRecording}
              className="bg-green-500 px-6 py-3 rounded-full text-white text-lg hover:bg-green-600 transition"
            >
              🎙️ Start Talking
            </button>
          ) : (
            <button
              onClick={stopRecording}
              className="bg-red-500 px-6 py-3 rounded-full text-white text-lg hover:bg-red-600 transition"
            >
              🛑 Stop
            </button>
          )}
        </div>

        <div className="bg-gray-700 p-4 rounded-lg h-40 overflow-y-auto">
          <h2 className="text-xl font-semibold mb-2">🗣️ Your Transcript</h2>
          <p className="whitespace-pre-wrap text-gray-200">
            {transcript || "Say something..."}
          </p>
        </div>

        <div className="bg-gray-700 p-4 rounded-lg h-40 overflow-y-auto">
          <h2 className="text-xl font-semibold mb-2">🤖 AI Response</h2>
          <p className="whitespace-pre-wrap text-green-300">
            {aiReply || "AI is waiting..."}
          </p>
        </div>

        {isSpeaking && (
          <p className="text-yellow-400 text-center">🔊 Speaking...</p>
        )}
      </div>
    </div>
  );
};

export default VoiceAgent;
