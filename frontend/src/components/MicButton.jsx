/**
 * MicButton — The signature orb.
 * Click to toggle recording. Rings radiate outward while active.
 */
export default function MicButton({ isRecording, isProcessing, onStart, onStop }) {
  const handleClick = () => {
    if (isProcessing) return;
    if (isRecording) onStop();
    else onStart();
  };

  const label = isProcessing ? "Processing…" : isRecording ? "Tap to send" : "Tap to speak";

  return (
    <div className="mic-wrapper">
      {isRecording && (
        <>
          <div className="mic-ring ring-1" />
          <div className="mic-ring ring-2" />
          <div className="mic-ring ring-3" />
        </>
      )}

      <button
        className={`mic-btn${isRecording ? " recording" : ""}${isProcessing ? " processing" : ""}`}
        onClick={handleClick}
        disabled={isProcessing}
        aria-label={label}
      >
        {isProcessing ? (
          <div className="spinner" />
        ) : isRecording ? (
          <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <rect x="6" y="6" width="12" height="12" rx="2" fill="white" />
          </svg>
        ) : (
          <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <rect x="9" y="2" width="6" height="11" rx="3" strokeWidth="2" />
            <path d="M5 10v1a7 7 0 0 0 14 0v-1" strokeWidth="2" />
            <line x1="12" y1="18" x2="12" y2="22" strokeWidth="2" />
            <line x1="8" y1="22" x2="16" y2="22" strokeWidth="2" />
          </svg>
        )}
      </button>

      <span className="mic-label">{label}</span>
    </div>
  );
}
