/**
 * AuthModal — Login / Register slide-in panel.
 */
import { useState } from "react";

export default function AuthModal({ open, onClose, onLogin, onRegister }) {
  const [tab, setTab]         = useState("login");
  const [username, setUsername] = useState("");
  const [email, setEmail]     = useState("");
  const [password, setPassword] = useState("");
  const [error, setError]     = useState("");
  const [loading, setLoading] = useState(false);

  const reset = () => { setError(""); setUsername(""); setEmail(""); setPassword(""); };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      if (tab === "login") {
        await onLogin(email, password);
      } else {
        await onRegister(username, email, password);
      }
      reset();
      onClose();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (!open) return null;

  return (
    <>
      <div className="drawer-overlay" onClick={onClose} />
      <div className="auth-modal">
        <div className="drawer-header">
          <span className="drawer-title">{tab === "login" ? "Sign In" : "Create Account"}</span>
          <button className="drawer-close" onClick={onClose}>✕</button>
        </div>

        <div className="auth-tabs">
          <button className={`auth-tab${tab === "login" ? " active" : ""}`} onClick={() => { setTab("login"); setError(""); }}>Login</button>
          <button className={`auth-tab${tab === "register" ? " active" : ""}`} onClick={() => { setTab("register"); setError(""); }}>Register</button>
        </div>

        <form className="auth-form" onSubmit={handleSubmit}>
          {tab === "register" && (
            <div className="auth-field">
              <label>Username</label>
              <input
                type="text" value={username} required minLength={2}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Your name"
              />
            </div>
          )}
          <div className="auth-field">
            <label>Email</label>
            <input
              type="email" value={email} required
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@email.com"
            />
          </div>
          <div className="auth-field">
            <label>Password</label>
            <input
              type="password" value={password} required minLength={6}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
            />
          </div>

          {error && <p className="auth-error">{error}</p>}

          <button className="auth-submit" type="submit" disabled={loading}>
            {loading ? "Please wait…" : tab === "login" ? "Sign In" : "Create Account"}
          </button>
        </form>

        <p className="auth-footer">
          {tab === "login" ? "No account? " : "Already have one? "}
          <button className="auth-link" onClick={() => { setTab(tab === "login" ? "register" : "login"); setError(""); }}>
            {tab === "login" ? "Register" : "Sign in"}
          </button>
        </p>
      </div>
    </>
  );
}
