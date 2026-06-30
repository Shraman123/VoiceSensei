"""
SQLite persistence for VoiceSensei chat history.
DB file: voicesensei.db (auto-created next to main.py)
"""
import aiosqlite
from pathlib import Path

DB_PATH = Path(__file__).parent / "voicesensei.db"


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role      TEXT NOT NULL,      -- 'user' | 'agent'
                text      TEXT NOT NULL,
                mode      TEXT DEFAULT 'study',
                subject   TEXT DEFAULT 'general',
                is_correct    INTEGER DEFAULT NULL,
                is_struggling INTEGER DEFAULT NULL,
                quiz_question TEXT DEFAULT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute(
            "CREATE INDEX IF NOT EXISTS idx_session ON messages(session_id, created_at)"
        )
        await db.commit()


async def save_turn(
    session_id: str,
    user_text: str,
    agent_text: str,
    mode: str = "study",
    subject: str = "general",
    is_correct: bool = None,
    is_struggling: bool = None,
    quiz_question: str = None,
):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO messages (session_id, role, text, mode, subject) VALUES (?, ?, ?, ?, ?)",
            (session_id, "user", user_text, mode, subject),
        )
        await db.execute(
            """INSERT INTO messages
               (session_id, role, text, mode, subject, is_correct, is_struggling, quiz_question)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                session_id, "agent", agent_text, mode, subject,
                int(is_correct) if is_correct is not None else None,
                int(is_struggling) if is_struggling is not None else None,
                quiz_question,
            ),
        )
        await db.commit()


async def get_history(session_id: str) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM messages WHERE session_id = ? ORDER BY created_at ASC",
            (session_id,),
        ) as cursor:
            rows = await cursor.fetchall()
    return [dict(r) for r in rows]


async def get_sessions() -> list[dict]:
    """Return one row per session (latest message text + timestamp)."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT session_id,
                   MAX(created_at) AS last_active,
                   COUNT(*) AS message_count,
                   MAX(subject) AS subject
            FROM messages
            GROUP BY session_id
            ORDER BY last_active DESC
            LIMIT 20
        """) as cursor:
            rows = await cursor.fetchall()
    return [dict(r) for r in rows]
