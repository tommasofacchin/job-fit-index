# pages/2_Score_Report.py
import json
import streamlit as st
from app.db.evaluations import init_evaluations_db, list_evaluations, get_evaluation

st.title("Score Report")

CRITERIA = [
    "Evidence density",
    "Decision quality",
    "Failure intelligence",
    "Context translation",
    "Uniqueness signal",
]

init_evaluations_db()

if "current_eval_id" not in st.session_state:
    st.session_state["current_eval_id"] = None

evals = list_evaluations()

col_left, col_right = st.columns([1, 3])

# ---------------------------
# COLONNA SINISTRA: lista evaluation
# ---------------------------
with col_left:
    st.subheader("Past evaluations")

    if not evals:
        st.info("No evaluations yet. Complete an interview first.")
    else:
        for eid, created_at, role_id, name, email, phone in evals:
            label = f"{name or 'Unknown'} – {created_at.split(' ')[0]}"
            if st.button(label, key=f"eval_btn_{eid}", use_container_width=True):
                st.session_state["current_eval_id"] = eid
                st.rerun()

# ---------------------------
# COLONNA DESTRA: dettaglio score
# ---------------------------
with col_right:
    eval_id = st.session_state.get("current_eval_id")

    if eval_id is None:
        st.markdown("### Select an evaluation to view details")
    else:
        ev = get_evaluation(eval_id)
        if not ev:
            st.warning("Selected evaluation not found.")
        else:
            scores = json.loads(ev["scores_json"])
            summary = ev["summary"]

            total = sum(scores.get(c, 0) for c in CRITERIA)
            st.markdown(
                f"### Candidate: {ev['candidate_name'] or 'Unknown'}  \n"
                f"Email: {ev['candidate_email'] or '-'}  \n"
                f"Phone: {ev['candidate_phone'] or '-'}"
            )
            st.subheader(f"Total score: {total} / 100")

            for crit in CRITERIA:
                s = scores.get(crit, 0)
                st.markdown(f"**{crit}**: {s} / 20")
                st.progress(s / 20)

            st.markdown("### Signature summary")
            st.write(summary)

                        # --- genera markdown anti-portfolio ---
            md = f"""# JobFitIndex Anti-Portfolio – Score Report

## Candidate
- Name: {ev['candidate_name'] or '-'}
- Email: {ev['candidate_email'] or '-'}
- Phone: {ev['candidate_phone'] or '-'}

## Impronta professionale (signature summary)
{summary}

## Score breakdown
Total score: {total} / 100

"""  # chiudo f-string

            for crit in CRITERIA:
                s = scores.get(crit, 0)
                md += f"- {crit}: {s} / 20\n"

            md += """

## Come usare questo anti-portfolio
Questo documento è generato da JobFitIndex a partire da un'intervista strutturata.
Mette in evidenza pattern decisionali, densità di evidenze e segnali di unicità,
invece di limitarsi a job title e lista di esperienze.
"""

            st.download_button(
                label="Download report (.md)",
                data=md,
                file_name=f"jobfitindex_anti_portfolio_{ev['candidate_name'] or 'candidate'}.md",
                mime="text/markdown",
            )


# Stile container
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
