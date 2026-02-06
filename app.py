"""
Socratic Writing Tutor - Streamlit App v1.2
"""
import streamlit as st
from core_engine import SocraticEngine
from passage_config import (
    PASSAGE_TITLE, PASSAGE_TEXT, WRITING_PROMPT,
    VALUE_RUBRIC, DIMENSION_ORDER, TARGET_SCORE,
    REFLECTION_PROMPTS, RESCORE_FRAMING
)

st.set_page_config(page_title="Socratic Writing Tutor", page_icon="📝", layout="centered")

# Session state
if "engine" not in st.session_state:
    st.session_state.engine = SocraticEngine()
if "phase" not in st.session_state:
    st.session_state.phase = "intro"
if "messages" not in st.session_state:
    st.session_state.messages = []
if "awaiting_reflection" not in st.session_state:
    st.session_state.awaiting_reflection = False


def add_message(role, content):
    st.session_state.messages.append({"role": role, "content": content})


def render_score_card(scores, title="Your Scores"):
    st.markdown(f"**{title}**")
    cols = st.columns(5)
    for i, dim_key in enumerate(DIMENSION_ORDER):
        dim = VALUE_RUBRIC[dim_key]
        score_data = scores.get(dim_key, {})
        score_val = score_data.get("score", "?")
        with cols[i]:
            if isinstance(score_val, int):
                if score_val >= TARGET_SCORE:
                    color = "🟢"
                elif score_val == TARGET_SCORE - 1:
                    color = "🟡"
                else:
                    color = "🔴"
            else:
                color = "⚪"
            st.metric(label=dim["name"], value=f"{color} {score_val}/4")


def render_score_comparison(initial_scores, final_scores):
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
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()


# Sidebar
with st.sidebar:
    st.markdown("## 📊 Session Status")
    engine = st.session_state.engine
    memory = engine.memory
    phase = st.session_state.phase
    st.write(f"**Phase:** {phase.title()}")
    st.write(f"**Revisions:** {memory.get_revision_count()}")
    st.write(f"**Coaching turns:** {memory.coaching_turns}")
    if memory.scores_history:
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


# Main content
st.title("📝 Socratic Writing Tutor")

# ---- PHASE: INTRO ----
if st.session_state.phase == "intro":
    st.markdown("### Welcome!")
    st.markdown("""
**Here's how this works:**

1. **Read** a short passage about a debatable topic
2. **Write** a response taking a clear position
3. **Get feedback** - I'll score your writing on 5 dimensions and ask you questions to help you improve
4. **Revise** your response based on our conversation
5. **Reflect** on what you learned

This is a Socratic tutor - I won't tell you what to write. Instead, I'll ask questions that help you discover how to make your writing stronger.

**The goal:** Get all 5 dimensions to a score of 3/4 (meeting the standard).

Ready?
    """)
    st.markdown("---")
    if st.button("Let's get started! →", use_container_width=True):
        st.session_state.phase = "read"
        st.rerun()

# ---- PHASE: READ ----
elif st.session_state.phase == "read":
    st.markdown("### Step 1: Read the Passage")
    st.info("Take your time reading. You'll need to reference specific details in your response.")
    st.markdown(f"**{PASSAGE_TITLE}**")
    st.markdown(PASSAGE_TEXT)
    st.markdown("---")
    if st.button("I've read it - show me the writing prompt ✏️", use_container_width=True):
        st.session_state.phase = "write"
        st.rerun()

# ---- PHASE: WRITE ----
elif st.session_state.phase == "write":
    st.markdown("### Step 2: Write Your Response")
    with st.expander("📖 View passage again"):
        st.markdown(PASSAGE_TEXT)
    st.markdown(WRITING_PROMPT)
    st.info("**Tip:** Don't overthink it - write your honest first draft. We'll work on improving it together.")
    st.markdown("---")
    essay = st.text_area("Your response:", height=250, placeholder="Write your response here...", key="initial_essay")
    if st.button("Submit my response", use_container_width=True, disabled=len(essay.strip()) < 10):
        with st.spinner("Reading your response..."):
            result = st.session_state.engine.process_essay(essay.strip())
            add_message("user", essay.strip())
            add_message("assistant", result["message"])
            st.session_state.phase = result["phase"]
        st.rerun()

# ---- PHASE: COACH ----
elif st.session_state.phase == "coach":
    st.markdown("### Step 3: Coaching Session")
    st.info("Read my feedback below, then revise your response. We'll keep working until all dimensions hit the target.")
    engine = st.session_state.engine
    memory = engine.memory
    
    if memory.scores_history:
        render_score_card(memory.get_latest_scores())
        st.markdown("---")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    st.markdown("---")
    st.markdown("**Revise your response based on the coaching above:**")
    with st.expander("📖 View passage"):
        st.markdown(PASSAGE_TEXT)

    current_essay = memory.get_latest_essay()
    revised = st.text_area("Your revised response:", value=current_essay, height=250, key=f"revision_{memory.get_revision_count()}")

    if st.button("Submit revision", use_container_width=True, disabled=len(revised.strip()) < 10):
        with st.spinner(RESCORE_FRAMING):
            result = st.session_state.engine.process_essay(revised.strip())
            add_message("user", f"[Revision #{memory.get_revision_count()}]\n\n{revised.strip()}")
            add_message("assistant", result["message"])
            st.session_state.phase = result["phase"]
        st.rerun()

# ---- PHASE: REFLECT ----
elif st.session_state.phase == "reflect":
    st.markdown("### Step 4: Reflection")
    st.info("Let's take a moment to think about what you learned during this session.")
    engine = st.session_state.engine
    memory = engine.memory

    if len(memory.scores_history) >= 2:
        render_score_comparison(memory.scores_history[0], memory.get_latest_scores())
        st.markdown("---")
    elif memory.scores_history:
        render_score_card(memory.get_latest_scores(), "Final Scores")
        st.markdown("---")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Get current reflection question
    current_q = engine.get_current_reflection_question()
    
    if current_q and not st.session_state.awaiting_reflection:
        add_message("assistant", current_q)
        st.session_state.awaiting_reflection = True
        st.rerun()

    if current_q:
        reflection_input = st.text_input("Your response:", key=f"reflection_{memory.reflection_turn}", placeholder="Type your thoughts here...")
        if st.button("Send", use_container_width=True, disabled=len(reflection_input.strip()) < 2):
            add_message("user", reflection_input.strip())
            with st.spinner("Thinking..."):
                result = engine.process_reflection(reflection_input.strip())
            add_message("assistant", result["message"])
            st.session_state.awaiting_reflection = False
            st.session_state.phase = result["phase"]
            st.rerun()
    else:
        st.session_state.phase = "done"
        st.rerun()

# ---- PHASE: DONE ----
elif st.session_state.phase == "done":
    st.markdown("### 🎉 Session Complete!")
    engine = st.session_state.engine
    memory = engine.memory

    if len(memory.scores_history) >= 2:
        render_score_comparison(memory.scores_history[0], memory.get_latest_scores())
    elif memory.scores_history:
        render_score_card(memory.get_latest_scores(), "Final Scores")

    st.markdown("---")
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    st.markdown("---")
    st.balloons()
    
    stats = engine.get_session_stats()
    st.markdown(f"""
**Session Stats:**
- Revisions: {stats['revisions']}
- Coaching turns: {stats['coaching_turns']}
- Essay versions: {stats['essay_versions']}
    """)

    if st.button("🔄 Start a New Session", use_container_width=True):
        reset_session()