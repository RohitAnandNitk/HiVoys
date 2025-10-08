import React, { useState, useRef } from "react";
import RecordRTC from "recordrtc";
import { motion } from "framer-motion";
import { Mic, Square, Loader2 } from "lucide-react";

const VoiceRecorder = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [audioURL, setAudioURL] = useState("");
  const [loading, setLoading] = useState(false);
  const recorderRef = useRef(null);

  const startRecording = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const recorder = new RecordRTC(stream, {
      type: "audio",
      mimeType: "audio/wav",
    });
    recorder.startRecording();
    recorderRef.current = recorder;
    setIsRecording(true);
  };

  const stopRecording = () => {
    setLoading(true);
    recorderRef.current.stopRecording(() => {
      const blob = recorderRef.current.getBlob();
      const audioURL = URL.createObjectURL(blob);
      setAudioURL(audioURL);
      setIsRecording(false);
      setLoading(false);

      // send to backend
      const formData = new FormData();
      formData.append("audio", blob, "recording.wav");

      fetch("http://127.0.0.1:5000/api/transcribe", {
        method: "POST",
        body: formData,
      })
        .then((res) => res.json())
        .then((data) => console.log("Backend Response:", data))
        .catch((err) => console.error("Error:", err));
    });
  };

  return (
    <div className="flex flex-col items-center gap-6">
      <motion.button
        whileTap={{ scale: 0.9 }}
        onClick={isRecording ? stopRecording : startRecording}
        className={`w-24 h-24 flex items-center justify-center rounded-full shadow-lg border-2 border-white/30 transition-all ${
          isRecording ? "bg-red-500 animate-pulse" : "bg-indigo-500 hover:bg-indigo-600"
        }`}
      >
        {loading ? (
          <Loader2 className="animate-spin w-8 h-8 text-white" />
        ) : isRecording ? (
          <Square className="w-10 h-10 text-white" />
        ) : (
          <Mic className="w-10 h-10 text-white" />
        )}
      </motion.button>

      <p className="text-gray-300 text-sm">
        {isRecording ? "Listening..." : "Tap to start recording"}
      </p>

      {audioURL && (
        <audio
          controls
          src={audioURL}
          className="mt-4 w-64 rounded-xl shadow-lg bg-white/10"
        />
      )}
    </div>
  );
};

export default VoiceRecorder;
