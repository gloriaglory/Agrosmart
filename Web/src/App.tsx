import { BrowserRouter, Routes, Route } from "react-router-dom";
import "./App.css"; 
import Navbar from "./components/Navbar";
import Chatbot from "./components/Chatbot";
import Home from "./pages/Home";
import CropRecommendation from "./pages/CropRecommendation";
import CropDiseaseDetection from "./pages/CropDiseaseDetection";
import Marketplace from "./pages/Marketplace";
import MyProducts from "./pages/MyProducts";
import Education from "./pages/Education";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import UserProfile from "./pages/UserProfile";



function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/market" element={<Marketplace />} />
        <Route path="/products" element={<MyProducts />} />
        <Route path="/crop_recommendation" element={<CropRecommendation />} />
        <Route path="/disease_detection" element={<CropDiseaseDetection />} />
        <Route path="/education" element={<Education />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Signup />} />
        <Route path="/profile" element={<UserProfile />} />
      </Routes>
      <Chatbot />
    </BrowserRouter>
  );
}

export default App;
