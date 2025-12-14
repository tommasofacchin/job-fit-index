# app/llm/questions.py
import json
import streamlit as st
from app.llm.client import call_llm


def generate_next_question(
    criterion: str,
    answers: dict,
    role_profile: dict,
    question_type: str = "open",
) -> str:
    """
    Ask the LLM to generate the next interview question for a specific criterion,
    tailored to the given role profile, candidate info, and previous answers.

    question_type: "open", "mcq", or "scale".
    """

    profile_str = json.dumps(role_profile, indent=2) if role_profile else "{}"
    answers_str = json.dumps(answers, indent=2)

    min_years = role_profile.get("min_years_exp")
    required_tech = (role_profile.get("required_tech") or "").strip()
    requires_degree = role_profile.get("requires_degree", "No")
    seniority = role_profile.get("seniority", "")
    role_title = role_profile.get("title", "")
    company = role_profile.get("company_name", "")

    candidate = st.session_state.get("candidate", {})
    candidate_str = json.dumps(candidate, indent=2)

    # Flags (if we ever want to use them programmatically)
    has_required_tech = bool(required_tech)
    requires_degree_flag = (requires_degree != "No")

    # Format instructions per question type
    if question_type == "mcq":
        format_instructions = (
            "Format the question as multiple-choice with 3-5 options.\n"
            "The options must represent realistic, different ways someone in THIS ROLE might behave.\n"
            "Return ONLY the question and options in this format:\n"
            "Question: <text>\n"
            "A) <option>\n"
            "B) <option>\n"
            "C) <option>\n"
            "D) <option> (optional)\n"
        )
    elif question_type == "scale":
        format_instructions = (
            "Format the question for a 1-10 scale answer.\n"
            "Make clear what 1 and 10 mean in the context of THIS ROLE.\n"
            "Return ONLY the question text, mentioning the 1-10 scale clearly.\n"
        )
    else:
        format_instructions = (
            "Ask ONE open-ended question that is specific, concrete, and asks for a real example.\n"
            "Anchor the scenario in the actual day-to-day of THIS ROLE and THIS COMPANY when possible.\n"
            "Return ONLY the question text, nothing else.\n"
        )

    prompt = f"""
You are an interview assistant for an AI-native anti-portfolio called JobFitIndex.
You design questions to reveal HOW a candidate works, tailored to the role profile and to what they already said.

ROLE PROFILE (JSON):
{profile_str}

CANDIDATE BASIC INFO (JSON):
{candidate_str}

CURRENT CRITERION TO EXPLORE:
{criterion}

PREVIOUS ANSWERS (JSON, may be empty):
{answers_str}

REQUIREMENT FLAGS:
- Minimum years of experience: {min_years}
- Required technologies (comma separated): "{required_tech}"
- Degree requirement: "{requires_degree}"

STRICT RULES ABOUT TOPICS:
- Only ask about specific tools or technologies if they appear in required_tech.
- Only ask about degrees or education if requires_degree is not "No".
- Do NOT assume the candidate meets any requirement; ask factual questions first if needed.
- Avoid generic questions like "Tell me about yourself".
- Avoid repeating topics that are already clearly answered in PREVIOUS ANSWERS or CANDIDATE BASIC INFO.

PERSONALIZATION RULES:
- You MUST adapt the question to this specific role (title: "{role_title}", seniority: "{seniority}", company: "{company}").
- The question should NOT make sense if copied to a very different role; use role-specific responsibilities, domain, and stack.
- When possible, reference 1–2 concrete elements from ROLE PROFILE (e.g., key technologies, responsibilities, stakeholders).
- Use PREVIOUS ANSWERS to go one level deeper: prefer follow-ups that reference what the candidate already said.
- If the candidate mentioned a project or situation before, reuse it and explore a different angle (e.g., decision, failure, collaboration).
- Vary the shape of the question for the same criterion across different roles (e.g., data pipelines vs. UX flows vs. GTM experiments).

QUESTION TYPE REQUESTED:
{question_type}

OUTPUT FORMAT:
{format_instructions}
"""

    messages = [
        {
            "role": "system",
            "content": (
                "You are a sharp, role-aware interview question generator for JobFitIndex. "
                "Always follow instructions exactly and do not add explanations."
            ),
        },
        {
            "role": "user",
            "content": prompt,
        },
    ]

    return call_llm(messages, temperature=0.6, max_tokens=220)


def generate_questions_batch(plan: list, role_profile: dict, answers: dict | None = None) -> list:
    """
    Prende il plan (lista di slot con id/type/focus) e genera una domanda testuale per ogni slot
    in UNA sola chiamata LLM. Ritorna una nuova lista di slot con anche "question".
    """
    profile_str = json.dumps(role_profile, indent=2) if role_profile else "{}"
    plan_str = json.dumps(plan, indent=2)
    answers_str = json.dumps(answers or {}, indent=2)

    prompt = f"""
You are an interview assistant for JobFitIndex.

ROLE PROFILE (JSON):
{profile_str}

INTERVIEW PLAN (JSON, without question text yet):
{plan_str}

PREVIOUS ANSWERS (JSON, may be empty):
{answers_str}

TASK:
For each item in the INTERVIEW PLAN, fill in a concrete, short "question" field.
Return ONLY a JSON array with the same objects but with an extra "question" key in each.

Rules:
- Question must be 1-2 sentences.
- Must be specific to this role and company.
- Use "type" and "focus" to shape the question.
- Do NOT add or remove items.
"""

    messages = [
        {
            "role": "system",
            "content": "You return valid JSON only. You keep the same list length and ids.",
        },
        {"role": "user", "content": prompt},
    ]

    raw = call_llm(messages, temperature=0.4, max_tokens=600)
    questions_plan = json.loads(raw)
    return questions_plan
