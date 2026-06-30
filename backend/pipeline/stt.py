"""
STT Pipeline — Groq Whisper (whisper-large-v3-turbo)
100% free tier: 7,200 audio-seconds/day, no OpenAI key needed.
"""
import io
import os

from groq import AsyncGroq


async def transcribe_audio(audio_bytes: bytes, filename: str = "recording.webm") -> str:
    """
    Transcribe audio bytes using Groq's Whisper endpoint.
    Groq free tier: 7,200 seconds/day — plenty for a study session.
    """
    client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

    audio_file = (filename, io.BytesIO(audio_bytes), _mime_from_filename(filename))

    transcription = await client.audio.transcriptions.create(
        model="whisper-large-v3-turbo",
        file=audio_file,
        response_format="text",
        language="en",  # remove to enable auto-detect
    )

    if isinstance(transcription, str):
        return transcription.strip()

    return (getattr(transcription, "text", "") or "").strip()


def _mime_from_filename(filename: str) -> str:
    ext = filename.rsplit(".", 1)[-1].lower()
    mime_map = {
        "webm": "audio/webm",
        "mp4":  "audio/mp4",
        "m4a":  "audio/mp4",
        "wav":  "audio/wav",
        "ogg":  "audio/ogg",
        "flac": "audio/flac",
        "mp3":  "audio/mpeg",
    }
    return mime_map.get(ext, "audio/webm")
