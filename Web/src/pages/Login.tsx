import { useState } from "react";
import axios from "axios";
import { useNavigate, useLocation } from "react-router-dom";
import { FaGoogle, FaFacebook } from "react-icons/fa";

const API_BASE = "http://localhost:8000/api/auth/login/";

export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);

  const navigate = useNavigate();
  const location = useLocation();

  // Get 'from' path from location state or fallback to "/"
  const from = (location.state as { from?: string })?.from || "/";

  const handleLogin = async () => {
    setError(null);
    try {
      const res = await axios.post(API_BASE, { username, password });
      localStorage.setItem("token", res.data.token);
      alert("Login successful");
      // Redirect to 'from' location after login
      navigate(from, { replace: true });
    } catch (err: any) {
      setError(err.response?.data?.error || "Login failed.");
    }
  };

  const handleSocialLogin = (provider: "google" | "facebook") => {
    window.location.href = `http://localhost:8000/api/auth/${provider}/`;
  };

  return (
    <div className="max-w-md mx-auto mt-10 bg-white p-6 rounded shadow">
      <h2 className="text-2xl font-bold mb-4">Login</h2>

      <input
        type="text"
        placeholder="Username"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        className="w-full mb-3 p-2 border rounded"
      />
      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        className="w-full mb-4 p-2 border rounded"
      />
      {error && <p className="text-red-600 mb-2">{error}</p>}
      <button
        onClick={handleLogin}
        className="w-full bg-primary text-white py-2 rounded hover:bg-blue-700"
      >
        Login
      </button>

      {/* Social login icons */}
      <div className="mt-6 text-center">
        <p className="text-gray-600 mb-2">Or login with</p>
        <div className="flex justify-center space-x-6 text-3xl">
          <FaGoogle
            onClick={() => handleSocialLogin("google")}
            className="cursor-pointer text-red-500 hover:scale-110 transition-transform"
            title="Login with Google"
          />
          <FaFacebook
            onClick={() => handleSocialLogin("facebook")}
            className="cursor-pointer text-primary hover:scale-110 transition-transform"
            title="Login with Facebook"
          />
        </div>
      </div>
    </div>
  );
}
