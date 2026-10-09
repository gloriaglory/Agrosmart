import { BrowserRouter, Routes, Route } from "react-router-dom";
import "./App.css";
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";
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
      <div className="flex min-h-screen flex-col">
        <Navbar />
        <main className="flex-1">
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
        </main>
        <Footer />
      </div>
      <Chatbot />
    </BrowserRouter>
  );
}

export default App;
