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

<br/>

<img src="frontend/public/icons/icon.svg" width="80" height="80" alt="VoiceSensei Logo" />

<h1>VoiceSensei</h1>

<p><strong>Voice-first AI tutor for India's toughest competitive exams.</strong><br/>Speak your doubts. Hear the answers. Ace the exam.</p>

<br/>

[![Live Demo](https://img.shields.io/badge/Live%20Demo-voicesensei.vercel.app-7C3AED?style=for-the-badge&logo=vercel&logoColor=white)](https://voicesensei.vercel.app)
&nbsp;
[![HF Space](https://img.shields.io/badge/API-HF%20Spaces-FF6B35?style=for-the-badge&logo=huggingface&logoColor=white)](https://shraman18-voicesensei.hf.space)

<br/><br/>

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-6-646CFF?style=flat-square&logo=vite&logoColor=white)](https://vitejs.dev)
[![Groq](https://img.shields.io/badge/Groq-Llama%203.3%20+%20Whisper-F55036?style=flat-square)](https://groq.com)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED?style=flat-square&logo=docker&logoColor=white)](Dockerfile)
[![PWA](https://img.shields.io/badge/PWA-enabled-5A0FC8?style=flat-square&logo=pwa&logoColor=white)](frontend/vite.config.js)
[![License](https://img.shields.io/badge/License-MIT-22C55E?style=flat-square)](LICENSE)

<br/>

</div>

---

## Why VoiceSensei?

Most Indian exam students don't have access to a personal tutor. VoiceSensei fills that gap — it listens to your question, retrieves the right context from your own notes, and speaks back a concise, exam-focused answer. No typing. No searching. Just learning.

> **Built for JEE · NEET · UPSC · SSC** on a 100% free-tier stack — Groq for STT + LLM, local FAISS for RAG, gTTS fallback for voice. Self-host it at **zero cost**.

---

## Features

<table>
<tr>
<td width="50%">

### 🎤 Voice Pipeline
Tap the mic → speak → hear the answer. WebM audio captured in the browser, transcribed by **Groq Whisper**, answered by **Llama 3.3-70b**, spoken back via **ElevenLabs** or gTTS.

</td>
<td width="50%">

### 🧠 RAG on Your Notes
Drop in any PDF — NCERT chapters, coaching material, past papers. **FAISS + sentence-transformers** runs 100% locally. Answers pull from your actual notes.

</td>
</tr>
<tr>
<td width="50%">

### 🎯 Quiz Mode
After every explanation, VoiceSensei flips to examiner mode and quizzes you on what you just heard. Speak your answer aloud — it evaluates it.

</td>
<td width="50%">

### 🔄 Struggle Detector
Answer wrong or hesitantly? The AI detects it automatically and re-explains the concept more simply — like a patient tutor would.

</td>
</tr>
<tr>
<td width="50%">

### 🇮🇳 Hindi Support
Full bilingual mode. Switch to हिंदी and get questions, answers, and quizzes entirely in Hindi — including voice output.

</td>
<td width="50%">

### 📊 Progress Tracking
JWT-authenticated accounts. Track your streak, accuracy by subject, quiz scores, and session history across devices.

</td>
</tr>
</table>

---

## Live Demo

```
🎤 Student (spoken): "Explain Newton's Third Law for JEE"

⚡ VoiceSensei (spoken back):
   "Newton's Third Law: every action has an equal and opposite reaction.
    When you push a wall, the wall pushes back with equal force —
    but on a different object. JEE loves this for rocket propulsion
    and gun recoil problems. Key takeaway: paired forces always act
    on different bodies, never the same one."

🎯 Quiz: "A rocket expels gas downward. Which law explains its upward thrust?"
```

**→ Try it live at [voicesensei.vercel.app](https://voicesensei.vercel.app)**

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Browser  (React 18 + Vite PWA)         │
│  MediaRecorder API → WebM blob → FormData               │
└─────────────────────────┬───────────────────────────────┘
                          │  HTTPS multipart/form-data
                          ▼
┌─────────────────────────────────────────────────────────┐
│              FastAPI Backend  (Uvicorn · Python 3.11)   │
│                                                         │
│  ┌─────────┐   ┌──────────────────────────────────┐    │
│  │  Auth   │   │          Voice Pipeline           │    │
│  │  JWT    │   │                                   │    │
│  │  bcrypt │   │  WebM → Groq Whisper → transcript │    │
│  └─────────┘   │         ↓                        │    │
│                │  FAISS RAG → top-4 note chunks    │    │
│  ┌──────────┐  │         ↓                        │    │
│  │ SQLite   │  │  Groq Llama 3.3-70b → answer     │    │
│  │aiosqlite │  │         ↓                        │    │
│  │ sessions │  │  ElevenLabs → gTTS → MP3 bytes   │    │
│  │ progress │  └──────────────────────────────────┘    │
│  └──────────┘                                           │
└─────────────────────────────────────────────────────────┘
          │ Docker container → Hugging Face Spaces
          │ Static files served by same FastAPI instance
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 18, Vite 6, Vite PWA (Workbox), pure CSS |
| **STT** | Groq `whisper-large-v3-turbo` — 7,200 free seconds/day |
| **LLM** | Groq `llama-3.3-70b-versatile` — exam-tuned system prompts |
| **TTS** | ElevenLabs (premium) → gTTS (free fallback) |
| **RAG** | FAISS + `sentence-transformers/all-MiniLM-L6-v2` (local) |
| **Backend** | FastAPI + Uvicorn, aiosqlite, python-jose JWT, passlib bcrypt |
| **Infra** | Docker → HF Spaces (API), Vercel (frontend) |

---

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- Free [Groq API key](https://console.groq.com) (covers both STT + LLM)

### 1. Clone

```bash
git clone https://github.com/Shraman123/VoiceSensei.git
cd VoiceSensei
```

### 2. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

Create `backend/.env`:

```env
GROQ_API_KEY=gsk_...          # Required — free at console.groq.com
ELEVENLABS_API_KEY=sk_...     # Optional — falls back to gTTS
SECRET_KEY=your-random-secret # JWT signing key
```

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend

```bash
cd frontend
npm install
echo "VITE_API_URL=http://localhost:8000" > .env.local
npm run dev
```

Open **[http://localhost:5173](http://localhost:5173)**

---

## Deploy

### Hugging Face Spaces (API + Full App)

VoiceSensei ships as a single Docker container — the FastAPI backend serves the built React frontend at the same URL.

```bash
# Add HF remote and push
git remote add hf https://huggingface.co/spaces/<your-username>/VoiceSensei
git push hf main
```

Set these in **Space Settings → Variables and secrets** (values only — no `KEY=` prefix):

| Secret | Value |
|---|---|
| `GROQ_API_KEY` | Your Groq key |
| `ELEVENLABS_API_KEY` | Your ElevenLabs key (optional) |
| `SECRET_KEY` | Any random string for JWT signing |

The Docker build pre-downloads `all-MiniLM-L6-v2` (~90 MB) so the first PDF upload is instant.

### Vercel (Frontend Only)

```bash
# Set VITE_API_URL to your HF Space URL, then:
vercel --prod
```

Or connect your GitHub repo to [vercel.com](https://vercel.com) and set:

```
VITE_API_URL = https://<your-username>-voicesensei.hf.space
```

---

## API Reference

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/health` | — | Server status + key check |
| `POST` | `/auth/register` | — | Create account |
| `POST` | `/auth/login` | — | Get JWT token |
| `GET` | `/auth/me` | Bearer | Current user |
| `POST` | `/upload` | — | Ingest PDF into FAISS |
| `POST` | `/voice` | Bearer (opt) | STT → RAG → LLM → TTS |
| `POST` | `/quiz/evaluate` | Bearer (opt) | Evaluate spoken quiz answer |
| `GET` | `/sessions` | Bearer (opt) | Recent session list |
| `GET` | `/history/{id}` | — | Messages for a session |
| `GET` | `/progress` | Bearer | User stats + streak |

---

## Project Structure

```
VoiceSensei/
├── Dockerfile                    # Multi-stage: Node build → Python serve
├── backend/
│   ├── main.py                   # FastAPI app + all endpoints
│   ├── auth.py                   # JWT + bcrypt helpers
│   ├── database.py               # aiosqlite — users, messages, scores
│   ├── requirements.txt
│   └── pipeline/
│       ├── stt.py                # Groq Whisper transcription
│       ├── llm.py                # Groq LLM + exam system prompts
│       ├── tts.py                # ElevenLabs / gTTS synthesis
│       ├── rag.py                # FAISS vector store + PDF ingestion
│       └── quiz.py               # Quiz engine + Struggle Detector
└── frontend/
    ├── vite.config.js            # Vite + PWA plugin
    ├── vercel.json               # SPA rewrite rules
    └── src/
        ├── App.jsx               # Root — auth, session, voice state
        ├── index.css             # Design system (dark theme, CSS tokens)
        ├── hooks/
        │   ├── useVoice.js       # Full voice pipeline hook
        │   └── useAuth.js        # JWT storage + auth header
        └── components/
            ├── MicButton.jsx     # Signature recording orb
            ├── ChatBubble.jsx    # Study / quiz / struggle renderer
            ├── AuthModal.jsx     # Login / register modal
            ├── ProgressPanel.jsx # Streak, stats, subject breakdown
            ├── SessionDrawer.jsx # Session history sidebar
            ├── LanguageToggle.jsx# English ↔ हिंदी switch
            ├── MobileMenu.jsx    # Bottom sheet for mobile
            ├── ModeToggle.jsx    # Study ↔ Quiz mode
            ├── SubjectSelector.jsx
            └── UploadPDF.jsx     # Drag-and-drop PDF ingestion
```

---

## Roadmap

- [x] Voice pipeline — STT → RAG → LLM → TTS
- [x] Persistent chat history (SQLite + aiosqlite)
- [x] Hindi language support (bilingual STT, LLM, TTS)
- [x] Mobile PWA (installable, offline shell, service worker)
- [x] Hugging Face Spaces Docker deployment
- [x] User accounts + JWT auth + progress tracking
- [ ] Spaced repetition scheduler
- [ ] Multi-user leaderboard
- [ ] Subject-specific voice personas

---

<div align="center">

<br/>

**Built for every student who learns better by** ***hearing*** **than reading.**

<br/>

[![Try VoiceSensei](https://img.shields.io/badge/Try%20VoiceSensei-voicesensei.vercel.app-7C3AED?style=for-the-badge&logo=vercel&logoColor=white)](https://voicesensei.vercel.app)

<br/>

<sub>Made with ⚡ by <a href="https://github.com/Shraman123">Shraman</a> · Powered by Groq · Deployed on Vercel + HF Spaces</sub>

<br/>

</div>
