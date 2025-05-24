import { BrowserRouter, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import Chatbot from "./components/Chatbot";
import Home from "./pages/Home";
import CropRecommendation from "./pages/CropRecommendation";
import CropDiseaseDetection from "./pages/CropDiseaseDetection";
import CropMarket from "./pages/CropMarket";

function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/market" element={<CropMarket />} />
        <Route path="/crop_recommendation" element={<CropRecommendation />} />
        <Route path="/disease_detection" element={<CropDiseaseDetection />} />
      </Routes>
      <Chatbot />
    </BrowserRouter>
  );
}

export default App;
