"""
SQLite persistence for VoiceSensei.
Tables: users, messages, quiz_scores
"""
import aiosqlite
from pathlib import Path

DB_PATH = Path(__file__).parent / "voicesensei.db"


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                username     TEXT NOT NULL UNIQUE,
                email        TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at   DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id    TEXT NOT NULL,
                user_id       INTEGER REFERENCES users(id),
                role          TEXT NOT NULL,
                text          TEXT NOT NULL,
                mode          TEXT DEFAULT 'study',
                subject       TEXT DEFAULT 'general',
                is_correct    INTEGER DEFAULT NULL,
                is_struggling INTEGER DEFAULT NULL,
                quiz_question TEXT DEFAULT NULL,
                created_at    DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # migrate: add user_id column if it doesn't exist yet
        try:
            await db.execute("ALTER TABLE messages ADD COLUMN user_id INTEGER REFERENCES users(id)")
        except Exception:
            pass

        await db.execute("""
            CREATE TABLE IF NOT EXISTS quiz_scores (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    INTEGER NOT NULL REFERENCES users(id),
                session_id TEXT NOT NULL,
                subject    TEXT DEFAULT 'general',
                score      INTEGER DEFAULT 5,
                is_correct INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        await db.execute(
            "CREATE INDEX IF NOT EXISTS idx_session ON messages(session_id, created_at)"
        )
        await db.execute(
            "CREATE INDEX IF NOT EXISTS idx_user_msgs ON messages(user_id, created_at)"
        )
        await db.execute(
            "CREATE INDEX IF NOT EXISTS idx_quiz_user ON quiz_scores(user_id, created_at)"
        )
        await db.commit()


# ── User CRUD ──────────────────────────────────────────────────────────────────

async def create_user(username: str, email: str, password_hash: str) -> dict:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (username, email, password_hash),
        )
        await db.commit()
        async with db.execute("SELECT * FROM users WHERE id = ?", (cursor.lastrowid,)) as c:
            row = await c.fetchone()
    return dict(row)


async def get_user_by_email(email: str) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE email = ?", (email,)) as c:
            row = await c.fetchone()
    return dict(row) if row else None


async def get_user_by_id(user_id: int) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE id = ?", (user_id,)) as c:
            row = await c.fetchone()
    return dict(row) if row else None


# ── Message persistence ────────────────────────────────────────────────────────

async def save_turn(
    session_id: str,
    user_text: str,
    agent_text: str,
    mode: str = "study",
    subject: str = "general",
    is_correct: bool = None,
    is_struggling: bool = None,
    quiz_question: str = None,
    user_id: int = None,
):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT INTO messages
               (session_id, user_id, role, text, mode, subject)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (session_id, user_id, "user", user_text, mode, subject),
        )
        await db.execute(
            """INSERT INTO messages
               (session_id, user_id, role, text, mode, subject, is_correct, is_struggling, quiz_question)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                session_id, user_id, "agent", agent_text, mode, subject,
                int(is_correct) if is_correct is not None else None,
                int(is_struggling) if is_struggling is not None else None,
                quiz_question,
            ),
        )
        await db.commit()


async def save_quiz_score(
    user_id: int,
    session_id: str,
    subject: str,
    score: int,
    is_correct: bool,
):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT INTO quiz_scores (user_id, session_id, subject, score, is_correct)
               VALUES (?, ?, ?, ?, ?)""",
            (user_id, session_id, subject, score, int(is_correct)),
        )
        await db.commit()


# ── History ────────────────────────────────────────────────────────────────────

async def get_history(session_id: str) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM messages WHERE session_id = ? ORDER BY created_at ASC",
            (session_id,),
        ) as cursor:
            rows = await cursor.fetchall()
    return [dict(r) for r in rows]


async def get_sessions(user_id: int = None) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        if user_id:
            query = """
                SELECT session_id, MAX(created_at) AS last_active,
                       COUNT(*) AS message_count, MAX(subject) AS subject
                FROM messages WHERE user_id = ?
                GROUP BY session_id ORDER BY last_active DESC LIMIT 20
            """
            args = (user_id,)
        else:
            query = """
                SELECT session_id, MAX(created_at) AS last_active,
                       COUNT(*) AS message_count, MAX(subject) AS subject
                FROM messages
                GROUP BY session_id ORDER BY last_active DESC LIMIT 20
            """
            args = ()
        async with db.execute(query, args) as cursor:
            rows = await cursor.fetchall()
    return [dict(r) for r in rows]


# ── Progress stats ─────────────────────────────────────────────────────────────

async def get_progress(user_id: int) -> dict:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row

        # Total questions asked (user messages)
        async with db.execute(
            "SELECT COUNT(*) AS total FROM messages WHERE user_id=? AND role='user'",
            (user_id,),
        ) as c:
            total_questions = (await c.fetchone())["total"]

        # Quiz stats
        async with db.execute(
            """SELECT COUNT(*) AS total,
                      SUM(is_correct) AS correct,
                      AVG(score) AS avg_score
               FROM quiz_scores WHERE user_id=?""",
            (user_id,),
        ) as c:
            row = await c.fetchone()
            quiz_total = row["total"] or 0
            quiz_correct = int(row["correct"] or 0)
            avg_score = round(float(row["avg_score"] or 0), 1)

        # Subject breakdown
        async with db.execute(
            """SELECT subject, COUNT(*) AS count
               FROM messages WHERE user_id=? AND role='user'
               GROUP BY subject ORDER BY count DESC""",
            (user_id,),
        ) as c:
            subjects = [dict(r) for r in await c.fetchall()]

        # Study streak (distinct days with activity)
        async with db.execute(
            """SELECT DATE(created_at) AS day
               FROM messages WHERE user_id=? AND role='user'
               GROUP BY day ORDER BY day DESC""",
            (user_id,),
        ) as c:
            days = [r["day"] for r in await c.fetchall()]

        streak = _calc_streak(days)

        # Total sessions
        async with db.execute(
            "SELECT COUNT(DISTINCT session_id) AS s FROM messages WHERE user_id=?",
            (user_id,),
        ) as c:
            total_sessions = (await c.fetchone())["s"]

    return {
        "total_questions": total_questions,
        "total_sessions": total_sessions,
        "quiz_total": quiz_total,
        "quiz_correct": quiz_correct,
        "quiz_accuracy": round(quiz_correct / quiz_total * 100) if quiz_total else 0,
        "avg_score": avg_score,
        "streak_days": streak,
        "subjects": subjects,
    }


def _calc_streak(days: list[str]) -> int:
    """Count consecutive calendar days ending today/yesterday."""
    if not days:
        return 0
    from datetime import date, timedelta
    today = date.today()
    streak = 0
    expected = today
    for day_str in days:
        d = date.fromisoformat(day_str)
        if d == expected or d == expected - timedelta(days=1) and streak == 0:
            streak += 1
            expected = d - timedelta(days=1)
        elif d < expected:
            break
    return streak
