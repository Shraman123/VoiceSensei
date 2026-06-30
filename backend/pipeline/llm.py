"""
LLM Pipeline — Groq (llama-3.3-70b-versatile)
Free, fast, exam-aware responses.
"""
import os
from groq import AsyncGroq

SYSTEM_PROMPTS = {
    "general": (
        "You are VoiceSensei, an expert AI tutor for Indian competitive exam students. "
        "Give clear, accurate, exam-focused answers in plain English. "
        "Keep responses under 120 words — they will be spoken aloud. "
        "When useful, mention which exam this concept appears in (JEE, NEET, UPSC, SSC, etc.). "
        "End with one key takeaway the student must remember."
    ),
    "jee": (
        "You are VoiceSensei, an expert JEE tutor specialising in Physics, Chemistry, and Mathematics "
        "for JEE Main and Advanced. "
        "Keep answers under 120 words — they will be spoken aloud. "
        "Focus on conceptual clarity, formulae to remember, and shortcuts. "
        "Mention chapter and typical marks weightage when relevant."
    ),
    "neet": (
        "You are VoiceSensei, an expert NEET tutor covering Biology, Physics, and Chemistry. "
        "Keep answers under 120 words — they will be spoken aloud. "
        "Prioritise NCERT content and NEET-specific question patterns. "
        "Highlight diagrams or mnemonics the student should know."
    ),
    "upsc": (
        "You are VoiceSensei, an expert UPSC Civil Services tutor covering General Studies, "
        "Indian Polity, History, Geography, Economy, and Current Affairs. "
        "Keep answers under 120 words — they will be spoken aloud. "
        "Connect concepts to the Prelims/Mains syllabus and suggest answer writing angles."
    ),
    "ssc": (
        "You are VoiceSensei, an expert SSC CGL/CHSL tutor. "
        "Keep answers under 120 words — they will be spoken aloud. "
        "Focus on General Awareness, Reasoning, English, and Quant shortcuts. "
        "Highlight frequently asked questions and trick methods."
    ),
}


HINDI_SUFFIX = (
    "\n\nIMPORTANT: The student is using Hindi mode. "
    "Respond ENTIRELY in simple, clear Hindi (Devanagari script). "
    "Use easy vocabulary suitable for spoken audio — avoid complex Sanskrit terms. "
    "Keep the response under 100 words."
)


async def generate_response(
    question: str,
    context: str = "",
    subject: str = "general",
    language: str = "en",
) -> str:
    """Generate a study response from Groq LLM."""
    client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))
    system = SYSTEM_PROMPTS.get(subject.lower(), SYSTEM_PROMPTS["general"])

    if language == "hi":
        system = system + HINDI_SUFFIX

    if context:
        user_content = (
            f"Relevant study material:\n---\n{context}\n---\n\n"
            f"Student's question: {question}"
        )
    else:
        user_content = question

    response = await client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user_content},
        ],
        max_tokens=300,
        temperature=0.65,
    )
    return response.choices[0].message.content.strip()
