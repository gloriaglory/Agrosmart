import { useTranslation } from "react-i18next";

export default function LanguageSwitcher() {
  const { i18n } = useTranslation();
  return (
    <div className="flex space-x-2">
      <button onClick={() => i18n.changeLanguage("en")} className="text-sm">EN</button>
      <button onClick={() => i18n.changeLanguage("sw")} className="text-sm">SW</button>
    </div>
  );
}
