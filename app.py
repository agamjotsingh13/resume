from html import escape
from pathlib import Path

import streamlit as st

from Src.career_assistant import generate_career_advice
from Src.resume_analyzer import analyze_resume
from Src.resume_reader import read_pdf_file
from Src.resume_utils import skill_label


st.set_page_config(
    page_title="Resume Intelligence",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

CSS_FILE = Path(__file__).parent / "assets" / "style.css"
st.markdown(f"<style>{CSS_FILE.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

EXAMPLE_QUESTIONS = [
    "Which skills should I learn next?",
    "Why was this role recommended?",
    "What project should I build?",
]

ICONS = {
    "score": '<path d="M4 18a8 8 0 1 1 16 0"/><path d="m12 13 4-4"/><path d="M12 4v2"/>',
    "skills": '<path d="m12 3 2.8 5.7 6.2.9-4.5 4.4 1.1 6.2-5.6-3-5.6 3 1.1-6.2L3 9.6l6.2-.9z"/>',
    "roles": '<rect x="3" y="7" width="18" height="14" rx="2"/><path d="M8 7V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M3 12h18"/>',
}


def safe_text(value):
    return escape(str(value)).replace("$", "&#36;")


def show_html(markup):
    st.markdown(markup, unsafe_allow_html=True)


def icon(name, size=18):
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
        f'stroke="currentColor" stroke-width="1.7" stroke-linecap="round" '
        f'stroke-linejoin="round" aria-hidden="true">{ICONS[name]}</svg>'
    )


def skill_chips(skills, kind=""):
    if not skills:
        return "<span class='ri-none'>None listed</span>"
    return "".join(
        f"<span class='ri-chip {kind}'>{safe_text(skill_label(skill))}</span>"
        for skill in skills
    )


def score_bar(score):
    width = max(0.0, min(float(score), 100.0))
    return (
        "<div class='ri-bar' role='progressbar' aria-valuemin='0' aria-valuemax='100' "
        f"aria-valuenow='{width:.0f}'><div style='width:{width:.1f}%'></div></div>"
    )


def section_heading(title, count=None):
    detail = f"<span>{safe_text(count)}</span>" if count is not None else ""
    show_html(
        f"<div class='ri-section-heading'><h2>{safe_text(title)}</h2>{detail}</div>"
    )


def metric_card(icon_name, label, value, suffix=""):
    unit = f"<small>{safe_text(suffix)}</small>" if suffix else ""
    return (
        f"<div class='ri-stat'><div class='ri-stat-top'>{icon(icon_name)}"
        f"<span>{safe_text(label)}</span></div>"
        f"<div class='ri-stat-value'>{safe_text(value)}{unit}</div></div>"
    )


def best_match_card(recommendation):
    matched = recommendation["matched_skills"]
    missing = recommendation["missing_skills"]
    score = max(0.0, min(float(recommendation["score"]), 100.0))
    show_html(
        "<div class='ri-top-match'>"
        "<div class='ri-top-match-content'><span class='ri-overline'>YOUR STRONGEST MATCH</span>"
        f"<h3>{safe_text(recommendation['job'])}</h3>"
        f"<p>{len(matched)} matching skills in your current profile</p></div>"
        f"<div class='ri-score-dial' style='--progress:{score:.1f}%'>"
        f"<div class='ri-score-dial-inner'><strong>{score:.0f}<small>%</small></strong>"
        "<span>match</span></div></div></div>"
        "<div class='ri-match-details'>"
        f"<div class='ri-match-group'><span>Skills you have</span><div>{skill_chips(matched[:8], 'match')}</div></div>"
        f"<div class='ri-match-group'><span>Skills to build</span><div>{skill_chips(missing[:8], 'gap')}</div></div>"
        "</div>"
    )


def role_details(recommendation):
    left, right = st.columns(2, gap="medium")
    with left:
        show_html(
            f"<div class='ri-detail-label'>MATCHING SKILLS</div>"
            f"<div class='ri-chip-wrap'>{skill_chips(recommendation['matched_skills'], 'match')}</div>"
        )
    with right:
        show_html(
            f"<div class='ri-detail-label'>SKILLS TO BUILD</div>"
            f"<div class='ri-chip-wrap'>{skill_chips(recommendation['missing_skills'], 'gap')}</div>"
        )


def get_resume_text(uploaded_file, pasted_text):
    if uploaded_file is not None:
        filename = uploaded_file.name.lower()
        if filename.endswith(".pdf"):
            return read_pdf_file(uploaded_file)
        if filename.endswith(".txt"):
            return uploaded_file.getvalue().decode("utf-8", errors="ignore")
    return pasted_text


def answer_question():
    question = st.session_state.get("question", "").strip()
    result = st.session_state.get("result")
    if not question:
        st.session_state.assistant = {"error": "Write a question first."}
        return
    if not result or not result.get("recommendations"):
        st.session_state.assistant = {"error": "Analyze a resume first."}
        return
    st.session_state.assistant = {
        "question": question,
        "answer": generate_career_advice(question, result),
    }


def ask_example(question):
    st.session_state.question = question
    answer_question()


st.session_state.setdefault("result", None)
st.session_state.setdefault("assistant", None)
st.session_state.setdefault("question", "")
st.session_state.setdefault("input_mode", "Upload a file")

show_html(
    "<header class='ri-topbar'><div class='ri-brand-symbol'>ri</div>"
    "<div class='ri-brand-name'>Resume Intelligence</div>"
    "<div class='ri-topbar-label'>RESUME ANALYSIS</div></header>"
)

with st.container(key="landing_grid"):
    intro_column, form_column = st.columns([1.12, 0.88], gap="large")

    with intro_column:
        show_html(
            "<section class='ri-hero'><div class='ri-hero-copy'>"
            "<div class='ri-eyebrow'>RESUME ANALYSIS / CAREER TOOLS</div>"
            "<h1><span>RESUME</span><span class='ri-title-accent'>INTELLIGENCE</span></h1>"
            "<p>Review your skills, explore relevant job roles, and find what to develop next.</p>"
            "</div></section>"
        )

    with form_column:
        with st.container(key="input_card"):
            show_html(
                "<div class='ri-card-head'><div><h2>Analyze your resume</h2>"
                "<p>PDF or TXT file, or paste your text</p></div></div>"
            )
            input_mode = st.radio(
                "Resume input",
                ["Upload a file", "Paste text"],
                horizontal=True,
                label_visibility="collapsed",
                key="input_mode",
            )
            uploaded_file = None
            pasted_text = ""
            if input_mode == "Upload a file":
                uploaded_file = st.file_uploader(
                    "Choose a resume",
                    type=["pdf", "txt"],
                    label_visibility="collapsed",
                    help="Text-based PDFs work best.",
                )
            else:
                pasted_text = st.text_area(
                    "Resume text",
                    height=174,
                    placeholder="Paste the text from your resume here…",
                    label_visibility="collapsed",
                    key="pasted_resume",
                )
            analyze_clicked = st.button("Analyze resume  ↗", type="primary", use_container_width=True)

show_html(
    "<section class='ri-feature-strip' aria-label='What the review covers'>"
    "<div class='ri-feature'><span class='ri-feature-index'>01</span><div><strong>Skills</strong><span>Identify skills in your resume</span></div></div>"
    "<div class='ri-feature'><span class='ri-feature-index'>02</span><div><strong>Role matches</strong><span>Compare relevant job profiles</span></div></div>"
    "<div class='ri-feature'><span class='ri-feature-index'>03</span><div><strong>Next steps</strong><span>See where to build further</span></div></div>"
    "</section>"
)

if analyze_clicked:
    st.session_state.result = None
    st.session_state.assistant = None
    st.session_state.question = ""
    try:
        resume_text = get_resume_text(uploaded_file, pasted_text)
    except Exception:
        resume_text = None
        st.error("This file could not be read. Try another file or paste the resume text.")

    if resume_text is not None:
        if resume_text.strip():
            with st.spinner("Reviewing your resume…"):
                try:
                    st.session_state.result = analyze_resume(resume_text)
                except (FileNotFoundError, ValueError, OSError) as error:
                    st.error(f"The review could not be completed: {error}")
                except Exception:
                    st.error("The review could not be completed. Check the project files and try again.")
        elif uploaded_file is not None:
            st.warning("No readable text was found. Try a text-based PDF or paste the resume text.")
        else:
            st.warning("Add a PDF/TXT file or paste your resume text first.")

result = st.session_state.result

if result and result.get("recommendations"):
    recommendations = result["recommendations"]
    show_html("<div class='ri-results-rule'></div>")
    section_heading("Your resume snapshot")
    show_html(
        "<div class='ri-stats'>"
        + metric_card("score", "Resume score", f"{result['resume_score']:g}", "/ 100")
        + metric_card("skills", "Skills found", result["total_skills"])
        + metric_card("roles", "Roles compared", len(recommendations))
        + "</div>"
    )
    section_heading("Best fit")
    best_match_card(recommendations[0])

    matches_tab, skills_tab, career_tab = st.tabs(["Role matches", "Skills & growth", "Career Q&A"])

    with matches_tab:
        section_heading("Explore roles", f"TOP {min(len(recommendations), 5)}")
        for rank, recommendation in enumerate(recommendations[1:5], start=2):
            title = f"{rank:02d}   {recommendation['job']}"
            with st.expander(title, expanded=False):
                show_html(
                    "<div class='ri-role-summary'>"
                    f"<div class='ri-role-summary-score'>{recommendation['score']:.0f}%</div>"
                    f"<div class='ri-role-summary-info'><strong>Skill match</strong>{score_bar(recommendation['score'])}</div>"
                    "</div>"
                )
                role_details(recommendation)

    with skills_tab:
        skill_column, growth_column = st.columns([1.15, 0.85], gap="large")
        with skill_column:
            section_heading("Skills in your resume", len(result["skills"]))
            show_html(
                f"<div class='ri-skill-card'><div class='ri-chip-wrap'>{skill_chips(result['skills'])}</div></div>"
                if result["skills"]
                else "<div class='ri-empty'>No recognised skills found in this resume yet.</div>"
            )
        with growth_column:
            section_heading("Worth building next", len(result["improvement_skills"]))
            if result["improvement_skills"]:
                items = "".join(
                    f"<li><span>{index:02d}</span><strong>{safe_text(skill_label(skill))}</strong></li>"
                    for index, skill in enumerate(result["improvement_skills"], start=1)
                )
                show_html(f"<div class='ri-growth-card'><ul>{items}</ul></div>")
            else:
                show_html("<div class='ri-empty'>No skill gaps surfaced in the top roles.</div>")

    with career_tab:
        show_html(
            "<div class='ri-career-head'><span class='ri-career-symbol'>↗</span>"
            "<div><h3>Think through your next step.</h3>"
            "<p>Ask about your matches, skills or projects.</p></div></div>"
        )
        st.text_input(
            "Ask a career question",
            key="question",
            placeholder="What should I focus on next?",
            label_visibility="collapsed",
        )
        st.button("Get guidance  ↗", type="primary", on_click=answer_question)
        quick_columns = st.columns(3, gap="small")
        quick_labels = ["Next skills", "Why this role?", "Project idea"]
        for column, label, question in zip(quick_columns, quick_labels, EXAMPLE_QUESTIONS):
            column.button(
                label,
                key=f"quick_{label}",
                on_click=ask_example,
                args=(question,),
                use_container_width=True,
            )
        assistant = st.session_state.assistant
        if assistant and "error" in assistant:
            st.warning(assistant["error"])
        elif assistant:
            show_html(
                "<div class='ri-answer-card'>"
                f"<div class='ri-answer-question'>{safe_text(assistant['question'])}</div>"
                f"<p>{safe_text(assistant['answer'])}</p></div>"
            )
elif result:
    st.warning("No job profiles were available to compare. Check the job profile file in the models folder.")

show_html(
    "<footer class='ri-footer'><span class='ri-footer-brand'>ri<span>.</span> Resume Intelligence</span>"
    "<span>Career profile workspace</span></footer>"
)
