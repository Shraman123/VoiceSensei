---
title: VoiceSensei
emoji: ⚡
colorFrom: purple
colorTo: indigo
sdk: docker
pinned: false
app_port: 7860
---

<div align="center">

# ⚡ VoiceSensei

### Voice-First AI Exam Tutor for Indian Competitive Exams

*Speak your doubts. Hear the answers. Ace the exam.*

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev)
[![Groq](https://img.shields.io/badge/Groq-Whisper%20+%20Llama%203.3-F55036?style=flat-square)](https://groq.com)
[![License](https://img.shields.io/badge/License-MIT-7C3AED?style=flat-square)](LICENSE)

</div>

---

## What is VoiceSensei?

VoiceSensei is a **voice-first AI study companion** built for students preparing for India's toughest exams — JEE, NEET, UPSC, and SSC. Just tap a button, speak your question, and get a spoken answer back in seconds. No typing. No searching. Just learning.

Built on a fully free-tier stack — **Groq** for blazing-fast STT + LLM inference and **local FAISS embeddings** for RAG — so anyone can self-host it at zero cost.

---

## Demo

```
Student: "Explain Newton's Third Law of Motion"

VoiceSensei: "Newton's Third Law states that for every action, there is an equal
              and opposite reaction. When you push a wall, the wall pushes back
              with equal force. Key for JEE: this law explains rocket propulsion
              and why a gun recoils when fired. Remember — the forces act on
              different objects, never on the same one."

              🎯 Quiz: A rocket expels gas downward. Which law explains its upward motion?
```

---

## Features

| Feature | Description |
|---|---|
| 🎤 **Voice Pipeline** | Speak → Transcribe (Groq Whisper) → Answer (Llama 3.3-70b) → Speak back |
| 🧠 **RAG on your notes** | Upload any PDF — NCERT, coaching notes, past papers — and answers pull from it |
| 🎯 **Quiz Mode** | After every answer, get quizzed. The AI tests if you actually understood |
| 🔄 **Struggle Detector** | Answers wrong or uncertain? AI detects it and re-explains more simply |
| 📚 **Exam Presets** | Tuned system prompts for JEE · NEET · UPSC · SSC · General |
| 🔊 **TTS Playback** | ElevenLabs premium voice or gTTS free fallback — always spoken aloud |

---

## Architecture

```
Browser (React + Vite)
    │
    │  WebM audio blob
    ▼
FastAPI Backend
    │
    ├── STT  ──► Groq Whisper (whisper-large-v3-turbo)
    │                └── transcript
    │
    ├── RAG  ──► FAISS + sentence-transformers/all-MiniLM-L6-v2
    │                └── top-4 relevant chunks (local, free)
    │
    ├── LLM  ──► Groq llama-3.3-70b-versatile
    │                └── exam-focused answer (<120 words, spoken-ready)
    │
    └── TTS  ──► ElevenLabs (premium) → gTTS (free fallback)
                     └── MP3 bytes → base64 → browser Audio API
```

---

## Tech Stack

**Backend**
- [FastAPI](https://fastapi.tiangolo.com) + Uvicorn
- [Groq](https://groq.com) — Whisper STT + Llama 3.3-70b LLM (free tier)
- [LangChain](https://langchain.com) + FAISS — local RAG pipeline
- `sentence-transformers/all-MiniLM-L6-v2` — local embeddings (~90 MB)
- ElevenLabs TTS / gTTS fallback

**Frontend**
- React 18 + Vite
- MediaRecorder API for in-browser audio capture
- Zero UI libraries — pure CSS with CSS custom properties

---

## Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- A free [Groq API key](https://console.groq.com)

### 1. Clone

```bash
git clone https://github.com/Shraman123/VoiceSensei.git
cd VoiceSensei
```

### 2. Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

pip install -r requirements.txt

cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

```bash
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

Open **http://localhost:5173**

---

## Environment Variables

**`backend/.env`**
```env
GROQ_API_KEY=your_groq_api_key        # Required — free at console.groq.com
ELEVENLABS_API_KEY=your_el_key        # Optional — premium TTS (falls back to gTTS)
```

**`frontend/.env.local`**
```env
VITE_API_URL=http://localhost:8000
```

---

## How to Use

1. **Pick a subject** — General, JEE, NEET, UPSC, or SSC
2. **Upload a PDF** (optional) — drop in your notes to enable RAG
3. **Tap the mic** — ask any exam question out loud
4. **Listen** — VoiceSensei speaks the answer back
5. **Switch to Quiz mode** — get quizzed after each answer
6. **Struggle Detector** — if you answer wrong or hesitantly, the AI simplifies its explanation automatically

---

## Project Structure

```
VoiceSensei/
├── backend/
│   ├── main.py                  # FastAPI app + endpoints
│   ├── requirements.txt
│   ├── Dockerfile
│   └── pipeline/
│       ├── stt.py               # Groq Whisper transcription
│       ├── llm.py               # Groq LLM + exam system prompts
│       ├── tts.py               # ElevenLabs / gTTS synthesis
│       ├── rag.py               # FAISS vector store + PDF ingestion
│       └── quiz.py              # Quiz engine + Struggle Detector
│
└── frontend/
    ├── index.html
    ├── vite.config.js
    └── src/
        ├── App.jsx              # Root — state machine for study/quiz flow
        ├── index.css            # Design system (dark theme, CSS tokens)
        ├── components/
        │   ├── MicButton.jsx    # Signature orb with recording rings
        │   ├── ChatBubble.jsx   # Message renderer (study / quiz / struggle)
        │   ├── ModeToggle.jsx   # Study ↔ Quiz switcher
        │   ├── SubjectSelector.jsx
        │   └── UploadPDF.jsx    # Drag-and-drop PDF ingestion
        └── hooks/
            └── useVoice.js      # Full voice pipeline hook
```

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Server + RAG status |
| `POST` | `/upload` | Ingest PDF into FAISS |
| `POST` | `/voice` | Main pipeline: STT → RAG → LLM → TTS |
| `POST` | `/quiz/evaluate` | Struggle Detector: evaluate spoken quiz answer |

---

## Deploy to Hugging Face Spaces

VoiceSensei ships as a single Docker container — the FastAPI backend serves the built React frontend at the same URL.

**Steps:**

1. Fork / push this repo to your Hugging Face account
2. Create a new Space → **Docker** SDK
3. Add these repository secrets in Space Settings → Variables:
   ```
   GROQ_API_KEY      = your_groq_api_key
   ELEVENLABS_API_KEY = your_elevenlabs_api_key   # optional
   ```
4. HF Spaces auto-detects `Dockerfile` at the root and builds it
5. Your app is live at `https://huggingface.co/spaces/<your-username>/VoiceSensei`

> The Docker build pre-downloads the `all-MiniLM-L6-v2` embedding model (~90 MB) so the first PDF upload is instant.

---

## Roadmap

- [x] Persistent chat history (SQLite)
- [x] Hindi language support
- [x] Mobile PWA
- [x] Hugging Face Spaces deployment
- [ ] User accounts + progress tracking

---

<div align="center">

Built for every student who learns better by *hearing* than reading.

**[⚡ Get your free Groq key →](https://console.groq.com)**

</div>
