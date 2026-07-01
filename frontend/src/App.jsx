/**
 * VoiceSensei — App root
 */
import { useState, useRef, useEffect } from "react";
import MicButton from "./components/MicButton";
import ChatBubble from "./components/ChatBubble";
import ModeToggle from "./components/ModeToggle";
import SubjectSelector from "./components/SubjectSelector";
import UploadPDF from "./components/UploadPDF";
import SessionDrawer from "./components/SessionDrawer";
import LanguageToggle from "./components/LanguageToggle";
import MobileMenu from "./components/MobileMenu";
import AuthModal from "./components/AuthModal";
import ProgressPanel from "./components/ProgressPanel";
import useVoice from "./hooks/useVoice";
import useAuth from "./hooks/useAuth";

const API_URL = (import.meta.env.VITE_API_URL || "").replace(/\/$/, "") || "http://localhost:8000";

const WELCOME = {
  id: "welcome",
  type: "agent",
  text:
    "Namaste! I'm VoiceSensei — your AI exam tutor. " +
    "Tap the mic and ask me anything: Newton's laws, Indian Polity, organic chemistry. " +
    "Switch to Quiz mode and I'll quiz you after each answer. If you're struggling, I'll automatically simplify my explanation.",
  audioUrl: null,
};

function getOrCreateSessionId() {
  let id = localStorage.getItem("vs_session_id");
  if (!id) { id = crypto.randomUUID(); localStorage.setItem("vs_session_id", id); }
  return id;
}

let _msgId = 1;
const uid = () => String(_msgId++);

function dbRowToMessage(row) {
  return {
    id: uid(), type: row.role === "user" ? "user" : "agent",
    text: row.text, audioUrl: null,
    quizQuestion: row.quiz_question || null,
    isCorrect: row.is_correct === 1,
    isStruggling: row.is_struggling === 1,
    evaluationMode: row.is_correct !== null,
  };
}

export default function App() {
  const [messages, setMessages]       = useState([WELCOME]);
  const [mode, setMode]               = useState("study");
  const [subject, setSubject]         = useState("general");
  const [ragLoaded, setRagLoaded]     = useState(false);
  const [ragMeta, setRagMeta]         = useState(null);
  const [pendingQuiz, setPendingQuiz] = useState(null);
  const [language, setLanguage]       = useState("en");
  const [drawerOpen, setDrawerOpen]   = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [authOpen, setAuthOpen]       = useState(false);
  const [progressOpen, setProgressOpen] = useState(false);

  const { token, user, authHeader, register, login, logout } = useAuth(API_URL);
  const sessionId  = useRef(getOrCreateSessionId()).current;
  const chatEndRef = useRef(null);

  useEffect(() => {
    fetch(`${API_URL}/history/${sessionId}`, { headers: authHeader })
      .then((r) => r.json())
      .then((data) => {
        if (data.messages?.length > 0)
          setMessages([WELCOME, ...data.messages.map(dbRowToMessage)]);
      })
      .catch(() => {});
  }, [sessionId]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleModeChange = (m) => { setMode(m); setPendingQuiz(null); };

  const handleResult = (result) => {
    setMessages((prev) => [
      ...prev,
      { id: uid(), type: "user",  text: result.transcript || "(inaudible)", audioUrl: null },
      {
        id: uid(), type: "agent", text: result.response,
        audioUrl: result.audioUrl,
        quizQuestion: result.quiz_question || null,
        isCorrect: result.is_correct,
        isStruggling: result.is_struggling,
        evaluationMode: !!result.evaluationMode,
      },
    ]);

    if (result.evaluationMode) {
      if (!result.is_struggling) setPendingQuiz(null);
    } else if (result.quiz_question && mode === "quiz") {
      setPendingQuiz({ question: result.quiz_question, expectedAnswer: result.response });
    } else {
      setPendingQuiz(null);
    }
  };

  const handleSessionSwitch = (id) => { localStorage.setItem("vs_session_id", id); window.location.reload(); };
  const handleNewSession    = ()  => { localStorage.setItem("vs_session_id", crypto.randomUUID()); window.location.reload(); };

  const { isRecording, isProcessing, startRecording, stopRecording } = useVoice({
    apiUrl: API_URL, mode, subject, sessionId,
    pendingQuiz, language, authHeader,
    onResult: handleResult,
  });

  const getModeHint = () => {
    if (language === "hi") {
      if (mode === "quiz" && pendingQuiz) return "🎯 ऊपर के प्रश्न का उत्तर दें";
      if (mode === "quiz") return "📖 कोई विषय पूछें — मैं उत्तर दूंगा, फिर प्रश्न करूंगा";
      return "🎤 कोई भी परीक्षा प्रश्न पूछें";
    }
    if (mode === "quiz" && pendingQuiz) return "🎯 Answer the quiz question above";
    if (mode === "quiz") return "📖 Ask a topic — I'll answer, then quiz you";
    return "🎤 Ask any exam question";
  };

  return (
    <div className="app">
      <MobileMenu
        open={mobileMenuOpen} onClose={() => setMobileMenuOpen(false)}
        mode={mode} onModeChange={handleModeChange}
        subject={subject} onSubjectChange={setSubject}
        language={language} onLanguageChange={setLanguage}
        apiUrl={API_URL}
        onPdfLoaded={(meta) => { setRagLoaded(true); setRagMeta(meta); }}
        ragLoaded={ragLoaded} ragMeta={ragMeta}
      />

      <SessionDrawer
        open={drawerOpen} onClose={() => setDrawerOpen(false)}
        apiUrl={API_URL} authHeader={authHeader}
        currentSessionId={sessionId}
        onSwitch={handleSessionSwitch} onNew={handleNewSession}
      />

      <AuthModal
        open={authOpen} onClose={() => setAuthOpen(false)}
        onLogin={login} onRegister={register}
      />

      <ProgressPanel
        open={progressOpen} onClose={() => setProgressOpen(false)}
        apiUrl={API_URL} authHeader={authHeader}
      />

      {/* Sidebar */}
      <aside className="sidebar">
        <div className="logo">
          <span className="logo-icon">⚡</span>
          <span className="logo-text">VoiceSensei</span>
        </div>

        {/* User account */}
        <div className="sidebar-section">
          {user ? (
            <div className="user-card">
              <div className="user-avatar">{user.username[0].toUpperCase()}</div>
              <div className="user-info">
                <div className="user-name">{user.username}</div>
                <button className="user-signout" onClick={logout}>Sign out</button>
              </div>
              <button className="progress-btn" onClick={() => setProgressOpen(true)} title="Progress">📈</button>
            </div>
          ) : (
            <button className="signin-btn" onClick={() => setAuthOpen(true)}>
              👤 Sign in to track progress
            </button>
          )}
        </div>

        <div className="sidebar-section">
          <span className="section-label">Mode</span>
          <ModeToggle mode={mode} onChange={handleModeChange} />
        </div>

        <div className="sidebar-section">
          <span className="section-label">Language</span>
          <LanguageToggle language={language} onChange={setLanguage} />
        </div>

        <div className="sidebar-section">
          <span className="section-label">Subject</span>
          <SubjectSelector subject={subject} onChange={setSubject} />
        </div>

        <div className="sidebar-section">
          <span className="section-label">Study Material</span>
          <UploadPDF apiUrl={API_URL} onLoaded={(meta) => { setRagLoaded(true); setRagMeta(meta); }} />
          {ragLoaded && ragMeta && (
            <div className="rag-badge">✓ {ragMeta.pages} pages · {ragMeta.chunks} chunks indexed</div>
          )}
        </div>

        <div className="sidebar-footer">
          {mode === "quiz" && pendingQuiz && (
            <div className="quiz-indicator"><span className="quiz-dot" />Awaiting your answer…</div>
          )}
          <button className="history-btn" onClick={() => setDrawerOpen(true)}>🕐 Session History</button>
        </div>
      </aside>

      {/* Main */}
      <main className="main">
        <div className="mobile-topbar">
          <div className="logo">
            <span className="logo-icon">⚡</span>
            <span className="logo-text">VoiceSensei</span>
          </div>
          <div style={{ display: "flex", gap: 8 }}>
            {user && <button className="mobile-icon-btn" onClick={() => setProgressOpen(true)}>📈</button>}
            {!user && <button className="mobile-icon-btn" onClick={() => setAuthOpen(true)}>👤</button>}
            <button className="mobile-icon-btn" onClick={() => setDrawerOpen(true)}>🕐</button>
            <button className="mobile-icon-btn" onClick={() => setMobileMenuOpen(true)}>☰</button>
          </div>
        </div>

        <div className="chat-container">
          {messages.map((msg) => <ChatBubble key={msg.id} message={msg} />)}
          {isProcessing && <div className="thinking-bubble"><span /><span /><span /></div>}
          <div ref={chatEndRef} />
        </div>

        <div className="input-bar">
          <div className="mode-hint">{getModeHint()}</div>
          <MicButton
            isRecording={isRecording} isProcessing={isProcessing}
            onStart={startRecording} onStop={stopRecording}
          />
        </div>
      </main>
    </div>
  );
}
