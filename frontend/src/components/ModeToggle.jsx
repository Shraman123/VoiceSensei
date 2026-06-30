export default function ModeToggle({ mode, onChange }) {
  return (
    <div className="mode-toggle">
      <button className={`mode-btn${mode === "study" ? " active" : ""}`} onClick={() => onChange("study")}>
        📖 Study
      </button>
      <button className={`mode-btn${mode === "quiz" ? " active" : ""}`} onClick={() => onChange("quiz")}>
        🎯 Quiz
      </button>
    </div>
  );
}
