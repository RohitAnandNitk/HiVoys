import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import VoiceAgent from "./Pages/VoiceAgent";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<VoiceAgent />} />
      </Routes>
    </Router>
  );
}

export default App;
