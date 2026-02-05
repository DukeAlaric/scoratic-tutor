"""
Socratic Writing Tutor — v0.3 (Revision Loop)
================================================
The student doesn't just THINK about revision — they DO it.

Dialogue cycle:
  Tutor asks question → Student responds → "Great insight, now revise that part"
  → Student edits essay → Score updates → "Nice, it went from 2 to 3. Let's tackle..."
  → Next question

The essay improves IN REAL TIME during the session.
"""

import streamlit as st
import json
import os
from datetime import datetime

from core_engine import (
    TutorEngine, VALUE_RUBRIC, DialogueMode,
    StudentIntent, LearnerLevel, ScaffoldStrategy,
    MemoryManager, IntentClassifier, ScaffoldingSystem,
)
from passage_config import (
    READING_PASSAGE, WRITING_PROMPT, SCORING_ANCHORS,
    CREATIVE_CONNECTION_POLICY, EDGE_CASE_FRAMEWORK, APP_CONFIG,
)

st.set_page_config(page_title="Socratic Writing Tutor", page_icon="🏛️", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,300;8..60,400;8..60,600;8..60,700&family=DM+Sans:wght@400;500;600;700&display=swap');
    .stApp { font-family: 'DM Sans', sans-serif; }
    .tutor-header { background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%); padding: 2rem 2.5rem; border-radius: 12px; margin-bottom: 1.5rem; border-left: 5px solid #e94560; }
    .tutor-header h1 { font-family: 'Source Serif 4', Georgia, serif; color: #fff; font-size: 2rem; font-weight: 700; margin: 0 0 0.3rem 0; }
    .tutor-header p { color: #a8b2d1; font-size: 0.95rem; margin: 0; }
    .tutor-header .accent { color: #e94560; font-weight: 600; }
    .score-card { background: #fff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 1.2rem; margin-bottom: 0.8rem; }
    .score-card.weakest { border-left: 4px solid #e94560; background: #fff5f7; }
    .score-card.strong { border-left: 4px solid #38a169; background: #f0fff4; }
    .score-label { font-weight: 600; font-size: 0.85rem; color: #4a5568; text-transform: uppercase; letter-spacing: 0.05em; }
    .score-value { font-family: 'Source Serif 4', serif; font-size: 1.8rem; font-weight: 700; color: #1a1a2e; }
    .score-desc { font-size: 0.82rem; color: #718096; margin-top: 0.3rem; line-height: 1.4; }
    .socratic-q { background: linear-gradient(135deg, #1a1a2e, #16213e); color: #fff; padding: 1.3rem 1.5rem; border-radius: 10px; margin: 1rem 0; font-family: 'Source Serif 4', serif; font-size: 1.05rem; line-height: 1.6; border-left: 4px solid #e94560; }
    .revision-prompt { background: linear-gradient(135deg, #1a472a, #2d6a4f); color: #fff; padding: 1.3rem 1.5rem; border-radius: 10px; margin: 1rem 0; font-family: 'Source Serif 4', serif; font-size: 1.05rem; line-height: 1.6; border-left: 4px solid #52b788; }
    .revision-feedback { background: #f0fff4; border: 2px solid #38a169; padding: 1rem 1.3rem; border-radius: 10px; margin: 0.5rem 0 1rem; }
    .score-up { color: #38a169; font-weight: 700; font-size: 1.1rem; }
    .score-same { color: #d69e2e; font-weight: 600; }
    .student-resp { background: #f7fafc; border: 1px solid #e2e8f0; padding: 1rem 1.3rem; border-radius: 10px; margin: 0.5rem 0 1rem; font-size: 0.92rem; color: #4a5568; }
    .engine-status { background: #1a1a2e; color: #a8b2d1; padding: 0.6rem 1rem; border-radius: 8px; font-size: 0.75rem; font-family: monospace; margin: 0.5rem 0; }
    .engine-status .label { color: #e94560; font-weight: 600; }
    .phase-indicator { display: inline-block; padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; }
    .phase-write { background: #ebf4ff; color: #2b6cb0; }
    .phase-assess { background: #fef3c7; color: #92400e; }
    .phase-dialogue { background: #fed7e2; color: #97266d; }
    .phase-reflect { background: #c6f6d5; color: #276749; }
    .prompt-box { background: #f8f9fa; border: 2px solid #e2e8f0; border-radius: 10px; padding: 1.5rem; margin: 1rem 0; }
    .highlight-box { background: linear-gradient(135deg, #1a1a2e, #0f3460); color: #fff; padding: 1.5rem; border-radius: 12px; margin: 1.5rem 0; }
    .highlight-box h3 { font-family: 'Source Serif 4', serif; color: #e94560; margin-bottom: 0.5rem; }
    .footer { text-align: center; color: #a0aec0; font-size: 0.78rem; padding: 2rem 0 1rem; border-top: 1px solid #e2e8f0; margin-top: 3rem; }
</style>
""", unsafe_allow_html=True)


def get_api_key():
    """Check Streamlit secrets first, then environment variable."""
    # Streamlit Cloud secrets
    try:
        key = st.secrets.get("ANTHROPIC_API_KEY", "")
        if key:
            return key
    except Exception:
        pass
    # Environment variable (Replit, local)
    return os.environ.get("ANTHROPIC_API_KEY", "")


def make_api_call(system_prompt, user_message):
    api_key = get_api_key()
    if not api_key:
        return None
    try:
        from anthropic import Anthropic
        client = Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-sonnet-4-20250514", max_tokens=1500,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )
        return response.content[0].text
    except Exception:
        return None


# Session state
if "phase" not in st.session_state:
    st.session_state.phase = "write"
if "engine" not in st.session_state:
    has_key = bool(get_api_key())
    st.session_state.engine = TutorEngine(api_call_fn=make_api_call if has_key else None)
if "essay_text" not in st.session_state:
    st.session_state.essay_text = ""
if "assessment" not in st.session_state:
    st.session_state.assessment = None
if "current_question" not in st.session_state:
    st.session_state.current_question = ""
if "dialogue_mode" not in st.session_state:
    st.session_state.dialogue_mode = "ask"
if "revision_prompt" not in st.session_state:
    st.session_state.revision_prompt = ""
if "revision_feedback" not in st.session_state:
    st.session_state.revision_feedback = ""
if "model_text" not in st.session_state:
    st.session_state.model_text = ""


# Header
st.markdown("""<div class="tutor-header"><h1>🏛️ Socratic Writing Tutor</h1><p>Read a passage. Write your analysis. Get <span class="accent">Socratic coaching with live revision</span> — read, write, discover, revise, improve.</p></div>""", unsafe_allow_html=True)


# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    auto_key = bool(get_api_key())
    if auto_key:
        st.markdown("**Mode:** 🟢 Live (Claude) — API key detected")
    else:
        api_key_input = st.text_input("Anthropic API Key", type="password", help="Enter for live AI. Leave blank for demo mode.")
        if api_key_input:
            os.environ["ANTHROPIC_API_KEY"] = api_key_input
            st.session_state.engine.api_call_fn = make_api_call
            st.markdown("**Mode:** 🟢 Live (Claude)")
        else:
            st.markdown("**Mode:** 🟡 Demo")
    st.markdown("---")
    engine = st.session_state.engine
    memory = engine.memory
    level = memory.current_level
    st.markdown("### 🔧 Engine Status")
    mode_display = st.session_state.dialogue_mode.upper()
    st.markdown(f"**Phase:** `{st.session_state.phase}` | **Mode:** `{mode_display}`  \n**Level:** `L{level.value}` | **Focus:** `{memory.focus_dimension or 'pending'}`  \n**Turns:** `{len(memory.dialogue_history)}` | **Insights:** `{len(memory.insights_discovered)}`  \n**Revisions:** `{len(memory.essay_versions) - 1 if memory.essay_versions else 0}`  \n**Deflections:** `{memory.deflection_streak}`")
    if memory.dialogue_history:
        last = memory.dialogue_history[-1]
        st.markdown(f"**Last:** `{last.intent}` → `{last.scaffold_used}`")
    st.markdown("---")
    st.markdown("### 📐 Rubric\n**AAC&U VALUE Written Communication** (OER)\n\n[View rubric →](https://www.aacu.org/value/rubrics/value-rubrics-written-communication)")
    st.markdown("---")
    st.markdown("### 🏗️ Architecture\n**v0.5 — Ask / Model / Revise**  \nAsk → Respond → Revise → Re-score → Model if stuck → Repeat  \n\n**Three-stroke DialogueMode** with dimension cycling  \nIntentClassifier · ScaffoldingSystem · DialogueGenerator · MemoryManager")
    if st.button("🔄 Reset", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()


# === PHASE 1: READ & WRITE ===
if st.session_state.phase == "write":
    st.markdown('<span class="phase-indicator phase-write">Phase 1: Read & Respond</span>', unsafe_allow_html=True)

    # Reading passage
    st.markdown(f'### 📖 {READING_PASSAGE["title"]}')
    st.markdown(f'<div class="prompt-box">{READING_PASSAGE["body"]}</div>', unsafe_allow_html=True)
    st.caption(f'{READING_PASSAGE["word_count"]} words · {READING_PASSAGE["source_note"]}')

    st.markdown("---")

    # Writing prompt
    st.markdown(f'### ✍️ {WRITING_PROMPT["title"]}')
    st.markdown(WRITING_PROMPT["instructions"])

    essay_input = st.text_area("Your Response", height=300, placeholder="Write your analytical response here (250-400 words)...", key="essay_input")
    wc = len(essay_input.split()) if essay_input.strip() else 0
    st.caption(f"Word count: {wc}")
    if st.button("Submit for Assessment →", type="primary", disabled=(wc < 30)):
        st.session_state.essay_text = essay_input
        st.session_state.phase = "assess"
        st.rerun()


# === PHASE 2: ASSESS ===
elif st.session_state.phase == "assess":
    st.markdown('<span class="phase-indicator phase-assess">Phase 2: Feedback</span>', unsafe_allow_html=True)
    with st.spinner("Reading your response..."):
        assessment = st.session_state.engine.assess_essay(
            st.session_state.essay_text, WRITING_PROMPT["instructions"],
            scoring_anchors=SCORING_ANCHORS,
            creative_policy=CREATIVE_CONNECTION_POLICY,
            edge_case_framework=EDGE_CASE_FRAMEWORK,
            passage_text=READING_PASSAGE["body"],
        )
        st.session_state.assessment = assessment

    # Conversational overview
    avg = assessment.overall_average
    if avg >= 3.5:
        opener = "This is strong work. You clearly engaged with the passage and brought real thinking to it."
    elif avg >= 2.5:
        opener = "Good foundation here - you have ideas and you are engaging with the passage. There are some specific places where we can push this further."
    elif avg >= 1.5:
        opener = "I can see you have opinions about this topic, and that is a starting point. The main thing we need to work on is connecting your ideas to specific evidence from the passage."
    else:
        opener = "Let us dig in. The passage gave you a lot to work with, and right now your response is not using much of it. That is exactly what we will fix together."

    st.markdown(f'<div class="socratic-q" style="border-left-color: #4299e1;">💬 {opener}</div>', unsafe_allow_html=True)

    st.markdown("Here is how your response landed across five dimensions of writing:")
    st.markdown("")

    # Score walkthrough - conversational, not a grid
    for score in assessment.scores:
        is_weakest = score.dimension == assessment.weakest_dimension
        is_strongest = score.score == assessment.strongest_score

        # Score indicator
        if score.score >= 4:
            icon = "🟢"
            label = "Strong"
        elif score.score >= 3:
            icon = "🟡"
            label = "Solid"
        elif score.score >= 2:
            icon = "🟠"
            label = "Developing"
        else:
            icon = "🔴"
            label = "Needs work"

        focus_tag = " ← *this is where we will focus*" if is_weakest else ""

        st.markdown(f"**{icon} {score.dimension_name}** ({score.score}/4 - {label}){focus_tag}")
        st.markdown(f"> {score.rationale}")
        st.markdown("")

    # What happens next
    wn = VALUE_RUBRIC[assessment.weakest_dimension]["name"]
    ws = assessment.weakest_score
    dims_below = sum(1 for s in assessment.scores if s.score < 3)
    st.markdown("---")
    if dims_below == 0:
        st.markdown(f'<div class="highlight-box"><h3>Looking good!</h3><p>All your scores are at 3 or above, which is solid. We will start with <strong>{wn}</strong> ({ws}/4) since it has the most room to grow, and see if we can push it even higher.</p></div>', unsafe_allow_html=True)
    elif dims_below == 1:
        st.markdown(f'<div class="highlight-box"><h3>Where we go from here</h3><p>We will start with <strong>{wn}</strong> ({ws}/4) since that is where the most room to grow is. I will ask you some questions, you will tell me what you notice, then you will revise and watch the score update. Once that dimension is solid, we will check the others.</p></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="highlight-box"><h3>Where we go from here</h3><p>There are <strong>{dims_below} dimensions</strong> we can strengthen. We will start with <strong>{wn}</strong> ({ws}/4), work on it together until it is solid, then move to the next one. Each time you revise, the whole essay gets re-scored - so improvements in one area often lift others too.</p></div>', unsafe_allow_html=True)

    if st.button("Let's go →", type="primary"):
        q = st.session_state.engine.generate_opening_question()
        st.session_state.current_question = q
        st.session_state.dialogue_mode = "ask"
        st.session_state.phase = "dialogue"
        st.rerun()


# === PHASE 3: DIALOGUE (with revision loop) ===
elif st.session_state.phase == "dialogue":
    engine = st.session_state.engine
    memory = engine.memory
    if not memory.focus_dimension:
        st.warning("Session was reset. Starting over.")
        st.session_state.phase = "write"
        st.rerun()

    dim_name = VALUE_RUBRIC[memory.focus_dimension]["name"]
    turn = len(memory.dialogue_history)
    level = memory.current_level
    mode = st.session_state.dialogue_mode

    st.markdown(f'<span class="phase-indicator phase-dialogue">Phase 3: Dialogue & Revision — {dim_name}</span>', unsafe_allow_html=True)

    # Live score bar
    if st.session_state.assessment:
        score_parts = []
        for s in st.session_state.assessment.scores:
            if s.dimension == memory.focus_dimension:
                score_parts.append(f"→ **{s.dimension_name}: {s.score}/4**")
            elif s.score >= 3:
                score_parts.append(f"✓ {s.dimension_name}: {s.score}/4")
            else:
                score_parts.append(f"{s.dimension_name}: {s.score}/4")
        dims_done = sum(1 for s in st.session_state.assessment.scores if s.score >= 3)
        score_parts.append(f"({dims_done}/5 complete)")
        st.caption(" | ".join(score_parts))

    st.markdown(f'<div class="engine-status"><span class="label">TURN:</span> {turn + 1} | <span class="label">MODE:</span> {mode.upper()} | <span class="label">LEVEL:</span> L{level.value} | <span class="label">REVISIONS:</span> {len(memory.essay_versions) - 1}</div>', unsafe_allow_html=True)

    # Dialogue history
    for t in memory.dialogue_history:
        if t.mode == "revise":
            # Re-score framing block
            feedback_text = t.question.replace("[REVISION] ", "")
            
            # Score change indicator
            if t.score_after > t.score_before:
                score_badge = f'<span style="color: #38a169; font-weight: bold;">📈 {t.score_before}/4 → {t.score_after}/4</span>'
            elif t.score_after == t.score_before:
                score_badge = f'<span style="color: #718096;">Score held at {t.score_after}/4</span>'
            else:
                score_badge = f'<span style="color: #e67e22;">{t.score_before}/4 → {t.score_after}/4</span>'
            
            st.markdown(f'''<div style="border-left: 3px solid #4299e1; padding: 12px; margin: 8px 0; background: #f7fafc; border-radius: 4px;">
                <div style="font-size: 0.85rem; color: #718096; margin-bottom: 6px;">📊 Re-scored after revision {score_badge}</div>
                <div>✅ {feedback_text}</div>
            </div>''', unsafe_allow_html=True)
        elif t.mode == "model":
            # Model lesson block
            model_text = t.question.replace("[MODEL] ", "")
            st.markdown(f'''<div style="border-left: 3px solid #9f7aea; padding: 12px; margin: 8px 0; background: #faf5ff; border-radius: 4px;">
                <div style="font-size: 0.85rem; color: #6b46c1; margin-bottom: 6px;">💡 Example shown</div>
                <div>{model_text}</div>
            </div>''', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="socratic-q">🏛️ {t.question}</div>', unsafe_allow_html=True)
            badge = ""
            if t.intent == "insight":
                badge = " 💡"
            elif t.intent == "off_topic":
                badge = " 🔀"
            elif t.intent == "deflection":
                badge = " ↩️"
            st.markdown(f'<div class="student-resp">✍️ {t.student_response}{badge}</div>', unsafe_allow_html=True)

    # === ASK MODE ===
    if mode == "ask":
        st.markdown(f'<div class="socratic-q">🏛️ {st.session_state.current_question}</div>', unsafe_allow_html=True)
        # Clear any stale revision feedback (already shown in dialogue history above)
        st.session_state.revision_feedback = ""
        
        response_input = st.text_area("Your response:", height=120, placeholder="Think about the question...", key=f"resp_{turn}")

        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            respond = st.button("Respond →", type="primary", disabled=(not response_input.strip()))
        with col2:
            if turn >= 2:
                if st.button("Finish → Reflection"):
                    st.session_state.phase = "reflect"
                    st.rerun()
        with col3:
            st.caption(f"Turn {turn + 1}")

        if respond and response_input.strip():
            result = engine.process_response(response_input.strip(), st.session_state.current_question)

            if result["should_end"]:
                st.session_state.phase = "reflect"
            elif result["should_revise"]:
                st.session_state.revision_prompt = result["revision_prompt"]
                st.session_state.dialogue_mode = "revise"
            else:
                st.session_state.current_question = result["next_question"]
            st.rerun()

    # === MODEL MODE (brief lesson — show before/after example) ===
    elif mode == "model":
        # Show the re-score feedback first
        if st.session_state.revision_feedback:
            st.markdown(f'''<div style="border-left: 3px solid #e67e22; padding: 12px; margin: 8px 0; background: #fffbf0; border-radius: 4px;">
                <div style="font-size: 0.85rem; color: #b7791f; margin-bottom: 6px;">📊 Re-score results</div>
                <div>{st.session_state.revision_feedback}</div>
            </div>''', unsafe_allow_html=True)
            st.session_state.revision_feedback = ""

        # Show the model — the before/after example
        st.markdown(f'''<div style="border-left: 3px solid #9f7aea; padding: 16px; margin: 12px 0; background: #faf5ff; border-radius: 4px;">
            <div style="font-size: 0.9rem; font-weight: bold; color: #6b46c1; margin-bottom: 10px;">💡 Let me show you what I mean</div>
            <div>{st.session_state.model_text}</div>
        </div>''', unsafe_allow_html=True)

        with st.expander("📖 Re-read the passage"):
            st.markdown(READING_PASSAGE["body"])

        st.markdown("#### Now try it yourself — edit your response below:")
        revised_essay = st.text_area(
            "Your response (apply the pattern you just saw):", value=memory.essay_text,
            height=350, key=f"model_revision_{turn}",
        )

        changed = revised_essay.strip() != memory.essay_text.strip()
        wc = len(revised_essay.split()) if revised_essay.strip() else 0
        st.caption(f"Word count: {wc} | {'✏️ Changes detected' if changed else '⏳ Apply the pattern above to your essay'}")

        col1, col2 = st.columns([1, 1])
        with col1:
            submit_model_revision = st.button("Submit Revision →", type="primary", disabled=(not changed), key="model_submit")
        with col2:
            if st.button("Skip → Continue", key="model_skip"):
                scaffold = ScaffoldStrategy.POINT_TO_TEXT
                from core_engine import DialogueGenerator
                next_q = DialogueGenerator.generate_question(
                    memory.essay_text, memory.focus_dimension,
                    memory, scaffold, turn + 1, engine.api_call_fn,
                )
                st.session_state.current_question = next_q
                st.session_state.dialogue_mode = "ask"
                st.rerun()

        if submit_model_revision and changed:
            with st.spinner("Re-scoring your full essay..."):
                result = engine.process_revision(revised_essay.strip(), WRITING_PROMPT["instructions"])

            st.session_state.essay_text = revised_essay.strip()

            if result["should_end"]:
                st.session_state.revision_feedback = result["feedback"]
                st.session_state.phase = "reflect"
            elif result.get("trigger_model"):
                # Still stuck after model — go back to ASK with a different angle
                st.session_state.current_question = result.get("next_question", "")
                if not st.session_state.current_question:
                    from core_engine import DialogueGenerator
                    st.session_state.current_question = DialogueGenerator.generate_question(
                        revised_essay.strip(), memory.focus_dimension,
                        memory, ScaffoldStrategy.POINT_TO_TEXT, turn + 1, engine.api_call_fn,
                    )
                st.session_state.revision_feedback = result["feedback"]
                st.session_state.dialogue_mode = "ask"
            else:
                st.session_state.current_question = result["next_question"]
                st.session_state.revision_feedback = result["feedback"]
                st.session_state.dialogue_mode = "ask"
            st.rerun()

    # === REVISE MODE ===
    elif mode == "revise":
        st.markdown(f'<div class="revision-prompt">✏️ {st.session_state.revision_prompt}</div>', unsafe_allow_html=True)

        with st.expander("📖 Re-read the passage"):
            st.markdown(READING_PASSAGE["body"])

        st.markdown("#### Edit your response below:")
        revised_essay = st.text_area(
            "Your essay (edit it!):", value=memory.essay_text,
            height=350, key=f"revision_{turn}",
        )

        changed = revised_essay.strip() != memory.essay_text.strip()
        wc = len(revised_essay.split()) if revised_essay.strip() else 0
        st.caption(f"Word count: {wc} | {'✏️ Changes detected' if changed else '⏳ Make your edits above'}")

        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            submit_revision = st.button("Submit Revision →", type="primary", disabled=(not changed))
        with col2:
            if st.button("Skip revision →"):
                # Generate next question without revising
                scaffold = ScaffoldStrategy.POINT_TO_TEXT
                next_q = st.session_state.engine.memory.previous_questions
                from core_engine import DialogueGenerator
                next_q = DialogueGenerator.generate_question(
                    memory.essay_text, memory.focus_dimension,
                    memory, scaffold, turn + 1, engine.api_call_fn,
                )
                st.session_state.current_question = next_q
                st.session_state.dialogue_mode = "ask"
                st.rerun()

        if submit_revision and changed:
            with st.spinner("Re-scoring your full essay..."):
                result = engine.process_revision(revised_essay.strip(), WRITING_PROMPT["instructions"])

            st.session_state.essay_text = revised_essay.strip()

            if result["should_end"]:
                st.session_state.revision_feedback = result["feedback"]
                st.session_state.phase = "reflect"
            elif result.get("trigger_model"):
                # Score didn't move — show a model example
                st.session_state.model_text = result["model_text"]
                st.session_state.revision_feedback = result["feedback"]
                st.session_state.dialogue_mode = "model"
            else:
                st.session_state.current_question = result["next_question"]
                st.session_state.revision_feedback = result["feedback"]
                st.session_state.dialogue_mode = "ask"
            st.rerun()


# === PHASE 4: REFLECT ===
elif st.session_state.phase == "reflect":
    engine = st.session_state.engine
    memory = engine.memory
    if not memory.focus_dimension:
        st.warning("Session was reset. Starting over.")
        st.session_state.phase = "write"
        st.rerun()

    dim_name = VALUE_RUBRIC[memory.focus_dimension]["name"]
    level = memory.current_level
    summary = memory.get_session_summary()

    st.markdown(f'<span class="phase-indicator phase-reflect">Phase 4: Looking Back</span>', unsafe_allow_html=True)

    # Conversational wrap-up
    if memory.initial_assessment and memory.assessment:
        init_avg = memory.initial_assessment.overall_average
        final_avg = memory.assessment.overall_average
        delta = round(final_avg - init_avg, 2)

        if delta > 0:
            wrap_msg = f"You started at {init_avg}/4 and ended at {final_avg}/4. That is real, measurable improvement from one session - nice work."
        elif delta == 0:
            wrap_msg = f"Your overall score held steady at {final_avg}/4, but the thinking you did in dialogue matters even when the number does not move yet. Understanding what needs to change is the first step."
        else:
            wrap_msg = f"The score shifted a bit, but do not read too much into small movements. What matters more is what you learned about your own writing process."

        st.markdown(f'<div class="socratic-q" style="border-left-color: #38a169;">💬 {wrap_msg}</div>', unsafe_allow_html=True)

        # Score journey - conversational
        st.markdown("**Your scores across the session:**")
        for init_s, final_s in zip(memory.initial_assessment.scores, memory.assessment.scores):
            d = final_s.score - init_s.score
            if d > 0:
                st.markdown(f"- **{final_s.dimension_name}:** {init_s.score} to {final_s.score} 📈")
            elif d < 0:
                st.markdown(f"- **{final_s.dimension_name}:** {init_s.score} to {final_s.score} (we will get this next time)")
            else:
                st.markdown(f"- **{final_s.dimension_name}:** held at {final_s.score}/4")

    st.markdown("")
    st.markdown(f"We worked through **{summary['total_turns']} turns** of dialogue with **{summary['revision_count']} revision(s)**, focusing on **{dim_name}**.")

    # Show essays
    with st.expander("📄 Your final response"):
        st.text(memory.essay_text)
    with st.expander("📄 Your original response (for comparison)"):
        st.text(memory.original_essay)

    st.markdown("---")
    st.markdown("#### One last thing - take a minute to reflect:")
    st.markdown("What changed in your writing during this session? What did you notice about your own process? What would you do differently next time?")
    reflection = st.text_area("Your reflection:", height=150, placeholder="No wrong answers here - just think about what you learned...")

    if reflection:
        st.markdown("---")
        st.markdown("Thanks for working through this. Your reflection is part of the session data.")
        session_data = engine.export_session(reflection)
        st.download_button("📥 Download your session", data=session_data.to_json(), file_name=f"socratic_session_{engine.session_id}.json", mime="application/json")


# Footer
st.markdown('---\n<div class="footer"><strong>Socratic Writing Tutor</strong> v0.5 (Ask / Model / Revise) | AAC&U VALUE Rubric with Scoring Anchors (OER)<br>Read → Write → Discover → Model → Revise → Improve | Full re-score after every revision<br>Built by a classroom practitioner for doctoral research at American College of Education</div>', unsafe_allow_html=True)
