import { useState, useEffect, useRef } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { FaUserCircle } from "react-icons/fa";
import axios from "axios";

const translateText = async (text: string, source: string, target: string) => {
  const res = await fetch("https://libretranslate.com/translate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      q: text,
      source,
      target,
      format: "text",
    }),
  });
  const data = await res.json();
  return data.translatedText;
};

const Navbar = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [language, setLanguage] = useState("en");
  const [translatedMenu, setTranslatedMenu] = useState({
    home: "Home",
    marketplace: "Marketplace",
    recommendations: "Recommendations",
    disease: "Disease Detection",
    education: "Learn more",
    login: "Login",
    signup: "Sign Up",
    logout: "Logout",
    profile: "Profile",
  });

  // State for user and dropdown
  const [user, setUser] = useState<{
    id_number: any;
    phone_number: any;
    last_name: any;
    first_name: any;
    username: string;
    email: string;
  } | null>(null);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Fetch user profile from backend using token on mount
  useEffect(() => {
    const fetchUser = async () => {
      const token = localStorage.getItem("token");
      if (!token) return;

      try {
        const res = await axios.get("http://localhost:8000/api/auth/profile/", {
          headers: { Authorization: `Token ${token}` },
        });
        setUser(res.data);
        localStorage.setItem("user", JSON.stringify(res.data)); // cache user
      } catch {
        setUser(null);
        localStorage.removeItem("token");
        localStorage.removeItem("user");
      }
    };

    fetchUser();
  }, []);

  // Close dropdown on outside click
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        setDropdownOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  // Language switcher toggling English <-> Swahili
  const switchLanguage = async () => {
    const target = language === "en" ? "sw" : "en";
    const texts = [
      "Home",
      "Marketplace",
      "Recommendations",
      "Disease Detection",
      "Learn more",
      "Login",
      "Sign Up",
      "Logout",
      "Profile",
    ];

    const translated = await Promise.all(
      texts.map((t) => translateText(t, language, target))
    );

    setTranslatedMenu({
      home: translated[0],
      marketplace: translated[1],
      recommendations: translated[2],
      disease: translated[3],
      education: translated[4],
      login: translated[5],
      signup: translated[6],
      logout: translated[7],
      profile: translated[8],
    });

    setLanguage(target);
  };

  const isActive = (path: string) => location.pathname === path;

  // Logout handler clears localStorage and state
  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    setUser(null);
    setDropdownOpen(false);
    navigate("/");
  };

  return (
    <nav className="flex items-center justify-between p-4 bg-white shadow-md">
      {/* Logo */}
      <div
        className="text-2xl font-bold cursor-pointer"
        onClick={() => navigate("/")}
      >
        <span className="text-black">Agro</span>
        <span className="text-primary">Smart</span>
      </div>

      {/* Menu Items */}
      <div className="hidden md:flex gap-6 text-gray-700">
        <Link
          to="/"
          className={`hover:text-primary transition duration-300 ${
            isActive("/") ? "font-semibold text-green-700" : ""
          }`}
        >
          {translatedMenu.home}
        </Link>
        <Link
          to="/market"
          className={`hover:text-primary transition duration-300 ${
            isActive("/market") ? "font-semibold text-green-700" : ""
          }`}
        >
          {translatedMenu.marketplace}
        </Link>
        <Link
          to="/crop_recommendation"
          className={`hover:text-primary transition duration-300 ${
            isActive("/crop_recommendation")
              ? "font-semibold text-green-700"
              : ""
          }`}
        >
          {translatedMenu.recommendations}
        </Link>
        <Link
          to="/disease_detection"
          className={`hover:text-green-600 transition duration-300 ${
            isActive("/disease_detection") ? "font-semibold text-green-700" : ""
          }`}
        >
          {translatedMenu.disease}
        </Link>
        <Link
          to="/education"
          className={`hover:text-green-600 transition duration-300 ${
            isActive("/education") ? "font-semibold text-green-700" : ""
          }`}
        >
          {translatedMenu.education}
        </Link>
      </div>

      {/* Right Section */}
      <div className="flex items-center gap-4 relative">
        <button
          onClick={switchLanguage}
          title="Switch Language"
          className="px-2 py-1 border rounded hover:bg-green-100"
        >
          {language.toUpperCase()}
        </button>

        {!user ? (
          <>
            <Link
              to="/login"
              className={`px-4 py-1 rounded transition duration-300 ${
                isActive("/login")
                  ? "bg-primary text-white"
                  : "text-gray-700 hover:text-green-600"
              }`}
            >
              {translatedMenu.login}
            </Link>

            <Link
              to="/register"
              className={`px-4 py-2 rounded transition duration-300 ${
                isActive("/register")
                  ? "bg-primary text-white"
                  : "text-gray-700 hover:text-green-600"
              }`}
            >
              {translatedMenu.signup}
            </Link>
          </>
        ) : (
          <div ref={dropdownRef} className="relative">
            <FaUserCircle
              className="text-3xl cursor-pointer text-green-700 hover:text-green-900"
              onClick={() => setDropdownOpen((open) => !open)}
              title="User Profile"
            />

            {dropdownOpen && (
              <div className="absolute right-0 mt-2 w-80 bg-white border rounded-lg shadow-lg z-50 p-5">
                <div className="border-b pb-4 mb-4 select-text">
                  <p className="text-xl font-semibold text-gray-800">
                    {user.username}
                  </p>
                  <p className="text-sm text-gray-600 truncate">{user.email}</p>
                </div>
                <div className="space-y-3 text-gray-700">
                  {user.first_name && (
                    <div>
                      <span className="font-medium">First Name:</span>{" "}
                      {user.first_name}
                    </div>
                  )}
                  {user.last_name && (
                    <div>
                      <span className="font-medium">Last Name:</span>{" "}
                      {user.last_name}
                    </div>
                  )}
                  {user.phone_number && (
                    <div>
                      <span className="font-medium">Phone Number:</span>{" "}
                      {user.phone_number}
                    </div>
                  )}
                  {user.id_number && (
                    <div>
                      <span className="font-medium">ID Number:</span>{" "}
                      {user.id_number}
                    </div>
                  )}
                </div>
                <button
                  onClick={handleLogout}
                  className="mt-6 w-full text-center px-4 py-2 rounded bg-primary text-white hover:bg-primary/80 transition"
                >
                  {translatedMenu.logout}
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
