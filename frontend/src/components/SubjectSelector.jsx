const SUBJECTS = [
  { id: "general", label: "General" },
  { id: "jee",     label: "JEE" },
  { id: "neet",    label: "NEET" },
  { id: "upsc",    label: "UPSC" },
  { id: "ssc",     label: "SSC" },
];

export default function SubjectSelector({ subject, onChange }) {
  return (
    <div className="subject-grid">
      {SUBJECTS.map((s) => (
        <button
          key={s.id}
          className={`subject-btn${subject === s.id ? " active" : ""}`}
          onClick={() => onChange(s.id)}
        >
          {s.label}
        </button>
      ))}
    </div>
  );
}
