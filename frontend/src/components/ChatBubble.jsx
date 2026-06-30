/**
 * ChatBubble — renders a single message in the conversation.
 * Supports: study answers, quiz questions, correct/struggling evaluation states.
 */
import { useRef, useState } from "react";

export default function ChatBubble({ message }) {
  const { type, text, audioUrl, quizQuestion, isCorrect, isStruggling, evaluationMode } = message;
  const isAgent = type === "agent";
  const audioRef = useRef(null);
  const [playing, setPlaying] = useState(false);

  const togglePlay = () => {
    if (!audioRef.current) return;
    if (playing) { audioRef.current.pause(); setPlaying(false); }
    else { audioRef.current.play(); setPlaying(true); }
  };

  let bubbleClass = isAgent ? "agent-bubble" : "user-bubble";
  if (evaluationMode && isStruggling) bubbleClass += " is-struggling";
  if (evaluationMode && isCorrect && !isStruggling) bubbleClass += " is-correct";

  return (
    <div className={`bubble-row ${isAgent ? "agent" : "user"}`}>
      <div className={`bubble-avatar ${isAgent ? "agent-av" : "user-av"}`}>
        {isAgent ? "⚡" : "👤"}
      </div>

      <div>
        <div className={`bubble ${bubbleClass}`}>
          {evaluationMode && isStruggling && (
            <div><span className="struggle-tag">🔄 Struggle Detector</span></div>
          )}
          {evaluationMode && isCorrect && !isStruggling && (
            <div><span className="correct-tag">✓ Correct</span></div>
          )}
          {quizQuestion && (
            <div><span className="quiz-tag">🎯 Quiz</span></div>
          )}

          <p style={{ whiteSpace: "pre-wrap" }}>{text}</p>

          {quizQuestion && (
            <p style={{
              marginTop: 12, paddingTop: 12,
              borderTop: "1px solid rgba(124,58,237,0.25)",
              color: "#A78BFA", fontStyle: "italic",
            }}>
              {quizQuestion}
            </p>
          )}

          {isAgent && audioUrl && (
            <>
              <audio ref={audioRef} src={audioUrl} onEnded={() => setPlaying(false)} onPause={() => setPlaying(false)} />
              <div className="bubble-meta">
                <button className="play-btn" onClick={togglePlay}>
                  {playing ? (
                    <>
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <rect x="6" y="4" width="4" height="16" rx="1" />
                        <rect x="14" y="4" width="4" height="16" rx="1" />
                      </svg>
                      Pause
                    </>
                  ) : (
                    <>
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <polygon points="5,3 19,12 5,21" />
                      </svg>
                      Replay
                    </>
                  )}
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
