# app/llm/plan.py
import json
from app.llm.client import call_llm
from app.db.plans import get_plan_for_role, save_plan_for_role


import json
from app.llm.client import call_llm
from app.db.plans import get_plan_for_role, save_plan_for_role


def generate_interview_plan(role_profile: dict, num_questions: int, use_llm: bool = True):
    role_id = role_profile.get("id")

    # Runtime: no LLM, solo cache
    if not use_llm:
        if role_id:
            cached = get_plan_for_role(role_id)
            if cached:
                return cached[:num_questions]
        return [
            {"id": i, "type": "open", "focus": f"generic_q{i}"}
            for i in range(1, num_questions + 1)
        ]

    profile_str = json.dumps(role_profile, indent=2) if role_profile else "{}"

    prompt = f"""
You create interview plans for JobFitIndex.

ROLE PROFILE:
{profile_str}

TASK:
Return ONLY a JSON array of EXACTLY {num_questions} objects.
Each object MUST have:
- "id": integer starting from 1, sequential, no gaps
- "type": one of "open", "mcq", "scale"
- "focus": short tag of what the question will explore.

DO NOT add explanations, comments, or any text outside the JSON array.

Example output for 2 questions:
[
  {{"id": 1, "type": "open", "focus": "experience_years"}},
  {{"id": 2, "type": "open", "focus": "failure_intelligence"}}
]
"""

    messages = [
        {"role": "system", "content": "Return valid JSON only."},
        {"role": "user", "content": prompt},
    ]

    raw = call_llm(messages, temperature=0.2, max_tokens=200)
    print("PLAN RAW LLM:", repr(raw))

    import re, json as _json
    try:
        plan = _json.loads(raw)
    except _json.JSONDecodeError:
        match = re.search(r"\[.*\]", raw, re.DOTALL)
        if not match:
            raise RuntimeError(f"LLM did not return JSON. Got: {raw[:200]}")
        json_str = match.group(0)
        plan = _json.loads(json_str)

    print("PLAN PARSED:", plan)

    if role_id:
        save_plan_for_role(role_id, plan)

    return plan

