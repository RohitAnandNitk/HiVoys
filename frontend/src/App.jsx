function App() {
  return (
    <div className="flex flex-col items-center justify-center h-screen bg-gradient-to-br from-slate-50 to-slate-200">
      <h1 className="text-xl font-bold text-gray-800 mb-4">🎤 HiVoys</h1>
      <p className="text-gray-600 text-lg">Your personal offline voice agent</p>
      <button className="mt-8 px-6 py-2 bg-blue-600 text-black rounded-xl shadow hover:bg-blue-700 transition">
        Start Talking
      </button>
    </div>
  );
}

export default App;
