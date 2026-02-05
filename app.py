"""
Socratic Writing Tutor v0.6 — Streamlit App
Fixes: revision count, interactive reflection, dedup, dimension cycling
"""

import streamlit as st
import json
import os
from datetime import datetime

from core_engine import (
    TutorEngine, VALUE_RUBRIC, DIMENSION_ORDER, TARGET_SCORE, MemoryManager
)
from passage_config import (
    READING_PASSAGE, WRITING_PROMPT, SCORING_ANCHORS,
    EDGE_CASE_FRAMEWORK, CREATIVE_CONNECTION_POLICY
)

# --- PAGE CONFIG ---
st.set_page_config(page_title="Socratic Writing Tutor", page_icon="🏛️", layout="wide")

# --- SESSION STATE INIT ---
if "engine" not in st.session_state:
    st.session_state.engine = None
if "phase" not in st.session_state:
    st.session_state.phase = 1
if "essay" not in st.session_state:
    st.session_state.essay = ""
if "current_question" not in st.session_state:
    st.session_state.current_question = ""
if "dialogue_mode" not in st.session_state:
    st.session_state.dialogue_mode = "ask"
if "model_data" not in st.session_state:
    st.session_state.model_data = None
if "reflection_history" not in st.session_state:
    st.session_state.reflection_history = []  # list of (role, text) tuples
if "session_exported" not in st.session_state:
    st.session_state.session_exported = False

# --- API KEY HANDLING ---
api_key = None
try:
    api_key = st.secrets.get("ANTHROPIC_API_KEY")
except Exception:
    pass

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Settings")

    if not api_key:
        api_key_input = st.text_input("Anthropic API Key", type="password",
                                       help="Paste your key for live Claude responses")
        if api_key_input:
            api_key = api_key_input

    if api_key:
        st.success("🟢 Live Mode (Claude)")
    else:
        st.warning("🟡 Demo Mode (pre-written responses)")

    st.divider()

    # Engine telemetry
    if st.session_state.engine:
        memory = st.session_state.engine.memory
        st.subheader("📊 Engine Status")
        st.caption(f"Level: L{memory.current_level}")
        st.caption(f"Revisions: {memory.revision_count}")
        st.caption(f"Insights: {len(memory.insights_found)}")
        if memory.focus_dimension and memory.focus_dimension in VALUE_RUBRIC:
            st.caption(f"Focus: {VALUE_RUBRIC[memory.focus_dimension]['name']}")

        # Dimension status
        scores = memory.get_current_scores()
        if scores:
            st.divider()
            for dim in DIMENSION_ORDER:
                score = scores.get(dim, 0)
                name = VALUE_RUBRIC[dim]["short"]
                if dim in memory.completed_dimensions or score >= TARGET_SCORE:
                    st.caption(f"✅ {name}: {score}/4")
                elif dim == memory.focus_dimension:
                    st.caption(f"➡️ {name}: {score}/4")
                else:
                    st.caption(f"⬜ {name}: {score}/4")

    st.divider()
    if st.button("🔄 Reset Session"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    st.caption("v0.6 | SOAR + MODEL + Interactive Reflection")

# --- INIT ENGINE ---
if st.session_state.engine is None:
    if api_key:
        try:
            from anthropic import Anthropic
            client = Anthropic(api_key=api_key)
            st.session_state.engine = TutorEngine(api_client=client)
        except Exception:
            st.session_state.engine = TutorEngine()
    else:
        st.session_state.engine = TutorEngine()

engine = st.session_state.engine

# --- HEADER ---
st.title("🏛️ Socratic Writing Tutor")
st.caption("Read a passage. Write your analysis. Get coached through revision.")

# ═══════════════════════════════════════════════════════════════
# PHASE 1: READ & WRITE
# ═══════════════════════════════════════════════════════════════
if st.session_state.phase == 1:
    st.subheader("📖 Phase 1: Read & Write")

    with st.expander("📄 Reading Passage", expanded=True):
        st.markdown(READING_PASSAGE)

    st.markdown(WRITING_PROMPT)

    essay = st.text_area("Your response:", height=300,
                          placeholder="Write your analytical response here...",
                          key="essay_input")

    if st.button("Submit for Assessment →", type="primary", disabled=len(essay.strip()) < 20):
        st.session_state.essay = essay.strip()
        with st.spinner("Reading your essay..."):
            engine.assess_essay(
                essay.strip(),
                scoring_anchors=SCORING_ANCHORS,
                edge_case_framework=EDGE_CASE_FRAMEWORK,
                creative_policy=CREATIVE_CONNECTION_POLICY,
                passage_text=READING_PASSAGE
            )
        st.session_state.phase = 2
        st.rerun()

# ═══════════════════════════════════════════════════════════════
# PHASE 2: ASSESSMENT
# ═══════════════════════════════════════════════════════════════
elif st.session_state.phase == 2:
    st.subheader("📋 Phase 2: Your Writing Assessment")
    memory = engine.memory
    assessment = memory.assessment

    if assessment:
        avg = assessment.overall_average
        if avg >= 3.5:
            st.markdown(f"**Overall: {avg}/4** — Strong foundation here. Let's make it even sharper.")
        elif avg >= 2.5:
            st.markdown(f"**Overall: {avg}/4** — Good start. There are some clear spots where we can strengthen this.")
        else:
            st.markdown(f"**Overall: {avg}/4** — You have ideas here, and that is the hardest part. Let's work on expressing them more effectively.")

        st.divider()

        for dim in DIMENSION_ORDER:
            score_obj = assessment.scores.get(dim)
            if not score_obj:
                continue
            name = VALUE_RUBRIC[dim]["name"]
            score = score_obj.score
            is_focus = (dim == assessment.weakest_dimension)

            if score >= 4:
                icon = "🟢"
            elif score >= 3:
                icon = "🟡"
            else:
                icon = "🔴"

            label = f" ← **We will work on this first**" if is_focus else ""
            st.markdown(f"{icon} **{name}: {score}/4**{label}")
            st.markdown(f"> {score_obj.rationale}")
            st.markdown("")

        # Count dimensions below target
        below_target = [d for d in DIMENSION_ORDER if assessment.scores[d].score < TARGET_SCORE]
        if below_target:
            st.info(f"We have {len(below_target)} dimension(s) to strengthen. We will work through each one — and every time you revise, the whole essay gets re-scored, so improvements in one area often lift others too.")
        else:
            st.success("All dimensions are at target! We can still refine if you want.")

        st.markdown("---")
        st.markdown("**Ready?** We will start with the dimension that needs the most work and go from there.")

        if st.button("Let's go →", type="primary"):
            question = engine.generate_first_question(st.session_state.essay)
            st.session_state.current_question = question
            st.session_state.dialogue_mode = "ask"
            st.session_state.phase = 3
            st.rerun()

# ═══════════════════════════════════════════════════════════════
# PHASE 3: DIALOGUE & REVISION
# ═══════════════════════════════════════════════════════════════
elif st.session_state.phase == 3:
    memory = engine.memory
    dim_name = VALUE_RUBRIC.get(memory.focus_dimension, {}).get("name", "Writing")

    st.subheader(f"✏️ Phase 3: Working on {dim_name}")

    # Live score bar
    scores = memory.get_current_scores()
    completed = sum(1 for d in DIMENSION_ORDER if scores.get(d, 0) >= TARGET_SCORE)
    score_parts = []
    for dim in DIMENSION_ORDER:
        s = scores.get(dim, 0)
        short = VALUE_RUBRIC[dim]["short"]
        if dim in memory.completed_dimensions or s >= TARGET_SCORE:
            score_parts.append(f"✅ {short}: {s}/4")
        elif dim == memory.focus_dimension:
            score_parts.append(f"➡️ **{short}: {s}/4**")
        else:
            score_parts.append(f"{short}: {s}/4")
    st.caption(" | ".join(score_parts) + f"  ({completed}/5 complete)")
    st.caption(f"Turn: {memory.get_ask_turn_count()} | Revisions: {memory.revision_count} | Level: L{memory.current_level}")

    # --- DIALOGUE HISTORY ---
    for turn in memory.dialogue_history:
        if turn.role == "tutor" and turn.mode == "ask":
            st.markdown(f"🏛️ {turn.content}")
        elif turn.role == "student" and turn.mode == "ask":
            intent_icon = "💡" if turn.intent in ("insight", "revision_plan") else "✍️"
            st.markdown(f"{intent_icon} {turn.content}")
        elif turn.role == "student" and turn.mode == "revise":
            # Show revision with score change
            if turn.scores_before and turn.scores_after:
                changes = []
                for d in DIMENSION_ORDER:
                    ob = turn.scores_before.get(d, 0)
                    nb = turn.scores_after.get(d, 0)
                    if nb > ob:
                        changes.append(f"📈 {VALUE_RUBRIC[d]['short']}: {ob}→{nb}")
                    elif nb < ob:
                        changes.append(f"📉 {VALUE_RUBRIC[d]['short']}: {ob}→{nb}")
                change_text = " | ".join(changes) if changes else "No score changes"
                st.info(f"📊 Re-scored: {change_text}")
        elif turn.role == "tutor" and turn.mode == "revise":
            # Revision feedback
            feedback_text = turn.content
            if feedback_text.startswith("[REVISION] "):
                feedback_text = feedback_text[len("[REVISION] "):]
            st.success(f"✅ {feedback_text}")
        elif turn.role == "tutor" and turn.mode == "model":
            # Model display in history
            st.markdown("---")
            st.markdown(f"🎨 *Model example was shown for {dim_name}*")
            st.markdown("---")

    # --- CURRENT MODE ---
    mode = st.session_state.dialogue_mode

    if mode == "ask":
        # Show current question
        if st.session_state.current_question:
            st.markdown(f"🏛️ {st.session_state.current_question}")

        response = st.text_area("Your response:", key="student_response",
                                 placeholder="Think about it and share what you notice...",
                                 height=100)
        if st.button("Send →", type="primary", disabled=len(response.strip()) < 3):
            result = engine.process_response(response.strip(), st.session_state.essay)

            if result["mode"] == "revise":
                st.session_state.dialogue_mode = "revise"
                st.session_state.current_question = result["revision_prompt"]
            elif result["mode"] == "end":
                st.session_state.phase = 4
            else:
                st.session_state.current_question = result.get("question", "")
                st.session_state.dialogue_mode = "ask"
            st.rerun()

    elif mode == "revise":
        st.markdown(f"✏️ {st.session_state.current_question}")

        # Show passage for reference
        with st.expander("📄 Reference: Reading Passage"):
            st.markdown(READING_PASSAGE)

        revised = st.text_area("Edit your essay:", value=st.session_state.essay,
                                height=300, key="revision_input")

        if st.button("Submit Revision →", type="primary"):
            old_essay = st.session_state.essay
            new_essay = revised.strip()
            st.session_state.essay = new_essay

            with st.spinner("Re-scoring your essay..."):
                result = engine.process_revision(
                    new_essay, old_essay,
                    scoring_anchors=SCORING_ANCHORS,
                    edge_case_framework=EDGE_CASE_FRAMEWORK,
                    creative_policy=CREATIVE_CONNECTION_POLICY,
                    passage_text=READING_PASSAGE
                )

            if result["all_complete"]:
                st.session_state.phase = 4
            elif result["next_mode"] == "model":
                st.session_state.dialogue_mode = "model"
                st.session_state.model_data = result["model_data"]
            elif result["next_mode"] == "reflect":
                st.session_state.phase = 4
            else:
                st.session_state.dialogue_mode = "ask"
                st.session_state.current_question = result.get("next_question", "")
                if result.get("dimension_changed"):
                    new_dim = result.get("new_dimension", "")
                    new_name = VALUE_RUBRIC.get(new_dim, {}).get("name", "the next area")
                    st.toast(f"✅ Moving to {new_name}")
            st.rerun()

    elif mode == "model":
        model = st.session_state.model_data
        if model:
            st.markdown("---")
            st.markdown("### 🎨 Let me show you what I mean")
            st.markdown("")

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**What you wrote:**")
                st.markdown(f"> {model.get('original_sentence', '')}")
            with col2:
                st.markdown("**What it could sound like:**")
                st.markdown(f"> {model.get('revised_sentence', '')}")

            st.markdown("")
            st.markdown(f"💡 {model.get('explanation', '')}")

            apply_to = model.get("apply_to", [])
            if apply_to:
                st.markdown("")
                st.markdown("**Now your turn.** Try applying that same move to:")
                for spot in apply_to:
                    st.markdown(f"- {spot}")

            st.markdown("---")

            # Show passage for reference
            with st.expander("📄 Reference: Reading Passage"):
                st.markdown(READING_PASSAGE)

            revised = st.text_area("Edit your essay with this pattern in mind:",
                                    value=st.session_state.essay, height=300,
                                    key="model_revision_input")

            if st.button("Submit Revision →", type="primary"):
                old_essay = st.session_state.essay
                new_essay = revised.strip()
                st.session_state.essay = new_essay

                # Record model turn
                memory.add_turn(DialogueTurn(
                    role="tutor",
                    content=f"[MODEL] Showed example for {dim_name}",
                    mode="model",
                    level=memory.current_level
                ))

                with st.spinner("Re-scoring..."):
                    result = engine.process_revision(
                        new_essay, old_essay,
                        scoring_anchors=SCORING_ANCHORS,
                        edge_case_framework=EDGE_CASE_FRAMEWORK,
                        creative_policy=CREATIVE_CONNECTION_POLICY,
                        passage_text=READING_PASSAGE
                    )

                if result["all_complete"]:
                    st.session_state.phase = 4
                elif result["next_mode"] == "reflect":
                    st.session_state.phase = 4
                else:
                    st.session_state.dialogue_mode = "ask"
                    st.session_state.current_question = result.get("next_question", "")
                    if result.get("dimension_changed"):
                        new_dim = result.get("new_dimension", "")
                        new_name = VALUE_RUBRIC.get(new_dim, {}).get("name", "the next area")
                        st.toast(f"✅ Moving to {new_name}")
                st.rerun()

# ═══════════════════════════════════════════════════════════════
# PHASE 4: INTERACTIVE REFLECTION
# ═══════════════════════════════════════════════════════════════
elif st.session_state.phase == 4:
    st.subheader("💭 Phase 4: Reflection")
    memory = engine.memory

    # Score journey
    if memory.score_snapshots and len(memory.score_snapshots) > 1:
        initial = memory.score_snapshots[0]["scores"]
        final = memory.score_snapshots[-1]["scores"]
        initial_avg = round(sum(initial.values()) / max(len(initial), 1), 1)
        final_avg = round(sum(final.values()) / max(len(final), 1), 1)

        if final_avg > initial_avg:
            st.markdown(f"You started at **{initial_avg}/4** and ended at **{final_avg}/4** — that is real, measurable improvement from one session.")
        elif final_avg == initial_avg:
            st.markdown(f"Your overall score held steady at **{final_avg}/4**, but the work you did matters — revision is where writing skills develop, even when numbers do not move immediately.")
        st.markdown(f"**Revisions made:** {memory.revision_count} | **Insights:** {len(memory.insights_found)}")

        # Show dimension changes
        changes = []
        for dim in DIMENSION_ORDER:
            oi = initial.get(dim, 0)
            fi = final.get(dim, 0)
            name = VALUE_RUBRIC[dim]["name"]
            if fi > oi:
                changes.append(f"📈 {name}: {oi} → {fi}")
            elif fi < oi:
                changes.append(f"📉 {name}: {oi} → {fi}")
            else:
                changes.append(f"➡️ {name}: {oi} (held)")
        for c in changes:
            st.caption(c)
    else:
        st.markdown("Session complete.")

    st.divider()

    # --- INTERACTIVE REFLECTION CONVERSATION ---
    st.markdown("**Let's talk about how that went.**")

    # Show reflection conversation history
    for role, text in st.session_state.reflection_history:
        if role == "tutor":
            st.markdown(f"🏛️ {text}")
        else:
            st.markdown(f"✍️ {text}")

    # Reflection prompts cycle
    reflection_turn = len([r for r in st.session_state.reflection_history if r[0] == "student"])

    if reflection_turn == 0:
        st.markdown("🏛️ What was the hardest part of this session for you?")
    elif reflection_turn == 1:
        st.markdown("🏛️ What is one thing you noticed about your writing that you did not see before we started?")
    elif reflection_turn == 2:
        st.markdown("🏛️ If you were starting a brand new essay right now, what would you do differently based on what we worked on?")

    if reflection_turn < 3:
        ref_input = st.text_area("Your thoughts:", key=f"reflection_{reflection_turn}",
                                  placeholder="Share what you are thinking...", height=100)
        if st.button("Share →", type="primary", disabled=len(ref_input.strip()) < 3):
            # Get AI response to their reflection
            session_data = {
                "initial_average": memory.score_snapshots[0]["scores"] if memory.score_snapshots else {},
                "final_average": memory.score_snapshots[-1]["scores"] if memory.score_snapshots else {},
            }
            # compute averages for the response generator
            if memory.score_snapshots:
                init_scores = memory.score_snapshots[0]["scores"]
                final_scores = memory.score_snapshots[-1]["scores"]
                session_data["initial_average"] = round(sum(init_scores.values()) / max(len(init_scores), 1), 1)
                session_data["final_average"] = round(sum(final_scores.values()) / max(len(final_scores), 1), 1)

            tutor_response = engine.generate_reflection_response(ref_input.strip(), session_data)

            st.session_state.reflection_history.append(("student", ref_input.strip()))
            st.session_state.reflection_history.append(("tutor", tutor_response))
            st.rerun()
    else:
        # After 3 reflection exchanges, wrap up
        st.markdown("---")
        st.markdown("🏛️ That is a wrap. You showed up, you did the work, and your writing is stronger for it. Take what you noticed today into your next piece.")
        st.balloons()

    # Export
    st.divider()
    if st.button("📥 Export Session Data"):
        session_data = engine.export_session()
        # Add reflection to export
        session_data["reflection_dialogue"] = st.session_state.reflection_history
        json_str = json.dumps(session_data, indent=2, default=str)
        st.download_button(
            "Download JSON",
            data=json_str,
            file_name=f"socratic_session_{session_data['session_id']}.json",
            mime="application/json"
        )

# --- FOOTER ---
st.markdown("---")
st.caption("Socratic Writing Tutor v0.6 | AAC&U VALUE Rubric (OER) | Built for Ed.D. research")
