import { Mic } from "lucide-react";
import VoiceRecorder from "../Components/VoiceRecorder";

function VoiceAgent() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center text-white">
      <div className="bg-slate-800/50 backdrop-blur-xl p-10 rounded-3xl shadow-2xl border border-slate-700 w-[95%] max-w-4xl flex flex-col items-center">
        {/* Logo and Title */}
        <div className="flex items-center gap-3 mb-6">
          <div className="bg-blue-600/20 p-3 rounded-full">
            <Mic className="text-blue-400 w-6 h-6" />
          </div>
          <h1 className="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-cyan-300">
            HiVoys
          </h1>
        </div>

        {/* Subtitle */}
        <p className="text-gray-300 mb-8 text-center text-lg">
          Your personal offline voice agent 🎧
        </p>

        {/* Voice Recorder Component */}
        <div className="w-full flex justify-center">
          {/* Replace with your VoiceRecorder component */}
          <div className="bg-slate-700/50 p-8 rounded-2xl border border-slate-600 w-full max-w-2xl">
            <p className="text-center text-gray-400">
              <VoiceRecorder />
            </p>
          </div>
        </div>

        {/* Footer */}
        <footer className="mt-10 text-sm text-gray-400">
          Built with <span className="text-pink-500">❤</span> by{" "}
          <span className="text-cyan-400 font-semibold">HiVoys</span>
        </footer>
      </div>
    </div>
  );
}

export default VoiceAgent;
