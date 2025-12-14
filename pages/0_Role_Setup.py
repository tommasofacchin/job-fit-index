# pages/0_Role_setup.py
import streamlit as st
from app.db.roles import init_db, add_role, list_roles, get_role, delete_role, update_role
from app.llm.plan import generate_interview_plan         
from app.db.plans import save_plan_for_role


@st.dialog("Confirm delete")
def confirm_delete_dialog(role_id: int):
    st.write("Are you sure you want to delete this role? This cannot be undone.")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Yes, delete", type="primary", use_container_width=True):
            delete_role(role_id)
            st.session_state["current_role_id"] = None
            st.session_state["role_profile"] = {}
            st.success("Role deleted.")
            st.rerun()
    with c2:
        if st.button("Cancel", use_container_width=True):
            st.rerun()


st.title("JobFitIndex – Role setup")

init_db()

if "role_profile" not in st.session_state:
    st.session_state["role_profile"] = {}
if "current_role_id" not in st.session_state:
    st.session_state["current_role_id"] = None

roles = list_roles()  # [(id, company_name, title), ...]

col_left, col_right = st.columns([1, 3])

# ---------------------------
# COLONNA SINISTRA: lista ruoli
# ---------------------------
with col_left:
    st.subheader("Existing roles")

    if st.button("Create new role", use_container_width=True):
        st.session_state["current_role_id"] = None
        st.session_state["role_profile"] = {}
        st.rerun()

    if roles:
        st.markdown("Select a role to edit:")
        current_id = st.session_state.get("current_role_id")
        for rid, company, title in roles:
            is_selected = (rid == current_id)
            label = f"**{company} – {title}**" if is_selected else f"{company} – {title}"
            clicked = st.button(
                label,
                key=f"role_btn_{rid}",
                use_container_width=True,
            )
            if clicked:
                role = get_role(rid)
                if role:
                    st.session_state["current_role_id"] = rid
                    st.session_state["role_profile"] = role
                    st.rerun()
    else:
        st.info("No roles saved yet.\nUse 'Create new role' to add one.")

# ---------------------------
# COLONNA DESTRA: dettagli ruolo
# ---------------------------
with col_right:
    role_profile = st.session_state.get("role_profile", {})

    if st.session_state["current_role_id"] is None and not role_profile:
        st.markdown("### Create a new role")
    elif st.session_state["current_role_id"] is not None:
        st.markdown(
            f"### Edit role: {role_profile.get('company_name','')} – {role_profile.get('title','')}"
        )
    else:
        st.markdown("### Role details")

    c1, c2 = st.columns(2)
    with c1:
        company_name = st.text_input(
            "Company name",
            placeholder="Acme Analytics",
            value=role_profile.get("company_name", ""),
        )
    with c2:
        title = st.text_input(
            "Role title",
            placeholder="Senior Data Scientist for growth team",
            value=role_profile.get("title", ""),
        )


    context = st.text_area(
        "Context",
        placeholder="Small cross-functional team, high uncertainty, focus on rapid experiments...",
        value=role_profile.get("context", ""),
    )

    st.subheader("Requirements")

    r1, r2 = st.columns(2)
    with r1:
        min_years_exp = st.number_input(
            "Minimum years of experience",
            min_value=0,
            max_value=40,
            value=role_profile.get("min_years_exp", 3),
            step=1,
        )
    with r2:
        degree_options = ["No", "Yes - Bachelor's", "Yes - Master's", "Yes - PhD"]
        requires_degree = st.selectbox(
            "Is a specific degree required?",
            degree_options,
            index=degree_options.index(role_profile.get("requires_degree", "No")),
        )


    required_tech = st.text_input(
        "Key tools / technologies (comma separated)",
        placeholder="SQL, Python, dbt",
        value=role_profile.get("required_tech", ""),
    )

    must_haves = st.text_area(
        "Must-have behaviors / skills",
        placeholder="- Owns experiments end-to-end\n- Communicates clearly with non-tech stakeholders\n- Comfortable with ambiguity",
        value=role_profile.get("must_haves", ""),
    )

    nice_to_have = st.text_input(
        "Nice-to-have skills",
        placeholder="Experiment design, causal inference",
        value=role_profile.get("nice_to_have", ""),
    )

    red_flags = st.text_area(
        "Red flags",
        placeholder="- Over-engineering simple problems\n- Avoids talking about failures",
        value=role_profile.get("red_flags", ""),
    )


    st.subheader("Interview settings")

    num_questions = st.slider(
        "Number of questions to ask",
        min_value=1,
        max_value=20,
        value=role_profile.get("num_questions", 5),
        step=1,
        help="Total number of AI-generated questions in the interview.",
    )

    s_left, s_right = st.columns([3, 2])
    with s_left:
        if st.session_state["current_role_id"] is not None:
            if st.button("Delete role", type="primary"):
                confirm_delete_dialog(st.session_state["current_role_id"])



    with s_right:
        if st.button("Save role profile", use_container_width=True):
            new_profile = {
                "company_name": company_name,
                "title": title,
                "context": context,
                "must_haves": must_haves,
                "red_flags": red_flags,
                "num_questions": num_questions,
                "min_years_exp": min_years_exp,
                "required_tech": required_tech,
                "nice_to_have": nice_to_have,
                "requires_degree": requires_degree,
            }

            current_id = st.session_state.get("current_role_id")
            if current_id is not None:
                update_role(current_id, new_profile)
                new_profile["id"] = current_id

                try:
                    plan = generate_interview_plan(new_profile, num_questions, use_llm=True)
                    st.write("DEBUG plan generated:", plan)
                    save_plan_for_role(current_id or role_id, plan)

                    save_plan_for_role(current_id, plan)
                except RuntimeError as e:
                    st.warning(f"Role updated, but plan generation failed: {e}")

                # assicura che resti selezionato
                st.session_state["role_profile"] = new_profile
                st.session_state["current_role_id"] = current_id
                st.success("Role profile updated.")
            else:
                role_id = add_role(new_profile)
                new_profile["id"] = role_id

                try:
                    plan = generate_interview_plan(new_profile, num_questions, use_llm=True)
                    st.write("DEBUG plan generated:", plan)
                    save_plan_for_role(current_id or role_id, plan)

                    save_plan_for_role(role_id, plan)
                except RuntimeError as e:
                    st.warning(f"Role saved, but plan generation failed: {e}")

                st.session_state["role_profile"] = new_profile
                st.session_state["current_role_id"] = role_id
                st.success("Role profile saved. You can now run the interview.")






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