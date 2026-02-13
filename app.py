"""
Socratic Writing Tutor - Streamlit App v1.2

A Socratic tutoring system that helps students improve their argumentative writing
through targeted questions, not direct answers.
"""

import streamlit as st
from core_engine import SocraticEngine
from passage_config import (
    PASSAGE_TITLE, PASSAGE_TEXT, WRITING_PROMPT, 
    VALUE_RUBRIC, DIMENSION_ORDER, TARGET_SCORE
)


def init_session():
    """Initialize session state."""
    if 'engine' not in st.session_state:
        st.session_state.engine = SocraticEngine()
    if 'phase' not in st.session_state:
        st.session_state.phase = 'read'
    if 'show_passage' not in st.session_state:
        st.session_state.show_passage = True
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'validation_result' not in st.session_state:
        st.session_state.validation_result = None
    if 'draft_text' not in st.session_state:
        st.session_state.draft_text = ""


def render_scores(scores: dict):
    """Render score display."""
    cols = st.columns(5)
    for i, dim in enumerate(DIMENSION_ORDER):
        with cols[i]:
            score = scores[dim]['score']
            name = VALUE_RUBRIC[dim]['name']
            
            if score >= TARGET_SCORE:
                color = "🟢"
            elif score == 2:
                color = "🟡"
            else:
                color = "🔴"
            
            st.markdown(f"**{name}**")
            st.markdown(f"{color} {score}/4")


def main():
    st.set_page_config(page_title="Socratic Writing Tutor", page_icon="📝")
    
    st.title("📝 Socratic Writing Tutor")
    
    # Custom CSS for welcome page
    st.markdown("""
    <style>
    .big-step {
        font-size: 1.3rem;
        font-weight: 600;
        margin: 8px 0;
        line-height: 1.6;
    }
    .coach-title {
        font-size: 1.4rem;
        font-weight: 700;
        margin: 16px 0 8px 0;
    }
    .coach-desc {
        font-size: 1.05rem;
        line-height: 1.6;
        margin-bottom: 12px;
    }
    .reassurance {
        font-size: 1.3rem;
        font-weight: 700;
        color: #065f46;
        background: #d1fae5;
        padding: 12px 20px;
        border-radius: 10px;
        margin: 12px 0;
        text-align: center;
    }
    .goal-box {
        font-size: 1.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px 24px;
        border-radius: 12px;
        text-align: center;
        margin: 20px 0;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: 700;
        margin: 24px 0 12px 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    init_session()
    engine = st.session_state.engine
    
    # Welcome message
    if st.session_state.phase == 'read':
        st.markdown("## Welcome!")
        st.markdown('<div class="section-header">Here\'s how this works:</div>', unsafe_allow_html=True)
        
        st.markdown("""
<div class="big-step">1. 📖 <strong>Read</strong> a short passage about a debatable topic</div>
<div class="big-step">2. ✏️ <strong>Write</strong> a response taking a clear position</div>
<div class="big-step">3. 🔍 <strong>Check & Improve</strong> your draft with help from two coaches</div>
<div class="big-step">4. 📝 <strong>Revise</strong> your response based on feedback</div>
<div class="big-step">5. 🪞 <strong>Reflect</strong> on what you learned and how you'll use it next time</div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.markdown('<div class="section-header">🤝 You\'ll have two coaches working with you:</div>', unsafe_allow_html=True)
        
        st.markdown("""
<div class="coach-title">🔍 The Draft Coach</div>
<div class="coach-desc">
Helps you <em>before</em> you're scored. It's an informal check that scans your writing for the basics — do you have a clear position? Did you use evidence from the passage? Is your reasoning showing? Think of it as a friendly second pair of eyes that points out what's working and what might need attention.
</div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="reassurance">✨ You can use the Draft Coach as many times as you want — no pressure, no scoring.</div>', unsafe_allow_html=True)
        
        st.markdown("""
<div class="coach-title">📝 The Socratic Coach</div>
<div class="coach-desc">
Steps in once you submit. It formally scores your writing on 5 dimensions and then asks you questions to help you strengthen your weakest areas. It won't tell you what to write — it'll help you figure it out yourself. Think of it like a teacher who believes you already have good ideas and just need the right questions to bring them out.
</div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="reassurance">💪 Don\'t worry — you can still revise and improve after submitting, too. This is all part of the learning process.</div>', unsafe_allow_html=True)
        
        st.markdown("""
<div style="font-size: 1.25rem; font-weight: 700; text-align: center; padding: 16px 20px; margin: 20px 0; background: #f0f4ff; border-radius: 10px; line-height: 1.6;">
Both coaches are here to help you grow as a writer.<br/>
🔍 The Draft Coach helps you prepare. &nbsp; 📝 The Socratic Coach helps you go deeper.
</div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.markdown('<div class="section-header">🪞 What\'s the Reflection step about?</div>', unsafe_allow_html=True)
        
        st.markdown("""
<div class="coach-desc">
At the end, you'll answer a few short questions about your experience. This isn't a test — there are no wrong answers. Reflection is how your brain moves learning from "something I did once" to "something I know how to do." You'll think about what was hard, what clicked, and where else you might use these skills. It only takes a few minutes, and it's one of the most powerful parts of the whole process.
</div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.markdown('<div class="goal-box">🎯 The Goal: Get all 5 dimensions to a score of 3/4 (meeting the standard)</div>', unsafe_allow_html=True)
        
        st.markdown("")
        
        if st.button("Let's begin!", type="primary"):
            st.session_state.phase = 'passage'
            st.rerun()
    
    # Show passage
    elif st.session_state.phase == 'passage':
        st.markdown("## Step 1: Read the Passage")
        st.info("Take your time reading. You'll need to reference specific details in your response.")
        
        st.markdown(f"### {PASSAGE_TITLE}")
        st.markdown(PASSAGE_TEXT)
        
        if st.button("I've read it — let me write!", type="primary"):
            st.session_state.phase = 'write'
            st.rerun()
    
    # Write phase
    elif st.session_state.phase == 'write':
        st.markdown("## Step 2: Write Your Response")
        
        with st.expander("📖 View passage again"):
            st.markdown(PASSAGE_TEXT)
        
        st.markdown(WRITING_PROMPT)

        st.markdown("")
        st.markdown("""💡 *Tip: Don't overthink it — write your honest first draft. We'll work on improving it together.*""")
        
        st.markdown("""---
**You have two coaches available:**

🔍 **Check My Draft** — An informal quick-look that scans for the basics (position, evidence, reasoning, structure, tone) and shows you what's missing *before* you get scored. Use this as many times as you want to strengthen your draft.

📝 **Submit for Feedback** — Your formal submission. This scores your writing on 5 dimensions and starts a Socratic coaching session where I'll ask you questions to help you improve. You can still revise after submitting.
""")

        # Show previous pre-check notes if they exist
        if st.session_state.validation_result:
            prev_result = st.session_state.validation_result
            needs_work = [c for c in prev_result.get('checks', []) if c.get('status') in ('weak', 'missing')]
            if needs_work:
                with st.expander("📋 Notes from your last draft check", expanded=True):
                    for check in needs_work:
                        status = check.get("status", "missing")
                        emoji = "⚠️" if status == "weak" else "❌"
                        obj = check.get("objective", "")
                        tip = check.get("tip", "")
                        st.markdown(f"{emoji} **{obj}**: {tip}")
        
        essay = st.text_area(
            "Your response:",
            value=st.session_state.draft_text,
            height=200,
            placeholder="Write your response here..."
        )
        st.session_state.draft_text = essay

        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔍 Check my draft first", type="secondary") and essay.strip():
                with st.spinner("Checking your draft..."):
                    result = engine.validator.validate(essay.strip())
                    st.session_state.validation_result = result
                    st.session_state.phase = 'validate'
                    st.rerun()
        
        with col2:
            if st.button("Submit for feedback", type="primary") and essay.strip():
                st.session_state.draft_text = essay.strip()
                result = engine.process_initial_essay(essay)
                st.session_state.phase = result['phase']
                st.session_state.messages.append({
                    'type': 'scores',
                    'scores': result['scores']
                })
                st.session_state.messages.append({
                    'type': 'essay',
                    'content': essay
                })
                st.session_state.messages.append({
                    'type': 'coaching',
                    'content': result['message']
                })
                st.rerun()
    
    # Pre-submission validation phase
    elif st.session_state.phase == 'validate':
        st.markdown("## 🔍 Draft Pre-Check")
        st.markdown("Here's how your draft looks before formal scoring:")
        
        result = st.session_state.validation_result
        if result:
            word_count = result.get('word_count', 0)
            overall_ready = result.get('overall_ready', False)
            checks = result.get('checks', [])
            summary = result.get('summary', '')
            
            # Status banner
            if overall_ready:
                st.success(f"✅ **Ready to submit** — {word_count} words")
            else:
                st.warning(f"⚠️ **Consider revising before submitting** — {word_count} words")
            
            if summary:
                st.markdown(f"*{summary}*")
            
            st.markdown("")
            
            # Show each objective as a status row
            status_config = {
                "present": ("✅", "Good", "#d1fae5"),
                "weak": ("⚠️", "Needs work", "#fef3c7"),
                "missing": ("❌", "Missing", "#fee2e2")
            }
            
            for check in checks:
                status = check.get("status", "missing")
                emoji, label, bg = status_config.get(status, ("❓", "Unknown", "#f3f4f6"))
                obj = check.get("objective", "")
                tip = check.get("tip", "")
                
                st.markdown(f"{emoji} **{obj}** — {label}")
                if tip:
                    st.markdown(f"   *💡 {tip}*")
            
            st.markdown("---")
            
            # Action buttons
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("✏️ Go back and revise", type="primary"):
                    st.session_state.phase = 'write'
                    st.session_state.validation_result = None
                    st.rerun()
            
            with col2:
                submit_label = "✅ Submit for scoring" if overall_ready else "⚠️ Submit anyway"
                if st.button(submit_label, type="secondary"):
                    essay = st.session_state.draft_text
                    result = engine.process_initial_essay(essay)
                    st.session_state.phase = result['phase']
                    st.session_state.messages.append({
                        'type': 'scores',
                        'scores': result['scores']
                    })
                    st.session_state.messages.append({
                        'type': 'essay',
                        'content': essay
                    })
                    st.session_state.messages.append({
                        'type': 'coaching',
                        'content': result['message']
                    })
                    st.rerun()
            
            if not overall_ready:
                missing_count = sum(1 for c in checks if c.get("status") == "missing")
                if missing_count >= 3:
                    st.info("💡 **Tip:** Your draft is missing several key elements. Going back to add them will give you a stronger starting point for coaching.")
        else:
            st.error("No validation results. Going back to writing.")
            st.session_state.phase = 'write'
            st.rerun()
    
    # Coaching phase
    elif st.session_state.phase == 'coach':
        st.markdown("## Step 3: Coaching Session")
        st.info("Read my feedback below, then revise your response. We'll keep working until all dimensions hit the target.")
        
        # Show current scores
        if st.session_state.messages:
            for msg in st.session_state.messages:
                if msg['type'] == 'scores':
                    st.markdown("### Your Scores")
                    render_scores(msg['scores'])
        
        # Show conversation history
        st.markdown("---")
        for msg in st.session_state.messages:
            if msg['type'] == 'essay':
                st.markdown(f"> {msg['content']}")
            elif msg['type'] == 'coaching':
                st.markdown(msg['content'])
        
        st.markdown("---")
        st.markdown("**Revise your response based on the coaching above:**")
        
        with st.expander("📖 View passage"):
            st.markdown(PASSAGE_TEXT)
        
        revision = st.text_area(
            "Your revised response:",
            value=st.session_state.draft_text,
            height=200,
            placeholder="Write your revision here..."
        )
        
        if st.button("Submit revision", type="primary") and revision.strip():
            st.session_state.draft_text = revision.strip()
            result = engine.process_revision(revision)
            st.session_state.phase = result['phase']
            st.session_state.messages.append({
                'type': 'scores',
                'scores': result.get('scores', engine.memory.get_latest_scores())
            })
            st.session_state.messages.append({
                'type': 'essay',
                'content': revision
            })
            st.session_state.messages.append({
                'type': 'coaching',
                'content': result['message']
            })
            st.rerun()
    
    # Reflection phase
    elif st.session_state.phase == 'reflect':
        st.markdown("## Step 4: Reflection")
        st.info("Let's take a moment to think about what you learned during this session.")
        
        # Show score progress
        if engine.memory.get_revision_count() > 0:
            st.markdown("### Score Progress")
            first_scores = engine.memory.scores_history[0]
            final_scores = engine.memory.get_latest_scores()
            
            for dim in DIMENSION_ORDER:
                first = first_scores[dim]['score']
                final = final_scores[dim]['score']
                name = VALUE_RUBRIC[dim]['name']
                
                if final > first:
                    st.markdown(f"**{name}:** {first} → {final} ⬆️")
                else:
                    st.markdown(f"**{name}:** {first} → {final} ➡️")
        
        # Show conversation
        st.markdown("---")
        for msg in st.session_state.messages:
            if msg['type'] == 'essay':
                st.markdown(f"> {msg['content']}")
            elif msg['type'] == 'coaching':
                st.markdown(msg['content'])
        
        # Reflection questions
        st.markdown("---")
        
        # Get current reflection question
        reflection_turn = engine.memory.reflection_turn
        if reflection_turn < len(engine.memory.reflection_responses):
            # Show previous responses
            from passage_config import REFLECTION_PROMPTS
            for i, resp in enumerate(engine.memory.reflection_responses):
                st.markdown(f"**{REFLECTION_PROMPTS[i]['question']}**")
                st.markdown(f"> {resp}")
        
        # Show current question or prompt for response
        from passage_config import REFLECTION_PROMPTS
        if reflection_turn < len(REFLECTION_PROMPTS):
            current_q = REFLECTION_PROMPTS[reflection_turn]['question']
            st.markdown(f"### {current_q}")
            
            reflection = st.text_area(
                "Your response:",
                height=100,
                placeholder="Take a moment to reflect...",
                key=f"reflection_{reflection_turn}"
            )
            
            if st.button("Submit", type="primary") and reflection.strip():
                result = engine.process_reflection(reflection)
                st.session_state.phase = result['phase']
                st.session_state.messages.append({
                    'type': 'coaching',
                    'content': result['message']
                })
                st.rerun()
    
    # Complete phase
    elif st.session_state.phase == 'complete':
        st.markdown("## 🎉 Session Complete!")
        
        # Show final message
        for msg in st.session_state.messages[-3:]:
            if msg['type'] == 'coaching':
                st.markdown(msg['content'])
        
        # Show stats
        stats = engine.get_session_stats()
        st.markdown("---")
        st.markdown("### Session Stats:")
        st.markdown(f"- **Revisions:** {stats['revisions']}")
        st.markdown(f"- **Coaching turns:** {stats['coaching_turns']}")
        st.markdown(f"- **Essay versions:** {stats['essay_versions']}")
        
        if st.button("Start a new session", type="primary"):
            # Reset everything
            st.session_state.engine = SocraticEngine()
            st.session_state.phase = 'read'
            st.session_state.messages = []
            st.session_state.validation_result = None
            st.session_state.draft_text = ""
            st.rerun()


if __name__ == "__main__":
    main()
