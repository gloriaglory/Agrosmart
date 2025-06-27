import { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import { FaGoogle, FaFacebook } from "react-icons/fa";

const API_BASE = "http://localhost:8000/api/auth/register/";

export default function Signup() {
  const [form, setForm] = useState({
    username: "",
    email: "",
    password: "",
    password2: "",
    first_name: "",
    last_name: "",
    phone_number: "",
    id_number: ""
  });
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSignup = async () => {
    setError(null);
    try {
      const res = await axios.post(API_BASE, form);
      localStorage.setItem("token", res.data.token);
      localStorage.setItem("user", JSON.stringify(res.data.user)); // Save user info
      alert("Signup successful");
      navigate("/login");
    } catch (err: any) {
      if (err.response?.data) {
        const errors = err.response.data;
        const messages = Object.values(errors).flat().join(" ");
        setError(messages);
      } else {
        setError("Signup failed. Please try again.");
      }
    }
  };

  const handleSocialSignup = (provider: "google" | "facebook") => {
    window.location.href = `http://localhost:8000/api/auth/${provider}/`;
  };

  return (
    <div className="max-w-3xl mx-auto mt-10 bg-white p-6 rounded shadow">
      <h2 className="text-2xl font-bold mb-6 text-center">Sign Up</h2>

      {/* Use grid with 2 columns and gap */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <input
          type="text"
          name="username"
          placeholder="Username"
          value={form.username}
          onChange={handleChange}
          className="w-full p-3 border rounded"
        />
        <input
          type="email"
          name="email"
          placeholder="Email"
          value={form.email}
          onChange={handleChange}
          className="w-full p-3 border rounded"
        />
        <input
          type="password"
          name="password"
          placeholder="Password"
          value={form.password}
          onChange={handleChange}
          className="w-full p-3 border rounded"
        />
        <input
          type="password"
          name="password2"
          placeholder="Confirm Password"
          value={form.password2}
          onChange={handleChange}
          className="w-full p-3 border rounded"
        />
        <input
          type="text"
          name="first_name"
          placeholder="First Name (optional)"
          value={form.first_name}
          onChange={handleChange}
          className="w-full p-3 border rounded"
        />
        <input
          type="text"
          name="last_name"
          placeholder="Last Name (optional)"
          value={form.last_name}
          onChange={handleChange}
          className="w-full p-3 border rounded"
        />
        <input
          type="text"
          name="phone_number"
          placeholder="Phone Number (optional)"
          value={form.phone_number}
          onChange={handleChange}
          className="w-full p-3 border rounded"
        />
        <input
          type="text"
          name="id_number"
          placeholder="ID Number (optional)"
          value={form.id_number}
          onChange={handleChange}
          className="w-full p-3 border rounded"
        />
      </div>

      {error && <p className="text-red-600 mb-4 text-center">{error}</p>}

      <button
        onClick={handleSignup}
        className="w-full bg-green-600 text-white py-3 rounded hover:bg-green-700 transition"
      >
        Sign Up
      </button>

      {/* Social signup icons */}
      <div className="mt-8 text-center">
        <p className="text-gray-600 mb-3">Or sign up with</p>
        <div className="flex justify-center space-x-8 text-4xl">
          <FaGoogle
            aria-label="Sign up with Google"
            onClick={() => handleSocialSignup("google")}
            className="cursor-pointer text-red-500 hover:scale-110 transition-transform"
            title="Sign up with Google"
          />
          <FaFacebook
            aria-label="Sign up with Facebook"
            onClick={() => handleSocialSignup("facebook")}
            className="cursor-pointer text-blue-600 hover:scale-110 transition-transform"
            title="Sign up with Facebook"
          />
        </div>
      </div>
    </div>
  );
}
