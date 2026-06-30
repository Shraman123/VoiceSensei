/**
 * ProgressPanel — slide-in dashboard showing user's study stats.
 */
import { useEffect, useState } from "react";

const SUBJECT_EMOJI = { jee: "⚗️", neet: "🧬", upsc: "🏛️", ssc: "📊", general: "📚" };

export default function ProgressPanel({ open, onClose, apiUrl, authHeader }) {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!open) return;
    setLoading(true);
    fetch(`${apiUrl}/progress`, { headers: authHeader })
      .then((r) => r.json())
      .then(setStats)
      .catch(() => setStats(null))
      .finally(() => setLoading(false));
  }, [open]);

  return (
    <>
      {open && <div className="drawer-overlay" onClick={onClose} />}
      <div className={`session-drawer${open ? " open" : ""}`}>
        <div className="drawer-header">
          <span className="drawer-title">📈 Progress</span>
          <button className="drawer-close" onClick={onClose}>✕</button>
        </div>

        {loading && <p className="drawer-hint">Loading…</p>}

        {!loading && stats && (
          <div className="progress-body">
            {/* Streak */}
            <div className="progress-streak">
              <span className="streak-flame">🔥</span>
              <div>
                <div className="streak-count">{stats.streak_days} day{stats.streak_days !== 1 ? "s" : ""}</div>
                <div className="streak-label">Study Streak</div>
              </div>
            </div>

            {/* Stat cards */}
            <div className="stat-grid">
              <div className="stat-card">
                <div className="stat-value">{stats.total_questions}</div>
                <div className="stat-label">Questions Asked</div>
              </div>
              <div className="stat-card">
                <div className="stat-value">{stats.total_sessions}</div>
                <div className="stat-label">Sessions</div>
              </div>
              <div className="stat-card">
                <div className="stat-value">{stats.quiz_accuracy}%</div>
                <div className="stat-label">Quiz Accuracy</div>
              </div>
              <div className="stat-card">
                <div className="stat-value">{stats.avg_score > 0 ? stats.avg_score : "—"}</div>
                <div className="stat-label">Avg Score /10</div>
              </div>
            </div>

            {/* Quiz bar */}
            {stats.quiz_total > 0 && (
              <div className="progress-section">
                <div className="section-label">Quiz Performance</div>
                <div className="quiz-bar-track">
                  <div
                    className="quiz-bar-fill"
                    style={{ width: `${stats.quiz_accuracy}%` }}
                  />
                </div>
                <div className="quiz-bar-labels">
                  <span>{stats.quiz_correct} correct</span>
                  <span>{stats.quiz_total - stats.quiz_correct} incorrect</span>
                </div>
              </div>
            )}

            {/* Subjects */}
            {stats.subjects.length > 0 && (
              <div className="progress-section">
                <div className="section-label">Subjects Studied</div>
                {stats.subjects.map((s) => (
                  <div key={s.subject} className="subject-row">
                    <span className="subject-row-name">
                      {SUBJECT_EMOJI[s.subject] || "📖"} {s.subject}
                    </span>
                    <span className="subject-row-count">{s.count} questions</span>
                  </div>
                ))}
              </div>
            )}

            {stats.total_questions === 0 && (
              <p className="drawer-hint">Start studying to see your progress here!</p>
            )}
          </div>
        )}

        {!loading && !stats && (
          <p className="drawer-hint">Could not load progress.</p>
        )}
      </div>
    </>
  );
}
