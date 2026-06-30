"""
Quiz Engine + Struggle Detector
Generates quiz questions and evaluates student answers with an LLM judge.
If the student is struggling, automatically generates a simpler re-explanation.
"""
import os
from groq import AsyncGroq

from pipeline.llm import SYSTEM_PROMPTS, generate_response


QUIZ_SUFFIX = (
    "\n\nAfter your explanation, ask ONE short quiz question to test understanding. "
    "Format your response as:\nANSWER: <your explanation>\nQUIZ: <your question>"
)

EVAL_PROMPT = """You are an exam tutor evaluating a student's spoken answer.

Quiz question: {question}
Expected answer / explanation: {expected}
Student's answer: {student_answer}

Evaluate strictly. Look for:
- Factual correctness
- Uncertainty markers ("I think", "maybe", "not sure", "I don't know")
- Fundamental misconceptions

Respond in JSON only:
{{
  "is_correct": true/false,
  "is_struggling": true/false,
  "score": <1-10>,
  "feedback": "<spoken feedback under 100 words>",
  "simplified_explanation": "<if is_struggling, re-explain more simply in under 80 words; else null>"
}}"""


class QuizEngine:
    async def generate_quiz_response(
        self,
        question: str,
        context: str = "",
        subject: str = "general",
    ) -> tuple[str, str]:
        """
        Generate a study answer + quiz question.
        Returns (answer_text, quiz_question).
        """
        client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))
        system = SYSTEM_PROMPTS.get(subject.lower(), SYSTEM_PROMPTS["general"])
        system_with_quiz = system + QUIZ_SUFFIX

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
                {"role": "system", "content": system_with_quiz},
                {"role": "user", "content": user_content},
            ],
            max_tokens=400,
            temperature=0.65,
        )

        raw = response.choices[0].message.content.strip()

        # Parse ANSWER: / QUIZ: format
        answer_text = raw
        quiz_question = None

        if "QUIZ:" in raw:
            parts = raw.split("QUIZ:", 1)
            answer_part = parts[0].replace("ANSWER:", "").strip()
            quiz_question = parts[1].strip()
            answer_text = answer_part
        elif "ANSWER:" in raw:
            answer_text = raw.replace("ANSWER:", "").strip()

        return answer_text, quiz_question

    async def evaluate_answer(
        self,
        question: str,
        expected: str,
        student_answer: str,
        subject: str = "general",
    ) -> dict:
        """
        Evaluate student's quiz answer. Returns evaluation dict.
        If struggling, feedback includes a simplified re-explanation.
        """
        import json

        client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

        prompt = EVAL_PROMPT.format(
            question=question,
            expected=expected,
            student_answer=student_answer,
        )

        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.3,
        )

        raw = response.choices[0].message.content.strip()

        try:
            # Strip markdown fences if present
            clean = raw.replace("```json", "").replace("```", "").strip()
            result = json.loads(clean)
        except json.JSONDecodeError:
            # Graceful fallback
            result = {
                "is_correct": False,
                "is_struggling": True,
                "score": 5,
                "feedback": "I couldn't evaluate your answer clearly. Let's try again.",
                "simplified_explanation": None,
            }

        # Merge simplified explanation into feedback if struggling
        if result.get("is_struggling") and result.get("simplified_explanation"):
            result["feedback"] = (
                result["feedback"] + " " + result["simplified_explanation"]
            )

        return result
