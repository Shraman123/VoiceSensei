# ── Stage 1: Build React frontend ─────────────────────────────────────────────
FROM node:20-slim AS frontend-builder

WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
# Production build — API calls go to same origin (relative URL)
RUN VITE_API_URL="" npm run build


# ── Stage 2: Python backend + serve frontend ───────────────────────────────────
FROM python:3.11-slim

WORKDIR /app

# System deps for faiss + sentence-transformers
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Backend source
COPY backend/ ./

# Copy built frontend into backend/static so FastAPI can serve it
COPY --from=frontend-builder /frontend/dist ./static

# HF Spaces requires port 7860
EXPOSE 7860

# Pre-download the embedding model so first request isn't slow
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')" || true

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
