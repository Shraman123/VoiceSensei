/**
 * SessionDrawer — slide-in panel showing past sessions.
 * Users can switch sessions or start a new one.
 */
import { useEffect, useState } from "react";

function formatDate(iso) {
  const d = new Date(iso + "Z");
  return d.toLocaleDateString("en-IN", {
    day: "numeric", month: "short", hour: "2-digit", minute: "2-digit",
  });
}

export default function SessionDrawer({ open, onClose, apiUrl, currentSessionId, onSwitch, onNew }) {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!open) return;
    setLoading(true);
    fetch(`${apiUrl}/sessions`)
      .then((r) => r.json())
      .then((d) => setSessions(d.sessions || []))
      .catch(() => setSessions([]))
      .finally(() => setLoading(false));
  }, [open, apiUrl]);

  return (
    <>
      {open && <div className="drawer-overlay" onClick={onClose} />}
      <div className={`session-drawer${open ? " open" : ""}`}>
        <div className="drawer-header">
          <span className="drawer-title">Session History</span>
          <button className="drawer-close" onClick={onClose}>✕</button>
        </div>

        <button className="new-session-btn" onClick={onNew}>
          + New Session
        </button>

        <div className="session-list">
          {loading && <p className="drawer-hint">Loading…</p>}
          {!loading && sessions.length === 0 && (
            <p className="drawer-hint">No sessions yet.</p>
          )}
          {sessions.map((s) => (
            <button
              key={s.session_id}
              className={`session-item${s.session_id === currentSessionId ? " active" : ""}`}
              onClick={() => s.session_id !== currentSessionId && onSwitch(s.session_id)}
            >
              <div className="session-item-top">
                <span className="session-subject">{s.subject || "general"}</span>
                <span className="session-count">{s.message_count} msgs</span>
              </div>
              <div className="session-date">{formatDate(s.last_active)}</div>
              {s.session_id === currentSessionId && (
                <div className="session-current-badge">Current</div>
              )}
            </button>
          ))}
        </div>
      </div>
    </>
  );
}
