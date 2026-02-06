"""
Core Engine for Socratic Writing Tutor v0.7
Handles: Scoring, Socratic coaching, dimension cycling, MODEL mode, reflection.
"""

import json
import re
import anthropic
import streamlit as st
from passage_config import (
    VALUE_RUBRIC, DIMENSION_ORDER, TARGET_SCORE,
    SCORING_SYSTEM_PROMPT, COACHING_SYSTEM_PROMPT,
    MODEL_EXAMPLE_PROMPT, REFLECTION_PROMPTS,
    PASSAGE_TEXT, EDGE_CASE_RULES, get_rubric_text
)


# ============================================================
# MEMORY MANAGER — tracks session state
# ============================================================

class SocraticMemory:
    """Tracks all session state for one tutoring session."""

    def __init__(self):
        self.essay_versions = []          # list of essay strings
        self.scores = []                  # list of score dicts
        self.current_dimension = None     # which dimension we're coaching
        self.dimension_index = 0          # index into sorted dimension list
        self.coaching_turns = 0           # total coaching turns used
        self.revision_count = 0           # actual revisions submitted
        self.model_mode_used = {}         # {dimension: True} — once per dim
        self.conversation_log = []        # full chat history
        self.reflection_step = 0          # 0-2 for reflection phase
        self.session_complete = False
        self.max_coaching_turns = 15

    def add_essay(self, essay_text):
        self.essay_versions.append(essay_text)

    def add_scores(self, scores):
        self.scores.append(scores)

    def get_latest_essay(self):
        return self.essay_versions[-1] if self.essay_versions else ""

    def get_latest_scores(self):
        return self.scores[-1] if self.scores else {}

    def get_initial_scores(self):
        return self.scores[0] if self.scores else {}

    def increment_revision(self):
        self.revision_count += 1

    def get_weakest_dimensions(self):
        """Return dimensions sorted by score (weakest first), excluding those at target."""
        latest = self.get_latest_scores()
        if not latest:
            return DIMENSION_ORDER[:]

        below_target = []
        for dim in DIMENSION_ORDER:
            if dim in latest:
                score = latest[dim].get("score", 0)
                if score < TARGET_SCORE:
                    below_target.append((dim, score))

        below_target.sort(key=lambda x: x[1])
        return [d[0] for d in below_target]

    def all_dimensions_at_target(self):
        """Check if every dimension has hit the target score."""
        latest = self.get_latest_scores()
        if not latest:
            return False
        return all(
            latest.get(dim, {}).get("score", 0) >= TARGET_SCORE
            for dim in DIMENSION_ORDER
        )

    def should_end_session(self):
        """Session ends when all dimensions at target OR max turns reached."""
        if self.all_dimensions_at_target():
            return True
        if self.coaching_turns >= self.max_coaching_turns:
            return True
        return False


# ============================================================
# API CALLS
# ============================================================

def get_client():
    """Get Anthropic client using Streamlit secrets."""
    api_key = st.secrets.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        st.error("Missing ANTHROPIC_API_KEY in Streamlit secrets.")
        st.stop()
    return anthropic.Anthropic(api_key=api_key)


def call_claude(system_prompt, user_message, max_tokens=1024):
    """Make a single Claude API call."""
    client = get_client()
    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}]
        )
        return response.content[0].text
    except Exception as e:
        return f"API Error: {str(e)}"


# ============================================================
# SCORING
# ============================================================

def score_essay(essay_text):
    """Score an essay across all 5 VALUE rubric dimensions. Returns dict."""
    rubric_text = get_rubric_text()
    system = SCORING_SYSTEM_PROMPT.format(rubric_text=rubric_text)

    user_msg = f"""PASSAGE:\n{PASSAGE_TEXT}\n\nSTUDENT RESPONSE:\n{essay_text}\n\n{EDGE_CASE_RULES}\n\nScore this response. Return ONLY valid JSON."""

    raw = call_claude(system, user_msg, max_tokens=800)

    # Parse JSON from response — handle markdown fences
    cleaned = raw.strip()
    cleaned = re.sub(r'^```(?:json)?\s*', '', cleaned)
    cleaned = re.sub(r'\s*```$', '', cleaned)

    try:
        scores = json.loads(cleaned)
        # Validate structure
        for dim in DIMENSION_ORDER:
            if dim not in scores:
                scores[dim] = {"score": 1, "rationale": "Unable to assess."}
            if not isinstance(scores[dim].get("score"), int):
                scores[dim]["score"] = int(scores[dim].get("score", 1))
            scores[dim]["score"] = max(1, min(4, scores[dim]["score"]))
        return scores
    except (json.JSONDecodeError, ValueError):
        # Fallback scores if parsing fails
        return {
            dim: {"score": 1, "rationale": "Scoring error — please try again."}
            for dim in DIMENSION_ORDER
        }


# ============================================================
# SOCRATIC COACHING
# ============================================================

def generate_coaching_question(memory):
    """Generate a Socratic coaching question for the current dimension."""
    dim_key = memory.current_dimension
    dim_info = VALUE_RUBRIC[dim_key]
    latest_scores = memory.get_latest_scores()
    dim_score = latest_scores.get(dim_key, {})

    system = COACHING_SYSTEM_PROMPT.format(
        dimension_name=dim_info["name"],
        current_score=dim_score.get("score", 1),
        target_score=TARGET_SCORE,
        rationale=dim_score.get("rationale", ""),
        essay=memory.get_latest_essay(),
        passage=PASSAGE_TEXT
    )

    user_msg = "Generate your coaching question now."
    return call_claude(system, user_msg, max_tokens=300)


def generate_model_example(memory):
    """Generate a before/after MODEL example when score doesn't improve."""
    dim_key = memory.current_dimension
    dim_info = VALUE_RUBRIC[dim_key]
    latest_scores = memory.get_latest_scores()
    dim_score = latest_scores.get(dim_key, {})

    system = MODEL_EXAMPLE_PROMPT.format(
        dimension_name=dim_info["name"],
        dimension_description=dim_info["description"],
        current_score=dim_score.get("score", 1)
    )

    user_msg = "Generate the before/after example now."
    return call_claude(system, user_msg, max_tokens=400)


# ============================================================
# REFLECTION
# ============================================================

def generate_reflection_response(memory, student_response):
    """Generate AI response during the reflection phase."""
    step = memory.reflection_step
    if step >= len(REFLECTION_PROMPTS):
        return None

    prompt_data = REFLECTION_PROMPTS[step]

    # Build context about the session
    initial = memory.get_initial_scores()
    final = memory.get_latest_scores()
    score_summary = []
    for dim in DIMENSION_ORDER:
        i_score = initial.get(dim, {}).get("score", "?")
        f_score = final.get(dim, {}).get("score", "?")
        name = VALUE_RUBRIC[dim]["name"]
        score_summary.append(f"{name}: {i_score} → {f_score}")

    session_context = (
        f"Session summary: {memory.revision_count} revision(s). "
        f"Score changes: {'; '.join(score_summary)}"
    )

    system = f"""{prompt_data['followup_system']}

SESSION CONTEXT: {session_context}"""

    user_msg = f"The student said: {student_response}"
    return call_claude(system, user_msg, max_tokens=300)


# ============================================================
# SESSION ORCHESTRATOR
# ============================================================

class TutorEngine:
    """Orchestrates the full tutoring session flow."""

    # Session phases
    PHASE_READ = "read"
    PHASE_WRITE = "write"
    PHASE_SCORE = "score"
    PHASE_COACH = "coach"
    PHASE_REVISE = "revise"
    PHASE_REFLECT = "reflect"
    PHASE_DONE = "done"

    def __init__(self, memory):
        self.memory = memory

    def process_initial_essay(self, essay_text):
        """Student submits their first essay. Score it and begin coaching."""
        self.memory.add_essay(essay_text)

        # Score the essay
        scores = score_essay(essay_text)
        self.memory.add_scores(scores)

        # Check if already at target everywhere (unlikely but handle it)
        if self.memory.all_dimensions_at_target():
            return {
                "phase": self.PHASE_REFLECT,
                "scores": scores,
                "message": "Impressive — your response is strong across the board. Let's reflect on your process."
            }

        # Set the first coaching dimension (weakest)
        weak = self.memory.get_weakest_dimensions()
        if weak:
            self.memory.current_dimension = weak[0]
            self.memory.dimension_index = 0

        # Generate first coaching question
        coaching_q = generate_coaching_question(self.memory)
        self.memory.coaching_turns += 1

        return {
            "phase": self.PHASE_COACH,
            "scores": scores,
            "coaching_question": coaching_q,
            "dimension": self.memory.current_dimension
        }

    def process_revision(self, revised_essay):
        """Student submits a revised essay. Re-score, check progress, continue or advance."""
        self.memory.add_essay(revised_essay)
        self.memory.increment_revision()

        # Re-score
        new_scores = score_essay(revised_essay)
        self.memory.add_scores(new_scores)

        # Check if all dimensions at target
        if self.memory.all_dimensions_at_target():
            return {
                "phase": self.PHASE_REFLECT,
                "scores": new_scores,
                "message": "Your response has really developed. Let's reflect on what you learned."
            }

        # Check if max turns reached
        if self.memory.should_end_session():
            return {
                "phase": self.PHASE_REFLECT,
                "scores": new_scores,
                "message": "We've done a lot of work together. Let's reflect on the session."
            }

        # Check current dimension progress
        dim_key = self.memory.current_dimension
        old_scores = self.memory.scores[-2] if len(self.memory.scores) >= 2 else {}
        old_score = old_scores.get(dim_key, {}).get("score", 0)
        new_score = new_scores.get(dim_key, {}).get("score", 0)

        # If dimension hit target, advance to next weakest
        if new_score >= TARGET_SCORE:
            weak = self.memory.get_weakest_dimensions()
            if weak:
                self.memory.current_dimension = weak[0]
            else:
                # All at target
                return {
                    "phase": self.PHASE_REFLECT,
                    "scores": new_scores,
                    "message": "All dimensions are at target. Let's reflect."
                }

        # If score didn't improve and MODEL mode not used yet for this dim
        elif new_score <= old_score and not self.memory.model_mode_used.get(dim_key, False):
            self.memory.model_mode_used[dim_key] = True
            model_example = generate_model_example(self.memory)
            self.memory.coaching_turns += 1
            return {
                "phase": self.PHASE_COACH,
                "scores": new_scores,
                "coaching_question": model_example,
                "dimension": dim_key,
                "is_model_mode": True
            }

        # Otherwise, continue coaching on current (or next weakest) dimension
        weak = self.memory.get_weakest_dimensions()
        if weak and self.memory.current_dimension not in weak:
            self.memory.current_dimension = weak[0]

        coaching_q = generate_coaching_question(self.memory)
        self.memory.coaching_turns += 1

        return {
            "phase": self.PHASE_COACH,
            "scores": new_scores,
            "coaching_question": coaching_q,
            "dimension": self.memory.current_dimension
        }

    def process_reflection_response(self, student_response):
        """Handle student response during reflection phase."""
        step = self.memory.reflection_step

        if step >= len(REFLECTION_PROMPTS):
            self.memory.session_complete = True
            return {
                "phase": self.PHASE_DONE,
                "message": "Session complete. Great work today! 🎈"
            }

        ai_response = generate_reflection_response(self.memory, student_response)
        self.memory.reflection_step += 1

        if self.memory.reflection_step >= len(REFLECTION_PROMPTS):
            self.memory.session_complete = True
            return {
                "phase": self.PHASE_DONE,
                "message": ai_response,
            }

        return {
            "phase": self.PHASE_REFLECT,
            "message": ai_response,
        }