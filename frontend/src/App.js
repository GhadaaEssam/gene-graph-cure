import { Routes, Route, Outlet } from "react-router-dom"; // ضفنا Outlet هنا

// استيراد الـ Navbars الجديدة
import PublicNavbar from "./components/layout/PublicNavbar"; // ده الـ Navbar بتاع الزوار
import PrivateNavbar from "./components/layout/PrivateNavbar"; // ده الـ Navbar بتاع التيم بعد التسجيل

// استيراد الصفحات بتاعتك زي ما هي
import LandingPage from "./pages/LandingPage";
import LoginPage from "./pages/LoginPage";
import SignUpPage from "./pages/SignUpPage";
import ImpactPage from "./pages/ImpactPage";
import Dashboard from "./pages/Dashboard";
import NewAnalysis from "./pages/NewAnalysis";
import ResultsPage from "./pages/ResultsPage";
import ChatAssistantPage from "./pages/ChatAssistantPage";
import InteractiveVisualization from "./pages/InteractiveVisualization";

// ----------------------------------------------------
// 1. إنشاء Layout للصفحات العامة (Public)
// ----------------------------------------------------
const PublicLayout = () => {
  return (
    <>
      <PublicNavbar />
      <Outlet /> {/* الأوتليت ده هو المكان اللي الصفحات هتتعرض جواه */}
    </>
  );
};

// ----------------------------------------------------
// 2. إنشاء Layout للصفحات الخاصة (Private / Dashboard)
// ----------------------------------------------------
const PrivateLayout = () => {
  return (
    <>
      <PrivateNavbar />
      <Outlet /> 
    </>
  );
};

// ----------------------------------------------------
// 3. التطبيق الرئيسي 
// ----------------------------------------------------
function App() {
  return (
    <Routes>
      
      {/* الجروب الأول: الصفحات اللي هتاخد الـ Public Navbar */}
      <Route element={<PublicLayout />}>
        <Route path="/" element={<LandingPage />} />
        <Route path="/impact" element={<ImpactPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/signup" element={<SignUpPage />} />
      </Route>

      {/* الجروب التاني: الصفحات اللي هتاخد الـ Private Navbar */}
      <Route element={<PrivateLayout />}>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/new-analysis" element={<NewAnalysis />} />
        <Route path="/results" element={<ResultsPage />} />
        <Route path="/chat" element={<ChatAssistantPage />} />
        <Route path="/visualization" element={<InteractiveVisualization />} />
      </Route>

    </Routes>
  );
}

export default App;