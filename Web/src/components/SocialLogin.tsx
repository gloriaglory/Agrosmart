import { useEffect, useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import { API_URL } from "../config";
import { useUser } from "../UserContext";

// Minimal typings for the Google Identity Services and Facebook SDK globals we use
type GoogleTokenResponse = { access_token?: string; error?: string };
type GoogleTokenClient = { requestAccessToken: () => void };
type FacebookLoginResponse = { authResponse?: { accessToken: string } | null };

declare global {
  interface Window {
    google?: {
      accounts: {
        oauth2: {
          initTokenClient: (config: {
            client_id: string;
            scope: string;
            callback: (response: GoogleTokenResponse) => void;
            error_callback?: (error: { type: string }) => void;
          }) => GoogleTokenClient;
        };
      };
    };
    FB?: {
      init: (options: { appId: string; cookie: boolean; xfbml: boolean; version: string }) => void;
      login: (callback: (response: FacebookLoginResponse) => void, options: { scope: string }) => void;
    };
  }
}

type Provider = "google" | "facebook";
type SocialConfig = { google_client_id: string | null; facebook_app_id: string | null };

const loadScript = (src: string, id: string) =>
  new Promise<void>((resolve, reject) => {
    if (document.getElementById(id)) return resolve();
    const script = document.createElement("script");
    script.id = id;
    script.src = src;
    script.async = true;
    script.onload = () => resolve();
    script.onerror = () => reject(new Error(`Could not load ${src}`));
    document.body.appendChild(script);
  });

type Props = {
  // Where to go after a successful login
  redirectTo: string;
  label: string;
};

// "Continue with Google / Facebook" buttons. Hidden until keys are set in the backend .env.
export default function SocialLogin({ redirectTo, label }: Props) {
  const [config, setConfig] = useState<SocialConfig | null>(null);
  const [busy, setBusy] = useState<Provider | null>(null);
  const [error, setError] = useState<string | null>(null);
  const { refreshUser } = useUser();
  const navigate = useNavigate();

  useEffect(() => {
    axios
      .get<SocialConfig>(`${API_URL}/api/auth/social/config/`)
      .then((res) => setConfig(res.data))
      .catch(() => setConfig({ google_client_id: null, facebook_app_id: null }));
  }, []);

  // Preload the SDKs so the popup opens straight from the click (browsers block delayed popups)
  useEffect(() => {
    if (config?.google_client_id) {
      loadScript("https://accounts.google.com/gsi/client", "google-gsi").catch(() => {});
    }
    if (config?.facebook_app_id) {
      loadScript("https://connect.facebook.net/en_US/sdk.js", "facebook-sdk")
        .then(() =>
          window.FB?.init({ appId: config.facebook_app_id!, cookie: false, xfbml: false, version: "v21.0" })
        )
        .catch(() => {});
    }
  }, [config]);

  const finishLogin = async (provider: Provider, accessToken: string) => {
    try {
      const res = await axios.post(`${API_URL}/api/auth/${provider}/`, { access_token: accessToken });
      localStorage.setItem("token", res.data.token);
      await refreshUser();
      navigate(redirectTo, { replace: true });
    } catch (err) {
      const data = axios.isAxiosError(err) ? err.response?.data : null;
      const message =
        (data && (data.error || data.non_field_errors?.join(" ") || data.detail)) ||
        "Sign-in failed. Please try again.";
      setError(
        String(message).includes("already registered")
          ? "An account with this email already exists. Log in with your username and password instead."
          : String(message)
      );
    } finally {
      setBusy(null);
    }
  };

  const loginWithGoogle = () => {
    setError(null);
    if (!window.google || !config?.google_client_id) {
      setError("Google sign-in is still loading. Try again in a moment.");
      return;
    }
    setBusy("google");
    const client = window.google.accounts.oauth2.initTokenClient({
      client_id: config.google_client_id,
      scope: "openid email profile",
      callback: (response) => {
        if (response.access_token) finishLogin("google", response.access_token);
        else {
          setBusy(null);
          if (response.error) setError("Google sign-in was cancelled.");
        }
      },
      error_callback: () => {
        setBusy(null);
        setError("Google sign-in was cancelled.");
      },
    });
    client.requestAccessToken();
  };

  const loginWithFacebook = () => {
    setError(null);
    if (!window.FB) {
      setError("Facebook sign-in is still loading. Try again in a moment.");
      return;
    }
    setBusy("facebook");
    window.FB.login(
      (response) => {
        const token = response.authResponse?.accessToken;
        if (token) finishLogin("facebook", token);
        else {
          setBusy(null);
          setError("Facebook sign-in was cancelled.");
        }
      },
      { scope: "email,public_profile" }
    );
  };

  if (!config || (!config.google_client_id && !config.facebook_app_id)) return null;

  const buttons = [
    config.google_client_id && { provider: "google" as const, name: "Google", onClick: loginWithGoogle },
    config.facebook_app_id && { provider: "facebook" as const, name: "Facebook", onClick: loginWithFacebook },
  ].filter(Boolean) as { provider: Provider; name: string; onClick: () => void }[];

  return (
    <div>
      <div className="my-4 flex items-center gap-3 text-xs text-stone-400">
        <div className="h-px flex-1 bg-stone-200" />
        {label}
        <div className="h-px flex-1 bg-stone-200" />
      </div>
      <div className={`grid gap-2 ${buttons.length > 1 ? "grid-cols-2" : "grid-cols-1"}`}>
        {buttons.map((b) => (
          <button
            key={b.provider}
            type="button"
            onClick={b.onClick}
            disabled={busy !== null}
            className="btn-secondary"
          >
            {busy === b.provider ? "Connecting…" : b.name}
          </button>
        ))}
      </div>
      {error && <p className="alert-error mt-3">{error}</p>}
    </div>
  );
}
