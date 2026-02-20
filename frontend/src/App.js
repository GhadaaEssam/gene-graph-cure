import { Routes, Route } from "react-router-dom";
import LandingPage from "./pages/LandingPage";
import PredictionPage from "./pages/PredictionPage";

function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/predict" element={<PredictionPage />} />
    </Routes>
  );
}

export default App;