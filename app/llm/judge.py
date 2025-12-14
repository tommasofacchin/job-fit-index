# app/llm/judge.py
import json
import streamlit as st
from app.llm.client import call_llm


CRITERIA = [
    "Evidence density",
    "Decision quality",
    "Failure intelligence",
    "Context translation",
    "Uniqueness signal",
]


def evaluate_answers_with_llama(answers: dict):
    """
    Use the LLM to suggest scores (0,5,10,15,20) and reasons per criterion,
    plus a short signature summary.
    """

    # Mock disattivato
    if False:
        scores = {
            "Evidence density": 10,
            "Decision quality": 15,
            "Failure intelligence": 5,
            "Context translation": 10,
            "Uniqueness signal": 5,
        }
        reasons = {k: "Mock reason for development." for k in scores}
        summary = "Mock summary for development. This is not from the LLM."
        return {"scores": scores, "reasons": reasons, "summary": summary}

    answers_json = json.dumps(answers, indent=2)

    prompt = f"""
You are scoring a professional profile for an AI-native anti-portfolio called JobFitIndex.

You must evaluate the candidate on 5 criteria. For each criterion, you MUST choose
ONE score from this set: 0, 5, 10, 15, or 20. Do NOT invent other numbers.

Criteria:
1) Evidence density: How concrete, specific, and supported by proof the answers are.
2) Decision quality: How well trade-offs, options, and reasoning are explained.
3) Failure intelligence: How deeply they reflect on failures and improve their process.
4) Context translation: How well they adapt explanations for non-technical people.
5) Uniqueness signal: How clearly their unique style and differentiators emerge.

Candidate answers (JSON, keys are criterion names):
{answers_json}

INSTRUCTIONS:
- Read the answers carefully.
- For each of the 5 criteria, choose one of the scores in [0,5,10,15,20].
- Use 0 ONLY if the answers are empty, clearly non-serious, or completely off-topic for that criterion.
- If there is at least some relevant content, prefer 5 instead of 0 and go higher only when the answer is strong.
- Write a short justification (2-3 sentences) for each criterion.
- Then write a 3-sentence "signature summary" of HOW this person works.

Return ONLY a JSON object with EXACTLY this structure (no extra text):

{{
  "scores": {{
    "Evidence density": 0,
    "Decision quality": 0,
    "Failure intelligence": 0,
    "Context translation": 0,
    "Uniqueness signal": 0
  }},
  "reasons": {{
    "Evidence density": "short justification",
    "Decision quality": "short justification",
    "Failure intelligence": "short justification",
    "Context translation": "short justification",
    "Uniqueness signal": "short justification"
  }},
  "summary": "3-sentence summary"
}}
"""

    messages = [
        {
            "role": "system",
            "content": "You are a precise, structured evaluator for JobFitIndex. Always return valid JSON only.",
        },
        {
            "role": "user",
            "content": prompt,
        },
    ]

    raw = call_llm(messages, temperature=0.1, max_tokens=900)

    # Pulizia: rimuovi ```
    raw_clean = raw.strip()
    if raw_clean.startswith("```"):
        raw_clean = raw_clean.strip("`").strip()
        if raw_clean.lower().startswith("json"):
            raw_clean = raw_clean[4:].lstrip()


    # Try direct JSON parse
    try:
        result = json.loads(raw_clean)
    except json.JSONDecodeError:
        scores = {c: 0 for c in CRITERIA}
        reasons = {c: "Automatic scoring failed, defaulting to 0." for c in CRITERIA}
        summary = "Automatic scoring failed. No summary available."
        return {
            "scores": scores,
            "reasons": reasons,
            "summary": summary,
        }

    scores = result.get("scores", {})
    reasons = result.get("reasons", {})
    summary = result.get("summary", "")

    # Completa eventuali chiavi mancanti, senza floor a 5
    for c in CRITERIA:
        if c not in scores:
            scores[c] = 0
        if c not in reasons:
            reasons[c] = "No justification provided."

    return {
        "scores": scores,
        "reasons": reasons,
        "summary": summary,
    }
