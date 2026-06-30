/**
 * VoiceSensei — App root
 * State machine:
 *   study mode:  speak → answer
 *   quiz mode:   speak → answer + quiz question → speak answer → evaluated (Struggle Detector)
 */
import { useState, useRef, useEffect } from "react";
import MicButton from "./components/MicButton";
import ChatBubble from "./components/ChatBubble";
import ModeToggle from "./components/ModeToggle";
import SubjectSelector from "./components/SubjectSelector";
import UploadPDF from "./components/UploadPDF";
import useVoice from "./hooks/useVoice";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const WELCOME = {
  id: "welcome",
  type: "agent",
  text:
    "Namaste! I'm VoiceSensei — your AI exam tutor. " +
    "Tap the mic and ask me anything: Newton's laws, Indian Polity, organic chemistry. " +
    "Switch to Quiz mode and I'll quiz you after each answer. If you're struggling, I'll automatically simplify my explanation.",
  audioUrl: null,
};

let _msgId = 1;
const uid = () => String(_msgId++);

export default function App() {
  const [messages, setMessages] = useState([WELCOME]);
  const [mode, setMode] = useState("study");
  const [subject, setSubject] = useState("general");
  const [ragLoaded, setRagLoaded] = useState(false);
  const [ragMeta, setRagMeta] = useState(null);
  const [pendingQuiz, setPendingQuiz] = useState(null);

  const sessionId = useRef(crypto.randomUUID()).current;
  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleModeChange = (m) => {
    setMode(m);
    setPendingQuiz(null);
  };

  const handleResult = (result) => {
    const userMsg = {
      id: uid(),
      type: "user",
      text: result.transcript || "(inaudible)",
      audioUrl: null,
    };

    const agentMsg = {
      id: uid(),
      type: "agent",
      text: result.response,
      audioUrl: result.audioUrl,
      quizQuestion: result.quiz_question || null,
      isCorrect: result.is_correct,
      isStruggling: result.is_struggling,
      evaluationMode: !!result.evaluationMode,
    };

    setMessages((prev) => [...prev, userMsg, agentMsg]);

    if (result.evaluationMode) {
      if (!result.is_struggling) setPendingQuiz(null);
      // if struggling, keep pendingQuiz so student gets another attempt
    } else if (result.quiz_question && mode === "quiz") {
      setPendingQuiz({
        question: result.quiz_question,
        expectedAnswer: result.response,
      });
    } else {
      setPendingQuiz(null);
    }
  };

  const { isRecording, isProcessing, startRecording, stopRecording } = useVoice({
    apiUrl: API_URL,
    mode,
    subject,
    sessionId,
    pendingQuiz,
    onResult: handleResult,
  });

  const getModeHint = () => {
    if (mode === "quiz" && pendingQuiz) return "🎯 Answer the quiz question above";
    if (mode === "quiz") return "📖 Ask a topic — I'll answer, then quiz you";
    return "🎤 Ask any exam question";
  };

  return (
    <div className="app">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="logo">
          <span className="logo-icon">⚡</span>
          <span className="logo-text">VoiceSensei</span>
        </div>

        <div className="sidebar-section">
          <span className="section-label">Mode</span>
          <ModeToggle mode={mode} onChange={handleModeChange} />
        </div>

        <div className="sidebar-section">
          <span className="section-label">Subject</span>
          <SubjectSelector subject={subject} onChange={setSubject} />
        </div>

        <div className="sidebar-section">
          <span className="section-label">Study Material</span>
          <UploadPDF
            apiUrl={API_URL}
            onLoaded={(meta) => {
              setRagLoaded(true);
              setRagMeta(meta);
            }}
          />
          {ragLoaded && ragMeta && (
            <div className="rag-badge">
              ✓ {ragMeta.pages} pages · {ragMeta.chunks} chunks indexed
            </div>
          )}
        </div>

        <div className="sidebar-footer">
          {mode === "quiz" && pendingQuiz && (
            <div className="quiz-indicator">
              <span className="quiz-dot" />
              Awaiting your answer…
            </div>
          )}
        </div>
      </aside>

      {/* Main */}
      <main className="main">
        <div className="chat-container">
          {messages.map((msg) => (
            <ChatBubble key={msg.id} message={msg} />
          ))}

          {isProcessing && (
            <div className="thinking-bubble">
              <span /><span /><span />
            </div>
          )}

          <div ref={chatEndRef} />
        </div>

        <div className="input-bar">
          <div className="mode-hint">{getModeHint()}</div>
          <MicButton
            isRecording={isRecording}
            isProcessing={isProcessing}
            onStart={startRecording}
            onStop={stopRecording}
          />
        </div>
      </main>
    </div>
  );
}
