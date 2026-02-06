"""
Core Engine for Socratic Writing Tutor v1.2
"""
import json
import anthropic
from passage_config import (
    PASSAGE_TEXT, WRITING_PROMPT, VALUE_RUBRIC, DIMENSION_ORDER, TARGET_SCORE,
    SCORING_SYSTEM_PROMPT, COACHING_SYSTEM_PROMPT, MODEL_EXAMPLE_PROMPT,
    REFLECTION_PROMPTS, EDGE_CASE_RULES, RESCORE_FRAMING, ROADMAP_PROMPT,
    QUOTE_SANDWICH_PROMPT, get_rubric_text, get_coaching_opener,
    get_micro_celebration, get_celebration_opener
)

def call_claude(system_prompt: str, user_message: str, max_tokens: int = 500) -> str:
    client = anthropic.Anthropic()
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}]
    )
    return message.content[0].text


class SocraticMemory:
    def __init__(self):
        self.essays = []
        self.scores_history = []
        self.coaching_history = []
        self.reflection_turn = 0
        self.reflection_responses = []
        self.coaching_turns = 0
        self.max_coaching_turns = 15
        self.model_mode_used = set()
        self.previous_scores = {}

    def add_essay(self, essay: str, scores: dict):
        if self.scores_history:
            self.previous_scores = {k: v['score'] for k, v in self.scores_history[-1].items()}
        self.essays.append(essay)
        self.scores_history.append(scores)

    def get_latest_essay(self) -> str:
        return self.essays[-1] if self.essays else ""

    def get_latest_scores(self) -> dict:
        return self.scores_history[-1] if self.scores_history else {}

    def get_revision_count(self) -> int:
        return max(0, len(self.essays) - 1)

    def all_dimensions_at_target(self) -> bool:
        scores = self.get_latest_scores()
        return all(scores.get(dim, {}).get('score', 0) >= TARGET_SCORE for dim in DIMENSION_ORDER)

    def get_lowest_dimension(self) -> tuple:
        scores = self.get_latest_scores()
        lowest = min(DIMENSION_ORDER, key=lambda d: scores.get(d, {}).get('score', 0))
        return lowest, scores.get(lowest, {})

    def get_improved_dimensions(self) -> list:
        if not self.previous_scores:
            return []
        current = self.get_latest_scores()
        improved = []
        for dim in DIMENSION_ORDER:
            old = self.previous_scores.get(dim, 0)
            new = current.get(dim, {}).get('score', 0)
            if new > old:
                improved.append({'dim': dim, 'name': VALUE_RUBRIC[dim]['name'], 'old': old, 'new': new})
        return improved

    def add_coaching(self, message: str):
        self.coaching_history.append(message)
        self.coaching_turns += 1

    def at_turn_limit(self) -> bool:
        return self.coaching_turns >= self.max_coaching_turns


class SocraticEngine:
    PHASE_INTRO = "intro"
    PHASE_WRITE = "write"
    PHASE_COACH = "coach"
    PHASE_REFLECT = "reflect"
    PHASE_DONE = "done"

    def __init__(self):
        self.memory = SocraticMemory()
        self.phase = self.PHASE_INTRO

    def score_essay(self, essay: str) -> dict:
        system = SCORING_SYSTEM_PROMPT.format(rubric_text=get_rubric_text())
        user_msg = f"ESSAY:\n{essay}\n\nPASSAGE:\n{PASSAGE_TEXT}\n\n{EDGE_CASE_RULES}"
        response = call_claude(system, user_msg, max_tokens=600)
        try:
            start = response.find('{')
            end = response.rfind('}') + 1
            if start >= 0 and end > start:
                return json.loads(response[start:end])
        except json.JSONDecodeError:
            pass
        return {dim: {"score": 2, "rationale": "Parse error"} for dim in DIMENSION_ORDER}

    def generate_coaching(self, dimension: str, score_data: dict, essay: str) -> str:
        system = COACHING_SYSTEM_PROMPT.format(
            dimension_name=VALUE_RUBRIC[dimension]['name'],
            current_score=score_data.get('score', 1),
            target_score=TARGET_SCORE,
            rationale=score_data.get('rationale', ''),
            essay=essay,
            passage=PASSAGE_TEXT
        )
        return call_claude(system, "Generate ONE focused coaching question.", max_tokens=250)

    def generate_model_example(self, dimension: str) -> str:
        system = MODEL_EXAMPLE_PROMPT.format(dimension_name=VALUE_RUBRIC[dimension]['name'])
        return call_claude(system, f"Create before/after example for {VALUE_RUBRIC[dimension]['name']}.", max_tokens=300)

    def should_show_roadmap(self) -> bool:
        scores = self.memory.get_latest_scores()
        return scores.get('organization', {}).get('score', 0) <= 2

    def process_essay(self, essay: str) -> dict:
        scores = self.score_essay(essay)
        self.memory.add_essay(essay, scores)

        if self.memory.all_dimensions_at_target():
            return self._build_success_response()

        if self.memory.at_turn_limit():
            return self._build_limit_response()

        lowest_dim, lowest_data = self.memory.get_lowest_dimension()
        prev_score = self.memory.previous_scores.get(lowest_dim, 0)
        new_score = lowest_data.get('score', 0)

        # Build micro-celebration for improved dimensions
        micro = ""
        for imp in self.memory.get_improved_dimensions():
            micro += get_micro_celebration(imp['name'], imp['old'], imp['new']) + " "

        # Check if stuck - use MODEL mode or Quote Sandwich
        if new_score <= prev_score and self.memory.get_revision_count() > 0:
            if lowest_dim in self.memory.model_mode_used:
                coaching = self.generate_coaching(lowest_dim, lowest_data, essay)
            else:
                self.memory.model_mode_used.add(lowest_dim)
                if lowest_dim == "evidence_use":
                    coaching = f"**Let me show you a technique:**\n\n{QUOTE_SANDWICH_PROMPT}"
                else:
                    coaching = f"**Let me show you an example:**\n\n{self.generate_model_example(lowest_dim)}"
        else:
            coaching = self.generate_coaching(lowest_dim, lowest_data, essay)

        self.memory.add_coaching(coaching)

        # Build message
        is_first = self.memory.get_revision_count() == 0
        opener = get_coaching_opener(is_first)
        
        message = f"{opener}\n\n"
        if micro:
            message += f"{micro.strip()}\n\n"
        if self.should_show_roadmap():
            message += f"**{ROADMAP_PROMPT}**\n\n"
        message += f"Here's my feedback:\n\n{coaching}"

        self.phase = self.PHASE_COACH
        return {"phase": self.PHASE_COACH, "scores": scores, "message": message, "focus": lowest_dim}

    def _build_success_response(self) -> dict:
        scores = self.memory.get_latest_scores()
        revisions = self.memory.get_revision_count()
        opener = get_celebration_opener(revisions)

        message = f"## ✓ {opener}\n\n"
        
        if revisions > 0:
            for dim in DIMENSION_ORDER:
                first = self.memory.scores_history[0].get(dim, {}).get('score', 0)
                final = scores.get(dim, {}).get('score', 0)
                arrow = "⬆️" if final > first else "➡️"
                message += f"- **{VALUE_RUBRIC[dim]['name']}:** {first} → {final} {arrow}\n"
            message += "\n"

        message += f"**Where you started:**\n> {self.memory.essays[0]}\n\n"
        message += f"**Where you are now:**\n> {self.memory.get_latest_essay()}\n\n"
        message += "---\n\nYour writing is stronger now. Let's reflect on what you learned."

        self.phase = self.PHASE_REFLECT
        return {"phase": self.PHASE_REFLECT, "scores": scores, "message": message}

    def _build_limit_response(self) -> dict:
        scores = self.memory.get_latest_scores()
        message = f"## Session Limit\n\nWe've done {self.memory.coaching_turns} coaching turns. Let's reflect on your progress.\n\n"
        message += f"**Your essay:**\n> {self.memory.get_latest_essay()}"
        self.phase = self.PHASE_REFLECT
        return {"phase": self.PHASE_REFLECT, "scores": scores, "message": message}

    def process_reflection(self, response: str) -> dict:
        self.memory.reflection_responses.append(response)
        turn = self.memory.reflection_turn
        
        if turn >= len(REFLECTION_PROMPTS):
            self.phase = self.PHASE_DONE
            return {"phase": self.PHASE_DONE, "message": "Session complete. Great work today!"}

        prompt = REFLECTION_PROMPTS[turn]
        system = f"You are a writing coach. {prompt['followup']}"
        ai_response = call_claude(system, f"Student said: {response}", max_tokens=150)
        
        self.memory.reflection_turn += 1
        
        if self.memory.reflection_turn >= len(REFLECTION_PROMPTS):
            self.phase = self.PHASE_DONE
            return {"phase": self.PHASE_DONE, "message": ai_response}
        
        return {"phase": self.PHASE_REFLECT, "message": ai_response}

    def get_current_reflection_question(self) -> str:
        turn = self.memory.reflection_turn
        if turn < len(REFLECTION_PROMPTS):
            return REFLECTION_PROMPTS[turn]['question']
        return ""

    def get_session_stats(self) -> dict:
        return {
            "revisions": self.memory.get_revision_count(),
            "coaching_turns": self.memory.coaching_turns,
            "essay_versions": len(self.memory.essays)
        }