"""
TTS Pipeline — ElevenLabs (premium) → gTTS (free fallback)
If ELEVENLABS_API_KEY is set, uses it. Otherwise falls back to gTTS at no cost.
"""
import io
import os

import httpx
from gtts import gTTS


ELEVENLABS_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # Rachel — clear, calm, neutral


async def synthesize_speech(text: str) -> bytes:
    """
    Synthesise speech from text.
    Returns raw MP3 bytes.
    """
    el_key = os.getenv("ELEVENLABS_API_KEY")
    if el_key:
        try:
            return await _elevenlabs_tts(text, el_key)
        except Exception as e:
            print(f"ElevenLabs TTS failed ({e}), falling back to gTTS")

    return _gtts_tts(text)


async def _elevenlabs_tts(text: str, api_key: str) -> bytes:
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json",
    }
    payload = {
        "text": text,
        "model_id": "eleven_turbo_v2",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
    }
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(url, json=payload, headers=headers)
        resp.raise_for_status()
        return resp.content


def _gtts_tts(text: str) -> bytes:
    tts = gTTS(text=text, lang="en", slow=False)
    buf = io.BytesIO()
    tts.write_to_fp(buf)
    buf.seek(0)
    return buf.read()
