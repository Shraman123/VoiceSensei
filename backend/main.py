"""
VoiceSensei — FastAPI Backend
Endpoints:
  POST /auth/register           — create account
  POST /auth/login              — get JWT
  GET  /auth/me                 — current user
  GET  /health                  — health check
  POST /upload                  — ingest PDF into RAG
  POST /voice                   — STT → RAG → LLM → TTS
  POST /quiz/evaluate           — Struggle Detector
  GET  /history/{session_id}    — chat history for a session
  GET  /sessions                — recent sessions
  GET  /progress                — user progress stats
"""
import base64
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, File, Form, HTTPException, UploadFile, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr

from pipeline.stt import transcribe_audio
from pipeline.llm import generate_response
from pipeline.tts import synthesize_speech
from pipeline.rag import RAGPipeline
from pipeline.quiz import QuizEngine
from database import (
    init_db, save_turn, save_quiz_score,
    get_history, get_sessions, get_progress,
    create_user, get_user_by_email,
)
from auth import (
    hash_password, verify_password, create_access_token,
    get_current_user, require_user,
)


rag = RAGPipeline()
quiz_engine = QuizEngine()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    print("VoiceSensei API starting up…")
    yield
    print("VoiceSensei API shutting down.")


app = FastAPI(
    title="VoiceSensei API",
    description="AI Voice Tutor for Indian Competitive Exam Prep",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Auth ───────────────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


@app.post("/auth/register", status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest):
    if len(body.password) < 6:
        raise HTTPException(400, "Password must be at least 6 characters.")
    existing = await get_user_by_email(body.email)
    if existing:
        raise HTTPException(400, "An account with this email already exists.")
    user = await create_user(body.username, body.email, hash_password(body.password))
    token = create_access_token(user["id"])
    return {"token": token, "user": {"id": user["id"], "username": user["username"], "email": user["email"]}}


@app.post("/auth/login")
async def login(body: LoginRequest):
    user = await get_user_by_email(body.email)
    if not user or not verify_password(body.password, user["password_hash"]):
        raise HTTPException(401, "Invalid email or password.")
    token = create_access_token(user["id"])
    return {"token": token, "user": {"id": user["id"], "username": user["username"], "email": user["email"]}}


@app.get("/auth/me")
async def me(user: dict = Depends(require_user)):
    return {"id": user["id"], "username": user["username"], "email": user["email"]}


# ── Health ─────────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    import os
    return {
        "status": "ok",
        "rag_loaded": rag.is_loaded,
        "version": "2.0.0",
        "groq_key_set": bool(os.getenv("GROQ_API_KEY")),
        "el_key_set": bool(os.getenv("ELEVENLABS_API_KEY")),
    }

@app.get("/debug/auth")
async def debug_auth():
    """Test bcrypt + jose are working."""
    try:
        from auth import hash_password, create_access_token
        h = hash_password("testpass")
        t = create_access_token(1)
        return {"bcrypt": "ok", "jose": "ok", "hash_len": len(h), "token_len": len(t)}
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}

@app.get("/debug/db")
async def debug_db():
    """Test DB write."""
    try:
        from database import init_db
        await init_db()
        return {"db": "ok"}
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


# ── Upload ─────────────────────────────────────────────────────────────────────

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are supported.")
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(400, "PDF must be under 10 MB.")
    result = rag.load_pdf_bytes(content, file.filename)
    return {"status": "loaded", "filename": file.filename, "chunks": result["chunks"], "pages": result["pages"]}


# ── Voice pipeline ─────────────────────────────────────────────────────────────

@app.post("/voice")
async def voice_pipeline(
    audio: UploadFile = File(...),
    mode: str = Form("study"),
    subject: str = Form("general"),
    session_id: str = Form(None),
    language: str = Form("en"),
    user: dict = Depends(get_current_user),
):
    if session_id is None:
        session_id = str(uuid.uuid4())

    audio_bytes = await audio.read()
    if not audio_bytes:
        raise HTTPException(400, "Empty audio received.")

    transcript = await transcribe_audio(audio_bytes, language=language if language == "hi" else None)
    if not transcript:
        raise HTTPException(400, "Could not transcribe audio. Please speak clearly and try again.")

    context = rag.retrieve(transcript) if rag.is_loaded else ""

    if mode == "quiz":
        response_text, quiz_question = await quiz_engine.generate_quiz_response(
            question=transcript, context=context, subject=subject, language=language,
        )
    else:
        response_text = await generate_response(
            question=transcript, context=context, subject=subject, language=language,
        )
        quiz_question = None

    speech_bytes = await synthesize_speech(response_text, language=language)

    await save_turn(
        session_id=session_id,
        user_text=transcript,
        agent_text=response_text,
        mode=mode,
        subject=subject,
        quiz_question=quiz_question,
        user_id=user["id"] if user else None,
    )

    return {
        "session_id": session_id,
        "transcript": transcript,
        "response": response_text,
        "quiz_question": quiz_question,
        "audio_b64": base64.b64encode(speech_bytes).decode("utf-8"),
    }


# ── Quiz evaluate ──────────────────────────────────────────────────────────────

@app.post("/quiz/evaluate")
async def evaluate_quiz_answer(
    audio: UploadFile = File(...),
    question: str = Form(...),
    expected_answer: str = Form(...),
    subject: str = Form("general"),
    session_id: str = Form(None),
    language: str = Form("en"),
    user: dict = Depends(get_current_user),
):
    if session_id is None:
        session_id = str(uuid.uuid4())

    audio_bytes = await audio.read()
    if not audio_bytes:
        raise HTTPException(400, "Empty audio received.")

    student_answer = await transcribe_audio(audio_bytes, language=language if language == "hi" else None)
    if not student_answer:
        raise HTTPException(400, "Could not transcribe your answer. Please try again.")

    evaluation = await quiz_engine.evaluate_answer(
        question=question, expected=expected_answer,
        student_answer=student_answer, subject=subject, language=language,
    )

    speech_bytes = await synthesize_speech(evaluation["feedback"], language=language)

    await save_turn(
        session_id=session_id,
        user_text=student_answer,
        agent_text=evaluation["feedback"],
        mode="quiz",
        subject=subject,
        is_correct=evaluation.get("is_correct"),
        is_struggling=evaluation.get("is_struggling"),
        user_id=user["id"] if user else None,
    )

    if user:
        await save_quiz_score(
            user_id=user["id"],
            session_id=session_id,
            subject=subject,
            score=evaluation.get("score", 5),
            is_correct=evaluation.get("is_correct", False),
        )

    return {
        "student_answer": student_answer,
        "is_correct": evaluation.get("is_correct", False),
        "is_struggling": evaluation.get("is_struggling", False),
        "score": evaluation.get("score", 5),
        "feedback": evaluation["feedback"],
        "simplified_explanation": evaluation.get("simplified_explanation"),
        "audio_b64": base64.b64encode(speech_bytes).decode("utf-8"),
    }


# ── History & sessions ─────────────────────────────────────────────────────────

@app.get("/history/{session_id}")
async def fetch_history(session_id: str):
    messages = await get_history(session_id)
    return {"session_id": session_id, "messages": messages}


@app.get("/sessions")
async def fetch_sessions(user: dict = Depends(get_current_user)):
    sessions = await get_sessions(user_id=user["id"] if user else None)
    return {"sessions": sessions}


# ── Progress ───────────────────────────────────────────────────────────────────

@app.get("/progress")
async def fetch_progress(user: dict = Depends(require_user)):
    stats = await get_progress(user["id"])
    return stats


# ── Serve frontend (production) ────────────────────────────────────────────────

_static_dir = Path(__file__).parent / "static"
if _static_dir.exists():
    app.mount("/", StaticFiles(directory=_static_dir, html=True), name="frontend")
