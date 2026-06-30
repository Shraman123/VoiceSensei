"""
VoiceSensei — FastAPI Backend
Endpoints:
  GET  /health                  — health check
  POST /upload                  — ingest PDF into RAG
  POST /voice                   — main pipeline: STT → RAG → LLM → TTS
  POST /quiz/evaluate           — Struggle Detector: evaluate student's quiz answer
  GET  /history/{session_id}    — fetch persisted chat history for a session
  GET  /sessions                — list recent sessions
"""
import base64
import uuid
from contextlib import asynccontextmanager

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from pipeline.stt import transcribe_audio
from pipeline.llm import generate_response
from pipeline.tts import synthesize_speech
from pipeline.rag import RAGPipeline
from pipeline.quiz import QuizEngine
from database import init_db, save_turn, get_history, get_sessions


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
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok", "rag_loaded": rag.is_loaded, "version": "1.0.0"}


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload a PDF study document into FAISS."""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="PDF must be under 10 MB.")

    result = rag.load_pdf_bytes(content, file.filename)
    return {
        "status": "loaded",
        "filename": file.filename,
        "chunks": result["chunks"],
        "pages": result["pages"],
    }


@app.post("/voice")
async def voice_pipeline(
    audio: UploadFile = File(...),
    mode: str = Form("study"),
    subject: str = Form("general"),
    session_id: str = Form(None),
):
    """Main voice pipeline: STT → RAG → LLM → TTS"""
    if session_id is None:
        session_id = str(uuid.uuid4())

    audio_bytes = await audio.read()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Empty audio received.")

    transcript = await transcribe_audio(audio_bytes)
    if not transcript:
        raise HTTPException(
            status_code=400,
            detail="Could not transcribe audio. Please speak clearly and try again.",
        )

    context = rag.retrieve(transcript) if rag.is_loaded else ""

    if mode == "quiz":
        response_text, quiz_question = await quiz_engine.generate_quiz_response(
            question=transcript, context=context, subject=subject,
        )
    else:
        response_text = await generate_response(
            question=transcript, context=context, subject=subject,
        )
        quiz_question = None

    speech_bytes = await synthesize_speech(response_text)

    await save_turn(
        session_id=session_id,
        user_text=transcript,
        agent_text=response_text,
        mode=mode,
        subject=subject,
        quiz_question=quiz_question,
    )

    return {
        "session_id": session_id,
        "transcript": transcript,
        "response": response_text,
        "quiz_question": quiz_question,
        "audio_b64": base64.b64encode(speech_bytes).decode("utf-8"),
    }


@app.post("/quiz/evaluate")
async def evaluate_quiz_answer(
    audio: UploadFile = File(...),
    question: str = Form(...),
    expected_answer: str = Form(...),
    subject: str = Form("general"),
    session_id: str = Form(None),
):
    """Struggle Detector: evaluate student's spoken quiz answer."""
    if session_id is None:
        session_id = str(uuid.uuid4())

    audio_bytes = await audio.read()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Empty audio received.")

    student_answer = await transcribe_audio(audio_bytes)
    if not student_answer:
        raise HTTPException(
            status_code=400,
            detail="Could not transcribe your answer. Please try again.",
        )

    evaluation = await quiz_engine.evaluate_answer(
        question=question,
        expected=expected_answer,
        student_answer=student_answer,
        subject=subject,
    )

    speech_bytes = await synthesize_speech(evaluation["feedback"])

    await save_turn(
        session_id=session_id,
        user_text=student_answer,
        agent_text=evaluation["feedback"],
        mode="quiz",
        subject=subject,
        is_correct=evaluation.get("is_correct"),
        is_struggling=evaluation.get("is_struggling"),
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


@app.get("/history/{session_id}")
async def fetch_history(session_id: str):
    """Return all messages for a session in chronological order."""
    messages = await get_history(session_id)
    return {"session_id": session_id, "messages": messages}


@app.get("/sessions")
async def fetch_sessions():
    """Return the 20 most recent sessions."""
    return {"sessions": await get_sessions()}
