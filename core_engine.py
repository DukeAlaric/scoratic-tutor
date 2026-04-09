"""
Socratic Writing Tutor - Core Engine v1.2

CHANGES FROM v1.1:
- Varied coaching openers (get_varied_coaching_opener)
- Conditional planning phase (only when Organization <= 2)
- Micro-celebrations for partial progress
- Quote Sandwich prompt for stuck Evidence Use
- Journey-aware celebration messages
- Intent-probing questions in coaching
- Improved first-try and improvement analysis
"""

import json
import random
import anthropic
from passage_config import (
    PASSAGE_TEXT, PASSAGE_TITLE, WRITING_PROMPT, VALUE_RUBRIC,
    DIMENSION_ORDER, TARGET_SCORE, SCORING_SYSTEM_PROMPT,
    COACHING_SYSTEM_PROMPT, MODEL_EXAMPLE_PROMPT, REFLECTION_PROMPTS,
    EDGE_CASE_RULES, RESCORE_FRAMING, ROADMAP_PROMPT, 
    COACHING_OPENERS, COACHING_OPENERS_FIRST_TRY, QUOTE_SANDWICH_PROMPT,
    CELEBRATION_MESSAGES, MICRO_CELEBRATION_TEMPLATES,
    PRE_VALIDATION_SYSTEM_PROMPT,
    get_rubric_text
)


class PreSubmissionValidator:
    """Grammarly-style pre-check that evaluates student input BEFORE formal scoring."""

    EVIDENCE_MARKERS = [
        "1962", "panopoulos", "sam", "2017", "iceland", "2019", "yougov",
        "12 percent", "hawaiian", "ontario", "canada", "tagine", "moroccan"
    ]
    POSITION_WORDS = [
        "i believe", "i think", "i argue", "i contend", "in my opinion",
        "my position", "should", "must", "belongs", "doesn't belong",
        "no place", "acceptable", "unacceptable"
    ]
    REASONING_WORDS = [
        "because", "therefore", "this means", "this shows", "which demonstrates",
        "as a result", "consequently", "this suggests", "the reason", "which is why"
    ]
    CASUAL_MARKERS = [
        "lol", "tbh", "ngl", "imo", "bruh", "like,", "gonna", "wanna",
        "kinda", "omg", "smh", "fr fr", "super gross", "it's just"
    ]

    def validate(self, essay: str) -> dict:
        """Run pre-submission validation. Tries AI first, falls back to heuristics."""
        try:
            return self._ai_check(essay)
        except Exception:
            return self._heuristic_check(essay)

    def _ai_check(self, essay: str) -> dict:
        prompt = PRE_VALIDATION_SYSTEM_PROMPT.format(
            passage_text=PASSAGE_TEXT, writing_prompt=WRITING_PROMPT
        )
        response = call_claude(prompt, f"Student draft:\n\n{essay}", max_tokens=500)
        cleaned = response.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        start = cleaned.find('{')
        end = cleaned.rfind('}') + 1
        if start >= 0 and end > start:
            result = json.loads(cleaned[start:end])
            result["word_count"] = len(essay.split())
            result["used_ai"] = True
            return result
        raise ValueError("Could not parse AI response")

    def _heuristic_check(self, essay: str) -> dict:
        lower = essay.lower()
        words = essay.split()
        sentences = [s.strip() for s in essay.replace("!", ".").replace("?", ".").split(".") if s.strip()]
        word_count = len(words)
        checks = []

        has_position = any(p in lower for p in self.POSITION_WORDS)
        checks.append({
            "objective": "POSITION",
            "status": "present" if has_position else ("weak" if word_count > 20 else "missing"),
            "tip": "" if has_position else "Try starting with a clear stance — what do you believe?"
        })

        found = [m for m in self.EVIDENCE_MARKERS if m in lower]
        ev_status = "present" if len(found) >= 2 else ("weak" if len(found) == 1 else "missing")
        checks.append({
            "objective": "EVIDENCE",
            "status": ev_status,
            "tip": "" if ev_status == "present" else "Reference specific facts — dates, names, statistics from the passage."
        })

        has_reasoning = any(r in lower for r in self.REASONING_WORDS)
        checks.append({
            "objective": "REASONING",
            "status": "present" if has_reasoning else ("weak" if word_count > 30 else "missing"),
            "tip": "" if has_reasoning else "Explain WHY — use 'because', 'this shows', or 'this means'."
        })

        checks.append({
            "objective": "STRUCTURE",
            "status": "present" if len(sentences) >= 4 else ("weak" if len(sentences) >= 2 else "missing"),
            "tip": "" if len(sentences) >= 4 else "Develop your ideas across multiple sentences — aim for 4-5."
        })

        has_casual = any(c in lower for c in self.CASUAL_MARKERS)
        checks.append({
            "objective": "TONE",
            "status": "missing" if has_casual else ("present" if word_count > 15 else "weak"),
            "tip": "Shift to academic language — replace casual phrases." if has_casual else ""
        })

        present_count = sum(1 for c in checks if c["status"] in ("present", "weak"))
        overall_ready = present_count >= 3 and word_count >= 10

        present = [c["objective"] for c in checks if c["status"] == "present"]
        missing = [c["objective"] for c in checks if c["status"] == "missing"]
        if word_count < 10:
            summary = "Your draft is very short — try expanding your ideas before submitting."
        elif len(missing) >= 3:
            summary = "You've started — now try adding a clear position, evidence, and analysis."
        elif len(present) >= 4:
            summary = "Looking strong! You've covered most of the key elements."
        elif present:
            summary = f"Good start with your {present[0].lower()}. Consider strengthening the other areas."
        else:
            summary = "Review the suggestions below to strengthen your draft."

        return {
            "overall_ready": overall_ready,
            "checks": checks,
            "summary": summary,
            "word_count": word_count,
            "used_ai": False
        }


def call_claude(system_prompt: str, user_message: str, max_tokens: int = 500) -> str:
    """Make API call to Claude."""
    client = anthropic.Anthropic()
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}]
    )
    return message.content[0].text


class SocraticMemory:
    """Tracks session state including essays, scores, and coaching history."""
    
    def __init__(self):
        self.essays = []           # All essay versions
        self.scores_history = []   # Score dict for each version
        self.coaching_history = [] # All coaching messages
        self.reflection_turn = 0   # Current reflection question index
        self.reflection_responses = []  # Student's reflection answers
        self.coaching_turns = 0    # Total coaching interactions
        self.max_coaching_turns = 15
        self.model_mode_used = set()  # Track which dimensions got MODEL examples
        self.previous_scores = {}  # For tracking dimension improvements
    
    def add_essay(self, essay: str, scores: dict):
        self.essays.append(essay)
        self.scores_history.append(scores)
        # Track previous scores for micro-celebrations
        if len(self.scores_history) > 1:
            self.previous_scores = {k: v['score'] for k, v in self.scores_history[-2].items()}
    
    def get_latest_essay(self) -> str:
        return self.essays[-1] if self.essays else ""
    
    def get_latest_scores(self) -> dict:
        return self.scores_history[-1] if self.scores_history else {}
    
    def get_revision_count(self) -> int:
        return max(0, len(self.essays) - 1)
    
    def all_dimensions_at_target(self) -> bool:
        scores = self.get_latest_scores()
        return all(scores[dim]['score'] >= TARGET_SCORE for dim in DIMENSION_ORDER)
    
    def get_lowest_dimension(self) -> tuple:
        """Returns (dimension_key, score_dict) for lowest scoring dimension."""
        scores = self.get_latest_scores()
        lowest = min(DIMENSION_ORDER, key=lambda d: scores[d]['score'])
        return lowest, scores[lowest]
    
    def get_improved_dimensions(self) -> list:
        """Returns list of dimensions that improved since last revision."""
        if not self.previous_scores:
            return []
        current = self.get_latest_scores()
        improved = []
        for dim in DIMENSION_ORDER:
            old_score = self.previous_scores.get(dim, 0)
            new_score = current[dim]['score']
            if new_score > old_score:
                improved.append({
                    'dimension': dim,
                    'name': VALUE_RUBRIC[dim]['name'],
                    'old': old_score,
                    'new': new_score
                })
        return improved
    
    def add_coaching(self, message: str):
        self.coaching_history.append(message)
        self.coaching_turns += 1
    
    def at_turn_limit(self) -> bool:
        return self.coaching_turns >= self.max_coaching_turns


class SocraticEngine:
    """Main engine for Socratic tutoring flow."""
    
    PHASE_READ = "read"
    PHASE_WRITE = "write"
    PHASE_COACH = "coach"
    PHASE_REFLECT = "reflect"
    PHASE_COMPLETE = "complete"
    
    def __init__(self):
        self.memory = SocraticMemory()
        self.current_phase = self.PHASE_READ
        self.validator = PreSubmissionValidator()
    
    def get_varied_coaching_opener(self, is_first: bool = False) -> str:
        """Get a varied coaching opener to avoid repetition."""
        if is_first:
            return random.choice(COACHING_OPENERS_FIRST_TRY)
        return random.choice(COACHING_OPENERS)
    
    def get_varied_celebration_opener(self) -> str:
        """Get varied celebration language based on revision count."""
        revisions = self.memory.get_revision_count()
        s = "s" if revisions != 1 else ""
        
        if revisions == 0:
            templates = CELEBRATION_MESSAGES["first_try"]
        elif revisions <= 2:
            templates = CELEBRATION_MESSAGES["quick_success"]
        elif revisions <= 5:
            templates = CELEBRATION_MESSAGES["solid_work"]
        elif revisions >= 8:
            templates = CELEBRATION_MESSAGES["adversarial"]
        else:
            templates = CELEBRATION_MESSAGES["persistence"]
        
        # Format with revision count
        return "\n".join([t.format(revisions=revisions, s=s) for t in templates])
    
    def get_micro_celebration(self) -> str:
        """Generate micro-celebration for improved dimensions."""
        improved = self.memory.get_improved_dimensions()
        if not improved:
            return ""
        
        celebrations = []
        for dim in improved:
            template = random.choice(MICRO_CELEBRATION_TEMPLATES)
            celebrations.append(template.format(
                dimension=dim['name'],
                old=dim['old'],
                new=dim['new']
            ))
        
        return " ".join(celebrations) + " "
    
    def score_essay(self, essay: str) -> dict:
        """Score essay against VALUE rubric."""
        system = SCORING_SYSTEM_PROMPT.format(rubric_text=get_rubric_text())
        user_msg = f"ESSAY:\n{essay}\n\nPASSAGE:\n{PASSAGE_TEXT}\n\n{EDGE_CASE_RULES}"
        
        response = call_claude(system, user_msg, max_tokens=600)
        
        # Parse JSON response
        try:
            # Find JSON in response
            start = response.find('{')
            end = response.rfind('}') + 1
            if start >= 0 and end > start:
                scores = json.loads(response[start:end])
                return scores
        except json.JSONDecodeError:
            pass
        
        # Fallback scores if parsing fails
        return {dim: {"score": 2, "rationale": "Unable to parse"} for dim in DIMENSION_ORDER}
    
    def generate_coaching(self, dimension: str, score_data: dict, essay: str) -> str:
        """Generate Socratic coaching question for a dimension."""
        system = COACHING_SYSTEM_PROMPT.format(
            dimension_name=VALUE_RUBRIC[dimension]['name'],
            current_score=score_data['score'],
            target_score=TARGET_SCORE,
            rationale=score_data['rationale'],
            essay=essay,
            passage=PASSAGE_TEXT
        )
        
        user_msg = f"Generate ONE focused coaching question for this student."
        return call_claude(system, user_msg, max_tokens=250)
    
    def generate_model_example(self, dimension: str) -> str:
        """Generate before/after example when student is stuck."""
        system = MODEL_EXAMPLE_PROMPT.format(
            dimension_name=VALUE_RUBRIC[dimension]['name']
        )
        user_msg = f"Create a brief before/after example showing how to improve {VALUE_RUBRIC[dimension]['name']}."
        return call_claude(system, user_msg, max_tokens=350)
    
    def generate_first_try_analysis(self, essay: str) -> str:
        """Generate specific praise for first-try success."""
        system = """You are a writing coach celebrating a student who wrote an excellent response on their first try.

Write 2 short paragraphs with headers:

**WHAT YOU DID WELL:**
Point out 2-3 specific things they did well. Reference their actual essay. Focus on academic writing skills: signal phrases, thesis clarity, evidence integration, vocabulary precision.

**WHY THIS WORKED:**
Explain WHY these choices made their writing strong. Help them understand the principle so they can repeat it.

Keep total response to 4-6 sentences. Be warm but specific."""
        
        user_msg = f"ESSAY:\n{essay}\n\nSCORES: All 5 dimensions at 3/4 or higher on first attempt."
        return call_claude(system, user_msg, max_tokens=350)
    
    def generate_improvement_insight(self, essay: str, first_essay: str) -> str:
        """Generate analysis of what changed between versions."""
        system = """You are a writing coach explaining what improved between essay versions.

Write a brief analysis (3-4 sentences) explaining:
1. The KEY change that made the difference
2. WHY that change strengthened the argument
3. A specific before/after example from their actual essays

Focus on academic writing improvements: evidence integration, signal phrases, thesis clarity, reasoning depth, academic register.

Keep it specific and actionable - reference their actual words."""
        
        user_msg = f"FIRST ESSAY:\n{first_essay}\n\nFINAL ESSAY:\n{essay}"
        return call_claude(system, user_msg, max_tokens=300)
    
    def should_show_roadmap(self) -> bool:
        """Determine if roadmap prompt should be shown (only when Organization <= 2)."""
        scores = self.memory.get_latest_scores()
        if not scores:
            return True  # Show on first submission
        return scores.get('organization', {}).get('score', 0) <= 2
    
    def process_initial_essay(self, essay: str) -> dict:
        """Process first essay submission."""
        scores = self.score_essay(essay)
        self.memory.add_essay(essay, scores)
        
        # Check if already at target
        if self.memory.all_dimensions_at_target():
            analysis = self.generate_first_try_analysis(essay)
            
            message = f"## ✓ {CELEBRATION_MESSAGES['first_try'][0]}\n\n"
            message += f"{CELEBRATION_MESSAGES['first_try'][1]}\n\n"
            message += f"{analysis}\n\n"
            message += "---\n\n"
            message += "**Your essay:**\n\n"
            message += f"> {essay}\n\n"
            message += "---\n\n"
            message += "Since your writing is already strong, let's reflect on your process so you can repeat this next time."
            
            return {
                "phase": self.PHASE_REFLECT,
                "scores": scores,
                "message": message
            }
        
        # Generate coaching for lowest dimension
        lowest_dim, lowest_data = self.memory.get_lowest_dimension()
        coaching = self.generate_coaching(lowest_dim, lowest_data, essay)
        self.memory.add_coaching(coaching)
        
        # Build response with conditional roadmap
        opener = self.get_varied_coaching_opener(is_first=True)
        
        message = f"{opener}\n\n"
        
        # Only show roadmap if Organization is low
        if self.should_show_roadmap():
            message += f"**{ROADMAP_PROMPT}**\n\n"
        
        message += f"Here's my first question for you:\n\n{coaching}"
        
        return {
            "phase": self.PHASE_COACH,
            "scores": scores,
            "message": message,
            "focus_dimension": lowest_dim
        }
    
    def process_revision(self, essay: str) -> dict:
        """Process a revision submission."""
        prev_scores = self.memory.get_latest_scores()
        new_scores = self.score_essay(essay)
        self.memory.add_essay(essay, new_scores)
        
        # Check if at target
        if self.memory.all_dimensions_at_target():
            return self._build_success_message(essay)
        
        # Check turn limit
        if self.memory.at_turn_limit():
            return self._build_turn_limit_message()
        
        # Find lowest dimension and check for improvement
        lowest_dim, lowest_data = self.memory.get_lowest_dimension()
        prev_score = prev_scores.get(lowest_dim, {}).get('score', 0)
        new_score = lowest_data['score']
        
        # Generate micro-celebration for any improvements
        micro_celeb = self.get_micro_celebration()
        
        # Check if stuck on same dimension (trigger MODEL mode)
        if new_score <= prev_score and lowest_dim in self.memory.model_mode_used:
            # Already tried MODEL mode, try different approach
            coaching = self.generate_coaching(lowest_dim, lowest_data, essay)
            self.memory.add_coaching(coaching)
            
            message = micro_celeb if micro_celeb else ""
            message += f"{coaching}"
            
            return {
                "phase": self.PHASE_COACH,
                "scores": new_scores,
                "message": message,
                "focus_dimension": lowest_dim
            }
        
        elif new_score <= prev_score:
            # First time stuck - use MODEL mode
            self.memory.model_mode_used.add(lowest_dim)
            
            # Special handling for Evidence Use - use Quote Sandwich
            if lowest_dim == "evidence_use":
                model_example = QUOTE_SANDWICH_PROMPT
            else:
                model_example = self.generate_model_example(lowest_dim)
            
            self.memory.add_coaching(model_example)
            
            message = f"## 📋 Let me show you an example:\n\n"
            message += f"Your {VALUE_RUBRIC[lowest_dim]['name']} score hasn't moved yet, and that's okay - this one can be tricky. "
            message += f"Let me show you an example of what I mean:\n\n"
            message += f"{model_example}"
            
            return {
                "phase": self.PHASE_COACH,
                "scores": new_scores,
                "message": message,
                "focus_dimension": lowest_dim
            }
        
        else:
            # Score improved, generate new coaching
            coaching = self.generate_coaching(lowest_dim, lowest_data, essay)
            self.memory.add_coaching(coaching)
            
            # Build message with micro-celebration
            opener = self.get_varied_coaching_opener()
            
            message = ""
            if micro_celeb:
                message += f"{micro_celeb}\n\n"
            
            # Only show roadmap if Organization is still low
            if self.should_show_roadmap():
                message += f"**{ROADMAP_PROMPT}**\n\n"
            
            message += f"{coaching}"
            
            return {
                "phase": self.PHASE_COACH,
                "scores": new_scores,
                "message": message,
                "focus_dimension": lowest_dim
            }
    
    def _build_success_message(self, essay: str) -> dict:
        """Build the success/celebration message."""
        scores = self.memory.get_latest_scores()
        revisions = self.memory.get_revision_count()
        
        # Get journey-aware opener
        celebration_opener = self.get_varied_celebration_opener()
        
        # Generate improvement insight
        if revisions > 0:
            first_essay = self.memory.essays[0]
            improvement_insight = self.generate_improvement_insight(essay, first_essay)
        else:
            improvement_insight = ""
        
        message = f"## ✓ {celebration_opener}\n\n"
        
        # Show score progress
        if revisions > 0:
            message += "**What changed:**\n\n"
            for dim in DIMENSION_ORDER:
                first_score = self.memory.scores_history[0][dim]['score']
                final_score = scores[dim]['score']
                if final_score > first_score:
                    message += f"- **{VALUE_RUBRIC[dim]['name']}:** {first_score} → {final_score} ⬆️\n"
                else:
                    message += f"- **{VALUE_RUBRIC[dim]['name']}:** {first_score} → {final_score} ➡️\n"
            message += "\n"
        
        # Add improvement insight
        if improvement_insight:
            message += f"**What made the difference:** {improvement_insight}\n\n"
        
        message += "---\n\n"
        message += "**Where you started:**\n\n"
        message += f"> {self.memory.essays[0]}\n\n"
        message += "**Where you are now:**\n\n"
        message += f"> {essay}\n\n"
        message += "---\n\n"
        message += "Your writing is stronger now. Let's take a few minutes to reflect on what you learned so you can use these skills again."
        
        return {
            "phase": self.PHASE_REFLECT,
            "scores": scores,
            "message": message
        }
    
    def _build_turn_limit_message(self) -> dict:
        """Build message when coaching turn limit is reached."""
        scores = self.memory.get_latest_scores()
        essay = self.memory.get_latest_essay()
        
        message = "## Session Limit Reached\n\n"
        message += f"We've worked through {self.memory.coaching_turns} coaching turns together. "
        message += "Let's pause and reflect on what you've learned.\n\n"
        
        # Show final scores
        message += "**Your final scores:**\n"
        for dim in DIMENSION_ORDER:
            score = scores[dim]['score']
            status = "🟢" if score >= TARGET_SCORE else "🟡" if score == 2 else "🔴"
            message += f"- {status} {VALUE_RUBRIC[dim]['name']}: {score}/4\n"
        
        message += "\n---\n\n"
        message += "**Your essay:**\n\n"
        message += f"> {essay}\n\n"
        message += "---\n\n"
        message += "Let's reflect on what you learned during this session."
        
        return {
            "phase": self.PHASE_REFLECT,
            "scores": scores,
            "message": message
        }
    
    def process_reflection(self, response: str) -> dict:
        """Process reflection response and return next reflection or completion."""
        self.memory.reflection_responses.append(response)
        
        # Get current reflection prompt
        current_prompt = REFLECTION_PROMPTS[self.memory.reflection_turn]
        
        # Generate followup to their response
        followup = call_claude(
            current_prompt['followup_system'],
            f"Student said: {response}",
            max_tokens=150
        )
        
        # Move to next reflection turn
        self.memory.reflection_turn += 1
        
        # Check if more reflection questions
        if self.memory.reflection_turn < len(REFLECTION_PROMPTS):
            next_question = REFLECTION_PROMPTS[self.memory.reflection_turn]['question']
            return {
                "phase": self.PHASE_REFLECT,
                "message": f"{followup}\n\n**{next_question}**"
            }
        else:
            # Reflection complete
            return {
                "phase": self.PHASE_COMPLETE,
                "message": followup
            }
    
    def get_session_stats(self) -> dict:
        """Return session statistics."""
        return {
            "revisions": self.memory.get_revision_count(),
            "coaching_turns": self.memory.coaching_turns,
            "essay_versions": len(self.memory.essays),
            "reflection_turns": self.memory.reflection_turn,
            "final_scores": self.memory.get_latest_scores()
        }
