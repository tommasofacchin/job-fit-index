# pages/1_Interview.py
import streamlit as st
from app.llm.questions import generate_next_question, generate_questions_batch
from app.llm.plan import generate_interview_plan
from app.llm.judge import evaluate_answers_with_llama
from app.db.roles import list_roles, get_role
from app.db.plans import init_plans_db
from app.db.evaluations import init_evaluations_db, save_evaluation

init_plans_db()
init_evaluations_db()


@st.dialog("Interview completed")
def interview_done_dialog():
    st.write("The interview is complete. The score report is being generated.")
    if st.button("OK", use_container_width=True, key="confirm_interview_done"):
        for key in [
            "role_profile", "candidate", "plan", "messages", "step", "answers",
            "current_question", "current_options", "current_q_type", "current_focus",
            "evaluation", "evaluation_error"
        ]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()


# ---------------------------
# Selezione ruolo (lista interviste)
# ---------------------------

st.title("Interview")

if "role_profile" not in st.session_state:
    st.session_state["role_profile"] = {}

# Se non c'è ancora un ruolo scelto, mostra solo la lista
if not st.session_state["role_profile"]:
    st.subheader("Select a role to start an interview")

    roles = list_roles()
    if not roles:
        st.info("No roles available. Go to Role setup to create one.")
        st.stop()

    for rid, company, title in roles:
        if st.button(f"{company} – {title}", key=f"start_role_{rid}", use_container_width=True):
            role = get_role(rid)
            if role:
                st.session_state["role_profile"] = role
                st.rerun()

    st.stop()

# ---------------------------
# Candidate basic info (pre-screen)
# ---------------------------

if "candidate" not in st.session_state:
    st.session_state["candidate"] = {}

candidate = st.session_state["candidate"]
role_profile = st.session_state.get("role_profile", {})

company = role_profile.get("company_name") or "Company"
title = role_profile.get("title") or "Role"

# Titolo + bottone back sulla stessa riga
h_col, b_col = st.columns([4, 1])
with h_col:
    st.title(f"{company} – {title}")
with b_col:
    if st.button("← Back", key="back_to_role_list", use_container_width=True):
        for key in [
            "role_profile", "candidate", "plan", "messages", "step", "answers",
            "current_question", "current_options", "current_q_type", "current_focus"
        ]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

# Form candidato
if not candidate:
    st.subheader("Candidate basic info")

    name = st.text_input("Full name")
    email = st.text_input("Email")
    phone = st.text_input("Phone number")
    years_exp = st.number_input(
        "Years of experience (overall)",
        min_value=0,
        max_value=50,
        value=0,
        step=1,
    )
    tools_used = st.text_input(
        "Key tools you have used",
        placeholder="Figma, Photoshop, Python, SQL, ...",
    )

    if st.button("Start interview", key="start_interview"):
        st.session_state["candidate"] = {
            "name": name,
            "email": email,
            "phone": phone,
            "years_exp": int(years_exp),
            "tools": tools_used,
        }
        st.rerun()

candidate = st.session_state["candidate"]
if not candidate:
    st.stop()

# ---------------------------
# Setup and role context
# ---------------------------

if "role_profile" not in st.session_state:
    st.session_state["role_profile"] = {}

role_profile = st.session_state["role_profile"]

company = role_profile.get("company_name") or "Company"
title = role_profile.get("title") or "Role"

# ---------------------------
# State init for chat
# ---------------------------

if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "step" not in st.session_state:
    st.session_state["step"] = 0
if "answers" not in st.session_state:
    st.session_state["answers"] = {}

def add_ai_message(content: str):
    st.session_state["messages"].append({"role": "assistant", "content": content})

def add_user_message(content: str):
    st.session_state["messages"].append({"role": "user", "content": content})

# ---------------------------
# Start interview
# ---------------------------

num_questions = role_profile.get("num_questions", 5)

if "plan" not in st.session_state:
    # Plan leggero: id/type/focus
    base_plan = generate_interview_plan(role_profile, num_questions, use_llm=False)
    # Una sola chiamata LLM per generare tutte le domande
    questions_plan = generate_questions_batch(base_plan, role_profile, answers={})
    st.session_state["plan"] = questions_plan

plan = st.session_state["plan"]
max_steps = len(plan)

st.write(f"DEBUG max_steps = {max_steps}, plan length = {len(plan)}")
st.write(f"DEBUG current step = {st.session_state['step']}")



if st.session_state["step"] == 0:
    intro_text = (
        "Welcome to JobFitIndex. This interview is tailored to this specific role "
        "and company. We will focus on how you work, not just what you did."
    )
    add_ai_message(intro_text)
    st.session_state["step"] = 1

# ---------------------------
# Render chat history
# ---------------------------

for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------------------------
# Render current question + input widget
# ---------------------------

current_step = st.session_state["step"]
if 1 <= current_step <= max_steps:
    slot = plan[current_step - 1]
    q_type = slot["type"]
    focus = slot["focus"]
    question = slot["question"]


    with st.chat_message("assistant"):
        st.markdown(f"**{question}**")

    answer_value = None

    if q_type == "open":
        answer_value = st.chat_input("Type your answer here...")
    elif q_type == "mcq":
        lines = question.splitlines()
        opts = [line.strip() for line in lines if line.strip().startswith(("A)", "B)", "C)", "D)"))]
        options_clean = [opt[2:].strip() for opt in opts] if opts else []
        st.session_state["current_options"] = options_clean

        if options_clean:
            selected = st.radio(
                "Select one option:",
                options_clean,
                index=0,
                key=f"mcq_{current_step}",
            )
            if st.button("Submit answer", key=f"submit_mcq_{current_step}"):
                answer_value = selected
        else:
            answer_value = st.chat_input("Type your answer here...")
    elif q_type == "scale":
        scale_value = st.slider(
            "Select a value from 1 to 10:",
            min_value=1,
            max_value=10,
            value=7,
            key=f"scale_{current_step}",
        )
        if st.button("Submit answer", key=f"submit_scale_{current_step}"):
            answer_value = str(scale_value)

        # ---------------------------
    # Handle answer and move on
    # ---------------------------

    if answer_value is not None and answer_value != "":
        # salva risposta
        add_user_message(answer_value)
        st.session_state["answers"][focus] = answer_value

        # passa allo step successivo o chiudi
        if current_step < max_steps:
            st.session_state["step"] = current_step + 1
            st.rerun()  
        else:
            add_ai_message(
                "The interview is complete. The score report is being generated in the background."
            )
            with st.spinner("Calculating score..."):
                try:
                    result = evaluate_answers_with_llama(st.session_state["answers"])
                    st.session_state["evaluation"] = result

                    role_id = st.session_state["role_profile"].get("id")
                    candidate = st.session_state.get("candidate", {})

                    save_evaluation(
                        role_id=role_id,
                        candidate=candidate,
                        answers=st.session_state["answers"],
                        scores=result["scores"],
                        summary=result["summary"],
                    )
                except RuntimeError as e:
                    st.session_state["evaluation_error"] = str(e)

            st.session_state["step"] = max_steps + 1
            interview_done_dialog()


# Stile
st.markdown(
    """
    <style>
    .block-container {
        max-width: 75%;
        margin-left: auto;
        margin-right: auto;
    }
    button[kind="primary"] {
        background-color: #d9534f;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
