import { API_URL } from "../config";
import { useState } from "react";
import axios from "axios";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { useUser } from "../UserContext";
import SocialLogin from "../components/SocialLogin";

const API_BASE = `${API_URL}/api/auth/login/`;

type LoginState = { from?: string; registered?: string } | null;

export default function Login() {
  const location = useLocation();
  const state = location.state as LoginState;
  // Set when arriving here straight after signing up
  const registered = state?.registered;

  const [username, setUsername] = useState(registered ?? "");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const navigate = useNavigate();
  const { refreshUser } = useUser();

  // Redirect back to where the user came from, or home
  const from = state?.from || "/";

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const res = await axios.post(API_BASE, { username, password });
      localStorage.setItem("token", res.data.token);
      await refreshUser();
      navigate(from, { replace: true });
    } catch (err) {
      setError(
        (axios.isAxiosError(err) && err.response?.data?.error) || "Login failed."
      );
    } finally {
      setLoading(false);
    }
  };


  return (
    <div className="mx-auto w-full max-w-sm px-4 py-16">
      <h1 className="page-title">Log in</h1>
      <p className="page-subtitle">Welcome back to AgroSmart.</p>

      {registered && (
        <p className="alert-success mt-6">
          Account created. Log in with your new password to continue.
        </p>
      )}

      <form onSubmit={handleLogin} className="card mt-8 space-y-4 p-6">
        <div>
          <label htmlFor="username" className="label">Username</label>
          <input
            id="username"
            type="text"
            autoComplete="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="input"
            required
          />
        </div>
        <div>
          <label htmlFor="password" className="label">Password</label>
          <input
            id="password"
            autoFocus={!!registered}
            type="password"
            autoComplete="current-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="input"
            required
          />
        </div>
        {error && <p className="alert-error">{error}</p>}
        <button type="submit" disabled={loading} className="btn-primary w-full py-2.5">
          {loading ? "Logging in…" : "Log in"}
        </button>

      </form>

      <SocialLogin redirectTo={from} label="or log in with" />

      <p className="mt-6 text-center text-sm text-stone-600">
        Don't have an account?{" "}
        <Link to="/register" className="link">Sign up</Link>
      </p>
    </div>
  );
}
