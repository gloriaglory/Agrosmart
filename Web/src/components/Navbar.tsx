import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';

const translateText = async (text: string, source: string, target: string) => {
  const res = await fetch('https://libretranslate.com/translate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      q: text,
      source,
      target,
      format: 'text'
    })
  });
  const data = await res.json();
  return data.translatedText;
};

const Navbar = () => {
  const location = useLocation();
  const [language, setLanguage] = useState('en');
  const [translatedMenu, setTranslatedMenu] = useState({
    home: 'Home',
    marketplace: 'Marketplace',
    recommendations: 'Recommendations',
    disease: 'Disease Detection',
    login: 'Login',
    signup: 'Sign Up'
  });

  const switchLanguage = async () => {
    const target = language === 'en' ? 'sw' : 'en';
    const texts = ['Home', 'Marketplace', 'Recommendations', 'Disease Detection', 'Login', 'Sign Up'];

    const translated = await Promise.all(
      texts.map(t => translateText(t, language, target))
    );

    setTranslatedMenu({
      home: translated[0],
      marketplace: translated[1],
      recommendations: translated[2],
      disease: translated[3],
      login: translated[4],
      signup: translated[5]
    });

    setLanguage(target);
  };

  const isActive = (path: string) => location.pathname === path;

  return (
    <nav className="flex items-center justify-between p-4 bg-white shadow-md">
      {/* Logo */}
      <div className="text-2xl font-bold">
        <span className="text-black">Agro</span>
        <span className="text-green-600">Smart</span>
      </div>

      {/* Menu Items */}
      <div className="hidden md:flex gap-6 text-gray-700">
        <Link to="/" className="hover:text-green-600 transition duration-300">{translatedMenu.home}</Link>
        <Link to="/marketplace" className="hover:text-green-600 transition duration-300">{translatedMenu.marketplace}</Link>
        <Link to="/recommendations" className="hover:text-green-600 transition duration-300">{translatedMenu.recommendations}</Link>
        <Link to="/disease" className="hover:text-green-600 transition duration-300">{translatedMenu.disease}</Link>
      </div>

      {/* Right Section */}
      <div className="flex items-center gap-4">
        <button onClick={switchLanguage} title="Switch Language">
      
        </button>

        <Link
          to="/login"
          className={`px-4 py-1 rounded transition duration-300 ${
            isActive('/login')
              ? 'bg-green-700 text-white'
              : 'text-gray-700 hover:text-green-600'
          }`}
        >
          {translatedMenu.login}
        </Link>

        <Link
          to="/signup"
          className={`px-4 py-2 rounded transition duration-300 ${
            isActive('/signup')
              ? 'bg-green-700 text-white'
              : 'text-gray-700 hover:text-green-600'
          }`}
        >
          {translatedMenu.signup}
        </Link>
      </div>
    </nav>
  );
};

export default Navbar;
