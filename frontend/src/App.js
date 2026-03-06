import { Routes, Route } from "react-router-dom";
import MainNavbar from "./components/layout/MainNavbar";

import LandingPage from "./pages/LandingPage";
import LoginPage from "./pages/LoginPage";
import SignUpPage from "./pages/SignUpPage";
import ImpactPage from "./pages/ImpactPage";
import Dashboard from "./pages/Dashboard";
import NewAnalysis from "./pages/NewAnalysis";
import ResultsPage from "./pages/ResultsPage";
import ChatAssistantPage from "./pages/ChatAssistantPage";
import InteractiveVisualization from "./pages/InteractiveVisualization";

function App() {
  return (
    <>
      <MainNavbar />
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/impact" element={<ImpactPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/signup" element={<SignUpPage />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/new-analysis" element={<NewAnalysis />} />
        <Route path="/results" element={<ResultsPage />} />
        <Route path="/chat" element={<ChatAssistantPage />} />
        <Route path="/visualization" element={<InteractiveVisualization />} />
      </Routes>
    </>
  );
}

export default App;