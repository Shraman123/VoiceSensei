export default function LanguageToggle({ language, onChange }) {
  return (
    <div className="mode-toggle">
      <button
        className={`mode-btn${language === "en" ? " active" : ""}`}
        onClick={() => onChange("en")}
      >
        🇬🇧 English
      </button>
      <button
        className={`mode-btn${language === "hi" ? " active" : ""}`}
        onClick={() => onChange("hi")}
      >
        🇮🇳 हिंदी
      </button>
    </div>
  );
}
