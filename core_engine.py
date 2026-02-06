"""
Core Engine for Socratic Writing Tutor v0.7
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


class SocraticMemory:
    def __init__(self):
        self.essay_versions = []
        self.scores = []
        self.current_dimension = None
        self.dimension_index = 0
        self.coaching_turns = 0
        self.revision_count = 0
        self.model_mode_used = {}
        self.conversation_log = []
        self.reflection_step = 0
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
        latest = self.get_latest_scores()
        if not latest:
            return False
        return all(
            latest.get(dim, {}).get("score", 0) >= TARGET_SCORE
            for dim in DIMENSION_ORDER
        )

    def should_end_session(self):
        if self.all_dimensions_at_target():
            return True
        if self.coaching_turns >= self.max_coaching_turns:
            return True
        return False


def get_client():
    api_key = st.secrets.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        st.error("Missing ANTHROPIC_API_KEY in Streamlit secrets.")
        st.stop()
    return anthropic.Anthropic(api_key=api_key)


def call_claude(system_prompt, user_message, max_tokens=1024):
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


def score_essay(essay_text):
    rubric_text = get_rubric_text()
    system = SCORING_SYSTEM_PROMPT.format(rubric_text=rubric_text)
    user_msg = f"PASSAGE:\n{PASSAGE_TEXT}\n\nSTUDENT RESPONSE:\n{essay_text}\n\n{EDGE_CASE_RULES}\n\nScore this response. Return ONLY valid JSON."
    raw = call_claude(system, user_msg, max_tokens=800)
    cleaned = raw.strip()
    cleaned = re.sub(r'^```(?:json)?\s*', '', cleaned)
    cleaned = re.sub(r'\s*```$', '', cleaned)
    try:
        scores = json.loads(cleaned)
        for dim in DIMENSION_ORDER:
            if dim not in scores:
                scores[dim] = {"score": 1, "rationale": "Unable to assess."}
            if not isinstance(scores[dim].get("score"), int):
                scores[dim]["score"] = int(scores[dim].get("score", 1))
            scores[dim]["score"] = max(1, min(4, scores[dim]["score"]))
        return scores
    except (json.JSONDecodeError, ValueError):
        return {dim: {"score": 1, "rationale": "Scoring error."} for dim in DIMENSION_ORDER}


def generate_coaching_question(memory):
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
    return call_claude(system, "Generate your coaching question now.", max_tokens=300)


def generate_model_example(memory):
    dim_key = memory.current_dimension
    dim_info = VALUE_RUBRIC[dim_key]
    latest_scores = memory.get_latest_scores()
    dim_score = latest_scores.get(dim_key, {})
    system = MODEL_EXAMPLE_PROMPT.format(
        dimension_name=dim_info["name"],
        dimension_description=dim_info["description"],
        current_score=dim_score.get("score", 1)
    )
    return call_claude(system, "Generate the before/after example now.", max_tokens=400)


def generate_reflection_response(memory, student_response):
    step = memory.reflection_step
    if step >= len(REFLECTION_PROMPTS):
        return None
    prompt_data = REFLECTION_PROMPTS[step]
    initial = memory.get_initial_scores()
    final = memory.get_latest_scores()
    score_summary = []
    for dim in DIMENSION_ORDER:
        i_score = initial.get(dim, {}).get("score", "?")
        f_score = final.get(dim, {}).get("score", "?")
        name = VALUE_RUBRIC[dim]["name"]
        score_summary.append(f"{name}: {i_score} -> {f_score}")
    session_context = f"Session: {memory.revision_count} revision(s). Scores: {'; '.join(score_summary)}"
    system = f"{prompt_data['followup_system']}\n\nCONTEXT: {session_context}"
    return call_claude(system, f"Student said: {student_response}", max_tokens=300)


def build_celebration_message(memory, new_scores):
    initial = memory.get_initial_scores()
    improvements = []
    for dim in DIMENSION_ORDER:
        i_score = initial.get(dim, {}).get("score", 0)
        f_score = new_scores.get(dim, {}).get("score", 0)
        if f_score > i_score:
            dim_name = VALUE_RUBRIC[dim]["name"]
            improvements.append(f"**{dim_name}** went from {i_score} to {f_score}")
    
    original_essay = memory.essay_versions[0] if memory.essay_versions else ""
    final_essay = memory.get_latest_essay()
    
    msg = "## 🎉 Look at how far you've come!\n\n"
    
    if improvements:
        msg += "**Your growth:**\n"
        for imp in improvements:
            msg += f"- {imp}\n"
        msg += "\n"
    else:
        msg += "You maintained strong scores across all dimensions!\n\n"
    
    msg += "---\n\n"
    msg += "**Where you started:**\n"
    msg += f"> {original_essay[:300]}{'...' if len(original_essay) > 300 else ''}\n\n"
    msg += "**Where you are now:**\n"
    msg += f"> {final_essay[:300]}{'...' if len(final_essay) > 300 else ''}\n\n"
    msg += "---\n\n"
    msg += "You've done real work here — your writing is stronger than when we started. "
    msg += "Now let's take a moment to reflect on what you discovered in this process..."
    
    return msg


class TutorEngine:
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
        self.memory.add_essay(essay_text)
        scores = score_essay(essay_text)
        self.memory.add_scores(scores)
        
        if self.memory.all_dimensions_at_target():
            return {
                "phase": self.PHASE_REFLECT,
                "scores": scores,
                "message": "🎉 **Impressive!** Your response is strong across the board right from the start. Let's reflect on your process."
            }
        
        weak = self.memory.get_weakest_dimensions()
        if weak:
            self.memory.current_dimension = weak[0]
            self.memory.dimension_index = 0
        
        coaching_q = generate_coaching_question(self.memory)
        self.memory.coaching_turns += 1
        
        return {
            "phase": self.PHASE_COACH,
            "scores": scores,
            "coaching_question": coaching_q,
            "dimension": self.memory.current_dimension
        }

    def process_revision(self, revised_essay):
        self.memory.add_essay(revised_essay)
        self.memory.increment_revision()
        new_scores = score_essay(revised_essay)
        self.memory.add_scores(new_scores)
        
        if self.memory.all_dimensions_at_target():
            celebration = build_celebration_message(self.memory, new_scores)
            return {
                "phase": self.PHASE_REFLECT,
                "scores": new_scores,
                "message": celebration
            }
        
        if self.memory.should_end_session():
            celebration = build_celebration_message(self.memory, new_scores)
            return {
                "phase": self.PHASE_REFLECT,
                "scores": new_scores,
                "message": celebration
            }
        
        dim_key = self.memory.current_dimension
        old_scores = self.memory.scores[-2] if len(self.memory.scores) >= 2 else {}
        old_score = old_scores.get(dim_key, {}).get("score", 0)
        new_score = new_scores.get(dim_key, {}).get("score", 0)
        
        if new_score >= TARGET_SCORE:
            weak = self.memory.get_weakest_dimensions()
            if weak:
                self.memory.current_dimension = weak[0]
            else:
                celebration = build_celebration_message(self.memory, new_scores)
                return {
                    "phase": self.PHASE_REFLECT,
                    "scores": new_scores,
                    "message": celebration
                }
        
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
        step = self.memory.reflection_step
        if step >= len(REFLECTION_PROMPTS):
            self.memory.session_complete = True
            return {"phase": self.PHASE_DONE, "message": "Session complete. Great work today! 🎈"}
        
        ai_response = generate_reflection_response(self.memory, student_response)
        self.memory.reflection_step += 1
        
        if self.memory.reflection_step >= len(REFLECTION_PROMPTS):
            self.memory.session_complete = True
            return {"phase": self.PHASE_DONE, "message": ai_response}
        
        return {"phase": self.PHASE_REFLECT, "message": ai_response}
