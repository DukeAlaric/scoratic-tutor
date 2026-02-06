"""
Socratic Writing Tutor — Streamlit App v0.7
A reading-to-writing tutoring system with AI-powered Socratic coaching.
"""

import streamlit as st
from core_engine import TutorEngine, SocraticMemory
from passage_config import (
    PASSAGE_TITLE, PASSAGE_TEXT, WRITING_PROMPT,
    VALUE_RUBRIC, DIMENSION_ORDER, TARGET_SCORE,
    REFLECTION_PROMPTS, RESCORE_FRAMING
)

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Socratic Writing Tutor",
    page_icon="📝",
    layout="centered"
)

# ============================================================
# SESSION STATE INITIALIZATION
# ============================================================

if "memory" not in st.session_state:
    st.session_state.memory = SocraticMemory()

if "engine" not in st.session_state:
    st.session_state.engine = TutorEngine(st.session_state.memory)

if "phase" not in st.session_state:
    st.session_state.phase = "read"  # read → write → coach → revise → reflect → done

if "messages" not in st.session_state:
    st.session_state.messages = []

if "latest_result" not in st.session_state:
    st.session_state.latest_result = None

if "awaiting_reflection" not in st.session_state:
    st.session_state.awaiting_reflection = False

if "reflection_question_shown" not in st.session_state:
    st.session_state.reflection_question_shown = False


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def add_message(role, content):
    """Add a message to the chat history."""
    st.session_state.messages.append({"role": role, "content": content})


def render_score_card(scores, title="Your Scores"):
    """Render a score card as a formatted display."""
    st.markdown(f"**{title}**")
    cols = st.columns(5)
    for i, dim_key in enumerate(DIMENSION_ORDER):
        dim = VALUE_RUBRIC[dim_key]
        score_data = scores.get(dim_key, {})
        score_val = score_data.get("score", "?")
        with cols[i]:
            # Color coding
            if isinstance(score_val, int):
                if score_val >= TARGET_SCORE:
                    color = "🟢"
                elif score_val == TARGET_SCORE - 1:
                    color = "🟡"
                else:
                    color = "🔴"
            else:
                color = "⚪"
            st.metric(
                label=dim["name"],
                value=f"{color} {score_val}/4"
            )


def render_score_comparison(initial_scores, final_scores):
    """Show before/after score comparison."""
    st.markdown("**Score Progress**")
    for dim_key in DIMENSION_ORDER:
        dim = VALUE_RUBRIC[dim_key]
        i_score = initial_scores.get(dim_key, {}).get("score", "?")
        f_score = final_scores.get(dim_key, {}).get("score", "?")
        arrow = ""
        if isinstance(i_score, int) and isinstance(f_score, int):
            if f_score > i_score:
                arrow = "⬆️"
            elif f_score == i_score:
                arrow = "➡️"
            else:
                arrow = "⬇️"
        st.write(f"**{dim['name']}**: {i_score} → {f_score} {arrow}")


def reset_session():
    """Reset everything for a new session."""
    for key in ["memory", "engine", "phase", "messages", "latest_result",
                "awaiting_reflection", "reflection_question_shown"]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()


# ============================================================
# SIDEBAR — STATUS & INFO
# ============================================================

with st.sidebar:
    st.markdown("## 📊 Session Status")

    memory = st.session_state.memory
    phase = st.session_state.phase

    st.write(f"**Phase:** {phase.title()}")
    st.write(f"**Revisions:** {memory.revision_count}")
    st.write(f"**Coaching turns:** {memory.coaching_turns}")

    if memory.current_dimension:
        dim_name = VALUE_RUBRIC.get(memory.current_dimension, {}).get("name", "")
        st.write(f"**Current focus:** {dim_name}")

    # Show latest scores if available
    if memory.scores:
        st.markdown("---")
        latest = memory.get_latest_scores()
        for dim_key in DIMENSION_ORDER:
            dim = VALUE_RUBRIC[dim_key]
            s = latest.get(dim_key, {}).get("score", "?")
            target_hit = "✅" if isinstance(s, int) and s >= TARGET_SCORE else "❌"
            st.write(f"{target_hit} {dim['name']}: **{s}/4**")

    st.markdown("---")
    if st.button("🔄 Start Over", use_container_width=True):
        reset_session()


# ============================================================
# MAIN CONTENT
# ============================================================

st.title("📝 Socratic Writing Tutor")

# ---- PHASE: READ ----
if st.session_state.phase == "read":
    st.markdown("### Step 1: Read the Passage")
    st.markdown(f"**{PASSAGE_TITLE}**")
    st.markdown(PASSAGE_TEXT)

    st.markdown("---")
    if st.button("I've read it — show me the writing prompt ✍️", use_container_width=True):
        st.session_state.phase = "write"
        st.rerun()

# ---- PHASE: WRITE ----
elif st.session_state.phase == "write":
    st.markdown("### Step 2: Write Your Response")

    with st.expander("📖 View passage again"):
        st.markdown(PASSAGE_TEXT)

    st.markdown(WRITING_PROMPT)
    st.markdown("---")

    essay = st.text_area(
        "Your response:",
        height=250,
        placeholder="Write your response here...",
        key="initial_essay"
    )

    if st.button("Submit my response", use_container_width=True, disabled=len(essay.strip()) < 10):
        with st.spinner("Reading your response and thinking about it..."):
            result = st.session_state.engine.process_initial_essay(essay.strip())
            st.session_state.latest_result = result

            # Add to chat
            add_message("user", essay.strip())

            if result["phase"] == "reflect":
                add_message("assistant", result["message"])
                st.session_state.phase = "reflect"
            else:
                add_message("assistant", result["coaching_question"])
                st.session_state.phase = "coach"

        st.rerun()

# ---- PHASE: COACH (Socratic conversation + revision) ----
elif st.session_state.phase in ["coach", "revise"]:

    st.markdown("### Coaching Session")

    # Show scores
    if st.session_state.memory.scores:
        render_score_card(st.session_state.memory.get_latest_scores())
        st.markdown("---")

    # Render chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Show revision area
    st.markdown("---")
    st.markdown("**Revise your response based on the coaching above:**")

    with st.expander("📖 View passage"):
        st.markdown(PASSAGE_TEXT)

    current_essay = st.session_state.memory.get_latest_essay()

    revised = st.text_area(
        "Your revised response:",
        value=current_essay,
        height=250,
        key=f"revision_{st.session_state.memory.revision_count}"
    )

    if st.button("Submit revision", use_container_width=True,
                  disabled=len(revised.strip()) < 10):
        with st.spinner(RESCORE_FRAMING):
            result = st.session_state.engine.process_revision(revised.strip())
            st.session_state.latest_result = result

            add_message("user", f"[Revision #{st.session_state.memory.revision_count}]\n\n{revised.strip()}")

            if result["phase"] == "reflect":
                add_message("assistant", result["message"])
                st.session_state.phase = "reflect"
            else:
                coaching_msg = result.get("coaching_question", "")
                if result.get("is_model_mode"):
                    coaching_msg = "📋 **Let me show you an example:**\n\n" + coaching_msg
                add_message("assistant", coaching_msg)
                st.session_state.phase = "coach"

        st.rerun()

# ---- PHASE: REFLECT ----
elif st.session_state.phase == "reflect":

    st.markdown("### 🪞 Reflection")

    # Show score comparison
    if len(st.session_state.memory.scores) >= 2:
        render_score_comparison(
            st.session_state.memory.get_initial_scores(),
            st.session_state.memory.get_latest_scores()
        )
        st.markdown("---")
    elif st.session_state.memory.scores:
        render_score_card(st.session_state.memory.get_latest_scores(), "Final Scores")
        st.markdown("---")

    # Render chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Show reflection question if we haven't completed all steps
    memory = st.session_state.memory
    step = memory.reflection_step

    if step < len(REFLECTION_PROMPTS) and not st.session_state.memory.session_complete:
        # Show the current reflection question if not yet answered
        if not st.session_state.awaiting_reflection:
            q = REFLECTION_PROMPTS[step]["question"]
            add_message("assistant", q)
            st.session_state.awaiting_reflection = True
            st.rerun()

        # Input for reflection response
        reflection_input = st.text_input(
            "Your response:",
            key=f"reflection_{step}",
            placeholder="Type your thoughts here..."
        )

        if st.button("Send", use_container_width=True,
                      disabled=len(reflection_input.strip()) < 2):
            add_message("user", reflection_input.strip())

            with st.spinner("Thinking..."):
                result = st.session_state.engine.process_reflection_response(
                    reflection_input.strip()
                )

            add_message("assistant", result["message"])
            st.session_state.awaiting_reflection = False

            if result["phase"] == "done":
                st.session_state.phase = "done"

            st.rerun()

    elif st.session_state.memory.session_complete:
        st.session_state.phase = "done"
        st.rerun()

# ---- PHASE: DONE ----
elif st.session_state.phase == "done":

    st.markdown("### 🎉 Session Complete!")

    # Show final score comparison
    if len(st.session_state.memory.scores) >= 2:
        render_score_comparison(
            st.session_state.memory.get_initial_scores(),
            st.session_state.memory.get_latest_scores()
        )
    elif st.session_state.memory.scores:
        render_score_card(st.session_state.memory.get_latest_scores(), "Final Scores")

    st.markdown("---")

    # Render full chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    st.markdown("---")
    st.balloons()

    # Session stats
    memory = st.session_state.memory
    st.markdown(f"""
**Session Stats:**
- Revisions: {memory.revision_count}
- Coaching turns: {memory.coaching_turns}
- Essay versions: {len(memory.essay_versions)}
    """)

    if st.button("🔄 Start a New Session", use_container_width=True):
        reset_session()