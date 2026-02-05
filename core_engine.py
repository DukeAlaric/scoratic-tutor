"""
Socratic Writing Tutor - Core Engine v0.3 (Revision Loop)
==========================================================
The key insight: a tutor that only asks questions produces reflection
without action. This version adds a REVISION LOOP:

  Question -> Student Insight -> "Lets revise that" -> Student Edits ->
  Updated Essay -> Re-score -> Next Question or Celebrate

The student sees their writing improve IN REAL TIME during the session.

Architecture: SOAR pattern (State, Operator, And, Result)
Reference: HwanieKim/Socratic_Tutor (MIT License)
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional
from datetime import datetime
import json
import os
import copy


# ============================================================
# DATA MODELS
# ============================================================

class DialogueMode(Enum):
    """Three-stroke cycle: ASK, then MODEL if stuck, then REVISE."""
    ASK = "ask"           # Tutor asks a Socratic question
    MODEL = "model"       # Tutor shows a before/after example using student's own sentence
    REVISE = "revise"     # Tutor invites student to edit their essay


class StudentIntent(Enum):
    DIRECT_ANSWER = "direct_answer"
    FOLLOW_UP = "follow_up"
    META_QUESTION = "meta_question"
    DEFLECTION = "deflection"
    INSIGHT = "insight"
    REVISION_PLAN = "revision_plan"
    OFF_TOPIC = "off_topic"


class LearnerLevel(Enum):
    L1_RECOGNITION = 1
    L2_COMPREHENSION = 2
    L3_ANALYSIS = 3
    L4_EVALUATION = 4
    L5_CREATION = 5


class ScaffoldStrategy(Enum):
    NARROW_FOCUS = "narrow_focus"
    PROVIDE_OPTIONS = "provide_options"
    POINT_TO_TEXT = "point_to_text"
    REFRAME = "reframe"
    VALIDATE_AND_PUSH = "validate_and_push"
    METACOGNITIVE = "metacognitive"
    SYNTHESIZE = "synthesize"


@dataclass
class RubricScore:
    dimension: str
    dimension_name: str
    score: int
    rationale: str
    level_description: str


@dataclass
class MultidimensionalAssessment:
    scores: list
    weakest_dimension: str
    weakest_score: int
    strongest_dimension: str
    strongest_score: int
    overall_average: float
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

    def to_dict(self):
        return {
            "scores": [asdict(s) for s in self.scores],
            "weakest_dimension": self.weakest_dimension,
            "weakest_score": self.weakest_score,
            "strongest_dimension": self.strongest_dimension,
            "strongest_score": self.strongest_score,
            "overall_average": self.overall_average,
            "timestamp": self.timestamp,
        }


@dataclass
class DialogueTurn:
    turn_number: int
    mode: str  # "ask" or "revise"
    question: str
    student_response: str = ""
    intent: str = ""
    scaffold_used: str = ""
    learner_level: int = 1
    essay_before: str = ""
    essay_after: str = ""
    score_before: int = 0
    score_after: int = 0
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


@dataclass
class SessionData:
    session_id: str
    original_essay: str
    final_essay: str
    prompt_title: str
    rubric_name: str
    initial_assessment: dict
    final_assessment: dict
    dialogue_turns: list
    revision_count: int = 0
    score_delta: float = 0.0
    reflection: str = ""
    learner_level_start: int = 1
    learner_level_end: int = 1
    started_at: str = ""
    completed_at: str = ""

    def __post_init__(self):
        if not self.started_at:
            self.started_at = datetime.now().isoformat()

    def to_json(self):
        return json.dumps(asdict(self), indent=2)


# ============================================================
# AAC&U VALUE RUBRIC
# ============================================================

VALUE_RUBRIC = {
    "context_and_purpose": {
        "name": "Context & Purpose",
        "description": "Includes considerations of audience, purpose, and the circumstances surrounding the writing task(s).",
        "levels": {
            4: "Demonstrates a thorough understanding of context, audience, and purpose that is responsive to the assigned task(s) and focuses all elements of the work.",
            3: "Demonstrates adequate consideration of context, audience, and purpose and a clear focus on the assigned task(s).",
            2: "Demonstrates awareness of context, audience, purpose, and to the assigned task(s).",
            1: "Demonstrates minimal attention to context, audience, purpose, and to the assigned task(s).",
        },
    },
    "content_development": {
        "name": "Content Development",
        "description": "The ways in which the text explores and represents its topic in relation to its audience and purpose.",
        "levels": {
            4: "Uses appropriate, relevant, and compelling content to illustrate mastery of the subject, conveying the writer's understanding, and shaping the whole work.",
            3: "Uses appropriate, relevant, and compelling content to explore ideas within the context of the discipline and shape the whole work.",
            2: "Uses appropriate and relevant content to develop and explore ideas through most of the work.",
            1: "Uses appropriate and relevant content to develop simple ideas in some parts of the work.",
        },
    },
    "genre_and_conventions": {
        "name": "Genre & Disciplinary Conventions",
        "description": "Formal and informal rules inherent in the expectations for writing in particular forms and/or academic fields.",
        "levels": {
            4: "Demonstrates detailed attention to and successful execution of a wide range of conventions particular to a specific discipline and/or writing task(s) including organization, content, presentation, formatting, and stylistic choices.",
            3: "Demonstrates consistent use of important conventions particular to a specific discipline and/or writing task(s), including organization, content, presentation, and stylistic choices.",
            2: "Follows expectations appropriate to a specific discipline and/or writing task(s) for basic organization, content, and presentation.",
            1: "Attempts to use a consistent system for basic organization and presentation.",
        },
    },
    "sources_and_evidence": {
        "name": "Sources & Evidence",
        "description": "The quality and use of sources and evidence to support ideas.",
        "levels": {
            4: "Demonstrates skillful use of high-quality, credible, relevant sources to develop ideas that are appropriate for the discipline and genre of the writing.",
            3: "Demonstrates consistent use of credible, relevant sources to support ideas that are situated within the discipline and genre of the writing.",
            2: "Demonstrates an attempt to use credible and/or relevant sources to support ideas that are appropriate for the discipline and genre of the writing.",
            1: "Demonstrates an attempt to use sources to support ideas in the writing.",
        },
    },
    "syntax_and_mechanics": {
        "name": "Syntax & Mechanics",
        "description": "Control of language, grammar, and mechanics.",
        "levels": {
            4: "Uses graceful language that skillfully communicates meaning to readers with clarity and fluency, and is virtually error-free.",
            3: "Uses straightforward language that generally conveys meaning to readers. The language has few errors.",
            2: "Uses language that generally conveys meaning to readers with clarity, although writing may include some errors.",
            1: "Uses language that sometimes impedes meaning because of errors in usage.",
        },
    },
}


# ============================================================
# INTENT CLASSIFIER
# ============================================================

class IntentClassifier:
    INTENT_SIGNALS = {
        StudentIntent.INSIGHT: [
            "i realize", "i see now", "i notice", "i didn't think about",
            "that makes sense", "i understand", "oh", "so that's why",
            "i should have", "now i see", "i get it",
        ],
        StudentIntent.REVISION_PLAN: [
            "i would change", "i'd revise", "next time", "i'll add",
            "i should include", "i need to", "my plan is", "i want to fix",
            "i could improve", "the revision",
        ],
        StudentIntent.FOLLOW_UP: [
            "what do you mean", "can you explain", "i'm not sure what",
            "could you clarify", "like what", "such as", "for example",
            "how do i", "what would that look like",
        ],
        StudentIntent.META_QUESTION: [
            "why are you asking", "what's the point", "how does this help",
            "what are we doing", "is this graded", "what's the purpose",
        ],
        StudentIntent.DEFLECTION: [
            "i don't know", "i'm not sure", "whatever", "it doesn't matter",
            "i guess", "maybe", "probably",
        ],
    }

    @staticmethod
    def classify(response: str) -> StudentIntent:
        lower = response.lower().strip()
        if len(lower.split()) < 4:
            return StudentIntent.DEFLECTION
        scores = {}
        for intent, signals in IntentClassifier.INTENT_SIGNALS.items():
            score = sum(1 for s in signals if s in lower)
            if score > 0:
                scores[intent] = score
        if scores:
            return max(scores, key=scores.get)
        return StudentIntent.DIRECT_ANSWER

    @staticmethod
    def classify_with_ai(response: str, question: str, api_call_fn) -> StudentIntent:
        prompt = f"""Classify this student response into exactly one category.

The tutor asked: "{question}"
The student replied: "{response}"

Categories:
- DIRECT_ANSWER: Student is answering the question
- FOLLOW_UP: Student wants clarification
- META_QUESTION: Student asks about the process
- DEFLECTION: Student avoids the question
- INSIGHT: Student arrives at a discovery
- REVISION_PLAN: Student articulates a concrete change
- OFF_TOPIC: Response doesn't relate

Respond with ONLY the category name."""

        result = api_call_fn(
            "You are a classification system. Respond with only the category name.",
            prompt,
        )
        if result:
            intent_map = {
                "DIRECT_ANSWER": StudentIntent.DIRECT_ANSWER,
                "FOLLOW_UP": StudentIntent.FOLLOW_UP,
                "META_QUESTION": StudentIntent.META_QUESTION,
                "DEFLECTION": StudentIntent.DEFLECTION,
                "INSIGHT": StudentIntent.INSIGHT,
                "REVISION_PLAN": StudentIntent.REVISION_PLAN,
                "OFF_TOPIC": StudentIntent.OFF_TOPIC,
            }
            return intent_map.get(result.strip().upper(), StudentIntent.DIRECT_ANSWER)
        return IntentClassifier.classify(response)


# ============================================================
# ANSWER EVALUATOR
# ============================================================

class AnswerEvaluator:
    @staticmethod
    def build_rubric_prompt(scoring_anchors=None, creative_policy=None, edge_case_framework=None) -> str:
        """Build rubric text - uses scoring anchors if available, falls back to VALUE_RUBRIC."""
        if scoring_anchors:
            text = ""
            for key, anchor in scoring_anchors.items():
                text += f"\n### {anchor['name']}\n"
                for level in [4, 3, 2, 1]:
                    a = anchor['anchors'][level]
                    text += f"  Level {level}: {a['descriptor']}\n"
                    text += f"    Looks like: {a['looks_like']}\n"
                    text += f"    Signal: {a['example_signal']}\n"
                if 'edge_case_3v4' in anchor:
                    text += f"  3 vs 4 decision: {anchor['edge_case_3v4']}\n"
                if 'creative_connection_guidance' in anchor:
                    text += f"  Creative connections: {anchor['creative_connection_guidance']}\n"
            if creative_policy:
                text += f"\n{creative_policy}\n"
            if edge_case_framework:
                text += f"\n{edge_case_framework}\n"
            return text
        # Fallback to basic VALUE rubric
        text = ""
        for key, dim in VALUE_RUBRIC.items():
            text += f"\n### {dim['name']}\n{dim['description']}\n"
            for level, desc in dim['levels'].items():
                text += f"  Level {level}: {desc}\n"
        return text

    @staticmethod
    def assess(essay_text: str, prompt_text: str, api_call_fn=None,
               scoring_anchors=None, creative_policy=None, edge_case_framework=None,
               passage_text=None) -> MultidimensionalAssessment:
        rubric_text = AnswerEvaluator.build_rubric_prompt(scoring_anchors, creative_policy, edge_case_framework)
        system_prompt = """You are a writing coach giving a student feedback on their analytical response to a reading passage. You use the AAC&U VALUE Written Communication Rubric to score, but your TONE is warm, specific, and grounded in THEIR ACTUAL WRITING.

Score the student on each of 5 dimensions using levels 1-4.
For each dimension, write a 2-4 sentence "rationale" that follows these rules:

RULE 1 - QUOTE THEIR WORDS: Every rationale MUST include at least one short quote from the student's actual essay. Put quotes in double-quotes. This proves you read their work, not just scored it.

RULE 2 - BE SPECIFIC: Never say vague things like "could be stronger" or "needs more development." Instead, name exactly what you see and what the next move is. Point at a specific sentence or paragraph.

RULE 3 - FRAME GROWTH AS COLLABORATIVE: Use "let's" not "you should." This is a coaching conversation, not a verdict. "Let's look at where you wrote X - we can push that further" not "You need to improve X."

RULE 4 - LEAD WITH WHAT WORKS: Even at a score of 1, find something real to validate. Energy, opinion, a good instinct, a phrase that shows promise. Then pivot to growth.

TONE EXAMPLES (notice the quotes from the essay):

- Score 3, Context: "Not a bad start at all - you clearly picked a side and committed to it. Where you wrote 'the passage makes a stronger case for pineapple' that sets up your whole argument. Let's talk about how to make your opening do even more work - right now it tells me your position but not WHY this question is interesting."

- Score 2, Sources: "You mention that 'some people think pineapple is gross' but the passage actually gave you specific ammunition - the YouGov poll, the Iceland president, the food science angle. Let's look at swapping some of your general claims for those concrete details."

- Score 4, Syntax: "Your writing has real personality - I especially like the rhythm in your closing paragraph. The way you land on that short sentence after the longer one gives it punch. Clean, confident, distinctly yours."

- Score 1, Content: "I can feel that you have a strong opinion here, and that matters! Right now though, most of your argument is coming from personal taste rather than the passage. Let's start with one specific detail from the text - even just one - and build from there."

BAD EXAMPLES (never do this):
- "The response clearly addresses the prompt and takes a position." (Clinical. Generic. Could describe anyone's essay.)
- "Awareness of audience and purpose could be stronger." (Meaningless to a student. What audience? What purpose? What specifically?)
- "Content development is adequate." (Adequate is a grade, not feedback.)

IMPORTANT SCORING PRINCIPLES:
- Use the concrete anchors and "looks like" examples to calibrate scores
- When torn between adjacent levels, use the edge-case guidance
- Reward creative connections that genuinely deepen the analysis
- Most student writing falls in the 2-3 range - a 4 requires something distinctive
- Benefit of the doubt goes to the student

Respond ONLY in valid JSON:
{
    "context_and_purpose": {"score": N, "rationale": "..."},
    "content_development": {"score": N, "rationale": "..."},
    "genre_and_conventions": {"score": N, "rationale": "..."},
    "sources_and_evidence": {"score": N, "rationale": "..."},
    "syntax_and_mechanics": {"score": N, "rationale": "..."}
}"""

        passage_section = ""
        if passage_text:
            passage_section = f"\nReading passage the student was given:\n---\n{passage_text}\n---\n"

        user_msg = f"Rubric with scoring anchors:\n{rubric_text}\n{passage_section}\nWriting prompt:\n{prompt_text}\n\nStudent response:\n---\n{essay_text}\n---\n\nScore all 5 dimensions. Return ONLY valid JSON."

        raw_scores = None
        if api_call_fn:
            result = api_call_fn(system_prompt, user_msg)
            if result:
                try:
                    cleaned = result.strip()
                    if cleaned.startswith("```"):
                        cleaned = cleaned.split("\n", 1)[1].rsplit("```", 1)[0]
                    raw_scores = json.loads(cleaned)
                except (json.JSONDecodeError, IndexError):
                    pass

        if not raw_scores:
            raw_scores = {
                "context_and_purpose": {"score": 2, "rationale": "You picked a side, which is the right instinct. Where you wrote 'I think pineapple is fine on pizza' - that is your thesis doing its job. Let's work on framing it as an analytical claim about the passage rather than a personal preference, and your whole response will sharpen up."},
                "content_development": {"score": 3, "rationale": "You brought in the YouGov poll and the bit about Sam Panopoulos, which shows you were reading carefully. Where you wrote 'this shows people disagree' - let's push on that. WHY does it matter that people disagree? That is where your analysis goes from reporting to interpreting."},
                "genre_and_conventions": {"score": 2, "rationale": "I can follow your thinking, but right now it reads like one long train of thought. Where you shift from talking about tradition to talking about taste - that is actually a natural paragraph break. Let's look at giving your argument some structure so each point gets room to land."},
                "sources_and_evidence": {"score": 1, "rationale": "This is where we have the most room to grow together. You have strong opinions, but right now the passage is doing almost none of the heavy lifting. It gave you real evidence - polls, history, food science. Let's pick even just one specific detail and build an argument around it."},
                "syntax_and_mechanics": {"score": 3, "rationale": "Your writing is clear and I never had to re-read a sentence to get your meaning, which is no small thing. Where you wrote 'at the end of the day' - let's see if we can find a more precise way to land that thought. Small word-choice upgrades can give your voice more punch."},
            }

        scores = []
        for key, data in raw_scores.items():
            dim = VALUE_RUBRIC.get(key, {})
            sv = data.get("score", 2)
            scores.append(RubricScore(
                dimension=key, dimension_name=dim.get("name", key),
                score=sv, rationale=data.get("rationale", ""),
                level_description=dim.get("levels", {}).get(sv, ""),
            ))

        sorted_scores = sorted(scores, key=lambda s: s.score)
        return MultidimensionalAssessment(
            scores=scores,
            weakest_dimension=sorted_scores[0].dimension,
            weakest_score=sorted_scores[0].score,
            strongest_dimension=sorted_scores[-1].dimension,
            strongest_score=sorted_scores[-1].score,
            overall_average=round(sum(s.score for s in scores) / len(scores), 2),
        )

    @staticmethod
    def score_single_dimension(essay_text: str, prompt_text: str, dimension_key: str, api_call_fn=None) -> int:
        """Re-score a single dimension after revision."""
        dim = VALUE_RUBRIC.get(dimension_key, {})
        system_prompt = f"""Score this essay on ONE dimension of the AAC&U VALUE rubric.

Dimension: {dim.get('name', '')}
Description: {dim.get('description', '')}
Levels:
  4: {dim['levels'][4]}
  3: {dim['levels'][3]}
  2: {dim['levels'][2]}
  1: {dim['levels'][1]}

Respond with ONLY a single digit (1, 2, 3, or 4). Nothing else."""

        user_msg = f"Prompt:\n{prompt_text}\n\nEssay:\n---\n{essay_text}\n---\n\nScore (1-4):"

        if api_call_fn:
            result = api_call_fn(system_prompt, user_msg)
            if result:
                for ch in result.strip():
                    if ch in "1234":
                        return int(ch)
        return 2


# ============================================================
# SCAFFOLDING SYSTEM
# ============================================================

class ScaffoldingSystem:
    STRATEGY_MATRIX = {
        StudentIntent.DIRECT_ANSWER: {
            LearnerLevel.L1_RECOGNITION: ScaffoldStrategy.NARROW_FOCUS,
            LearnerLevel.L2_COMPREHENSION: ScaffoldStrategy.POINT_TO_TEXT,
            LearnerLevel.L3_ANALYSIS: ScaffoldStrategy.VALIDATE_AND_PUSH,
            LearnerLevel.L4_EVALUATION: ScaffoldStrategy.METACOGNITIVE,
            LearnerLevel.L5_CREATION: ScaffoldStrategy.SYNTHESIZE,
        },
        StudentIntent.DEFLECTION: {
            LearnerLevel.L1_RECOGNITION: ScaffoldStrategy.PROVIDE_OPTIONS,
            LearnerLevel.L2_COMPREHENSION: ScaffoldStrategy.PROVIDE_OPTIONS,
            LearnerLevel.L3_ANALYSIS: ScaffoldStrategy.REFRAME,
            LearnerLevel.L4_EVALUATION: ScaffoldStrategy.REFRAME,
            LearnerLevel.L5_CREATION: ScaffoldStrategy.REFRAME,
        },
        StudentIntent.FOLLOW_UP: {
            LearnerLevel.L1_RECOGNITION: ScaffoldStrategy.NARROW_FOCUS,
            LearnerLevel.L2_COMPREHENSION: ScaffoldStrategy.NARROW_FOCUS,
            LearnerLevel.L3_ANALYSIS: ScaffoldStrategy.POINT_TO_TEXT,
            LearnerLevel.L4_EVALUATION: ScaffoldStrategy.POINT_TO_TEXT,
            LearnerLevel.L5_CREATION: ScaffoldStrategy.POINT_TO_TEXT,
        },
        StudentIntent.INSIGHT: {
            LearnerLevel.L1_RECOGNITION: ScaffoldStrategy.VALIDATE_AND_PUSH,
            LearnerLevel.L2_COMPREHENSION: ScaffoldStrategy.VALIDATE_AND_PUSH,
            LearnerLevel.L3_ANALYSIS: ScaffoldStrategy.METACOGNITIVE,
            LearnerLevel.L4_EVALUATION: ScaffoldStrategy.SYNTHESIZE,
            LearnerLevel.L5_CREATION: ScaffoldStrategy.SYNTHESIZE,
        },
        StudentIntent.REVISION_PLAN: {
            LearnerLevel.L1_RECOGNITION: ScaffoldStrategy.VALIDATE_AND_PUSH,
            LearnerLevel.L2_COMPREHENSION: ScaffoldStrategy.VALIDATE_AND_PUSH,
            LearnerLevel.L3_ANALYSIS: ScaffoldStrategy.METACOGNITIVE,
            LearnerLevel.L4_EVALUATION: ScaffoldStrategy.SYNTHESIZE,
            LearnerLevel.L5_CREATION: ScaffoldStrategy.SYNTHESIZE,
        },
        StudentIntent.OFF_TOPIC: {
            LearnerLevel.L1_RECOGNITION: ScaffoldStrategy.PROVIDE_OPTIONS,
            LearnerLevel.L2_COMPREHENSION: ScaffoldStrategy.NARROW_FOCUS,
            LearnerLevel.L3_ANALYSIS: ScaffoldStrategy.REFRAME,
            LearnerLevel.L4_EVALUATION: ScaffoldStrategy.REFRAME,
            LearnerLevel.L5_CREATION: ScaffoldStrategy.REFRAME,
        },
    }

    @staticmethod
    def select_strategy(intent: StudentIntent, level: LearnerLevel, turn: int, deflection_streak: int = 0) -> ScaffoldStrategy:
        if deflection_streak >= 3:
            return ScaffoldStrategy.PROVIDE_OPTIONS
        if turn >= 4:
            if intent in (StudentIntent.INSIGHT, StudentIntent.REVISION_PLAN):
                return ScaffoldStrategy.SYNTHESIZE
            return ScaffoldStrategy.METACOGNITIVE
        intent_strategies = ScaffoldingSystem.STRATEGY_MATRIX.get(intent)
        if intent_strategies:
            strategy = intent_strategies.get(level)
            if strategy:
                return strategy
        return ScaffoldStrategy.POINT_TO_TEXT

    @staticmethod
    def get_strategy_instruction(strategy: ScaffoldStrategy, dimension_name: str) -> str:
        instructions = {
            ScaffoldStrategy.NARROW_FOCUS:
                f"Zoom in on ONE concrete element of their essay related to {dimension_name}.",
            ScaffoldStrategy.PROVIDE_OPTIONS:
                f"Give 2-3 concrete options for improving {dimension_name}. Frame as choices.",
            ScaffoldStrategy.POINT_TO_TEXT:
                f"Point to a specific passage. Ask what they notice about {dimension_name}.",
            ScaffoldStrategy.REFRAME:
                f"Ask the same underlying question about {dimension_name} from a different angle.",
            ScaffoldStrategy.VALIDATE_AND_PUSH:
                f"Acknowledge their specific insight, then push one level deeper on {dimension_name}.",
            ScaffoldStrategy.METACOGNITIVE:
                f"Ask them to reflect on their thinking process about {dimension_name}.",
            ScaffoldStrategy.SYNTHESIZE:
                f"Help them connect insights into a concrete revision for {dimension_name}.",
        }
        return instructions.get(strategy, instructions[ScaffoldStrategy.POINT_TO_TEXT])

    @staticmethod
    def estimate_level(dialogue_history: list) -> LearnerLevel:
        if not dialogue_history:
            return LearnerLevel.L1_RECOGNITION
        insights = sum(1 for t in dialogue_history if t.get("intent") == "insight")
        revisions = sum(1 for t in dialogue_history if t.get("intent") == "revision_plan")
        substantive = sum(1 for t in dialogue_history if len(t.get("response", "").split()) > 20)
        if revisions >= 1 and insights >= 2:
            return LearnerLevel.L5_CREATION
        if insights >= 2 or revisions >= 1:
            return LearnerLevel.L4_EVALUATION
        if insights >= 1 or substantive >= 2:
            return LearnerLevel.L3_ANALYSIS
        if substantive >= 1:
            return LearnerLevel.L2_COMPREHENSION
        return LearnerLevel.L1_RECOGNITION


# ============================================================
# MEMORY MANAGER
# ============================================================

class MemoryManager:
    def __init__(self):
        self.dialogue_history: list = []
        self.insights_discovered: list = []
        self.current_level: LearnerLevel = LearnerLevel.L1_RECOGNITION
        self.focus_dimension: str = ""
        self.essay_text: str = ""
        self.original_essay: str = ""
        self.essay_versions: list = []  # Track every version
        self.assessment: MultidimensionalAssessment = None
        self.initial_assessment: MultidimensionalAssessment = None
        self.deflection_streak: int = 0
        self.previous_questions: list = []  # For dedup
        self.targeted_passages: list = []  # Quotes from essay already addressed
        self.revision_attempts_on_dimension: int = 0  # How many revisions without score change
        self.model_shown_for_dimension: bool = False  # Have we shown a model for current focus

    def add_turn(self, question: str, response: str, intent: StudentIntent,
                 scaffold: ScaffoldStrategy, level: LearnerLevel, mode: str = "ask",
                 essay_before: str = "", essay_after: str = "",
                 score_before: int = 0, score_after: int = 0):
        turn = DialogueTurn(
            turn_number=len(self.dialogue_history) + 1,
            mode=mode, question=question, student_response=response,
            intent=intent.value, scaffold_used=scaffold.value,
            learner_level=level.value,
            essay_before=essay_before, essay_after=essay_after,
            score_before=score_before, score_after=score_after,
        )
        self.dialogue_history.append(turn)
        self.current_level = level
        self.previous_questions.append(question)

        if intent in (StudentIntent.DEFLECTION, StudentIntent.OFF_TOPIC):
            self.deflection_streak += 1
        else:
            self.deflection_streak = 0

        if intent == StudentIntent.INSIGHT:
            self.insights_discovered.append({
                "turn": turn.turn_number, "text": response,
                "timestamp": turn.timestamp,
            })

    def get_context_for_prompt(self) -> str:
        if not self.dialogue_history:
            return "(This is the opening question.)"
        ctx = ""
        for t in self.dialogue_history:
            ctx += f"\nTutor [{t.mode.upper()} Turn {t.turn_number}]: {t.question}"
            ctx += f"\nStudent: {t.student_response}"
            if t.score_before and t.score_after:
                ctx += f"\n[Score: {t.score_before} -> {t.score_after}]"
            ctx += "\n"
        return ctx

    def get_history_for_export(self) -> list:
        return [asdict(t) for t in self.dialogue_history]

    def get_session_summary(self) -> dict:
        revisions = sum(1 for t in self.dialogue_history if t.mode == "revise" and t.essay_after)
        return {
            "total_turns": len(self.dialogue_history),
            "focus_dimension": self.focus_dimension,
            "level_start": self.dialogue_history[0].learner_level if self.dialogue_history else 1,
            "level_end": self.current_level.value,
            "insights_count": len(self.insights_discovered),
            "revision_count": revisions,
            "insights": self.insights_discovered,
            "intents_observed": [t.intent for t in self.dialogue_history],
            "scaffolds_used": [t.scaffold_used for t in self.dialogue_history],
        }


# ============================================================
# DIALOGUE GENERATOR (with revision prompts)
# ============================================================

class DialogueGenerator:
    FALLBACK_PROBES = {
        "context_and_purpose": [
            "Who do you imagine reading this piece? How did that shape your choices?",
            "What were you trying to accomplish with this essay?",
            "If your reader had never encountered this topic, what would they need from your opening?",
            "How might your argument land differently for someone who already disagrees?",
            "What assumptions are you making about what your reader already knows?",
        ],
        "content_development": [
            "Which of your supporting points do you feel is strongest? What makes it convincing?",
            "Where in your essay do you think the argument is thinnest?",
            "You make an interesting claim here. What evidence led you to that conclusion?",
            "If someone challenged your main argument, what would be the hardest counterpoint?",
            "How does each paragraph connect back to your central thesis?",
        ],
        "genre_and_conventions": [
            "How did you decide on the structure of your essay?",
            "What conventions of argumentative writing did you try to follow?",
            "How does your introduction set up what follows?",
            "Look at your transitions between paragraphs. Do they guide the reader or just jump?",
            "What would change about this piece if you were writing it as a letter?",
        ],
        "sources_and_evidence": [
            "How did you choose the sources you used? What made them credible to you?",
            "Where do you rely on your own reasoning versus outside evidence?",
            "If a skeptical reader asked 'says who?' after your main claim, how would your sources answer?",
            "Are there perspectives or sources you considered but chose not to include?",
            "How do your sources talk to each other? Do they agree, or are you synthesizing?",
        ],
        "syntax_and_mechanics": [
            "Read your first paragraph aloud. Where do you stumble or lose the rhythm?",
            "Which sentence in your essay are you most proud of? What makes it work?",
            "Are there places where a simpler sentence would hit harder?",
            "Look at your word choices. Where could a more precise word sharpen your meaning?",
            "If you had to cut your essay by 20%, what would go first?",
        ],
    }

    @staticmethod
    def _is_duplicate(new_q: str, previous: list, threshold: float = 0.4) -> bool:
        """Check if new question is too similar to any previous question.
        
        Uses three checks:
        1. Word overlap (40% threshold - tighter than before)
        2. Quoted phrase match (if both questions quote the same essay phrase)
        3. Exact substring (if 8+ consecutive words match)
        """
        if not previous:
            return False
        new_lower = new_q.lower()
        new_words = set(new_lower.split())
        
        # Extract any quoted phrases from new question
        import re
        new_quotes = set(re.findall(r'"([^"]+)"', new_lower))
        
        for prev in previous:
            prev_lower = prev.lower()
            prev_words = set(prev_lower.split())
            if not new_words or not prev_words:
                continue
            
            # Check 1: Word overlap
            overlap = len(new_words & prev_words) / max(len(new_words), len(prev_words))
            if overlap > threshold:
                return True
            
            # Check 2: Shared quoted phrases (if both quote the same essay text)
            prev_quotes = set(re.findall(r'"([^"]+)"', prev_lower))
            if new_quotes and prev_quotes and new_quotes & prev_quotes:
                return True
            
            # Check 3: Long substring match (8+ consecutive words)
            new_word_list = new_lower.split()
            prev_word_list = prev_lower.split()
            for i in range(len(new_word_list) - 7):
                chunk = " ".join(new_word_list[i:i+8])
                if chunk in prev_lower:
                    return True
        
        return False

    @staticmethod
    def generate_question(essay_text: str, dimension_key: str, memory: MemoryManager,
                          scaffold: ScaffoldStrategy, turn: int, api_call_fn=None) -> str:
        dim = VALUE_RUBRIC.get(dimension_key, {})
        dim_name = dim.get("name", dimension_key)
        scaffold_instruction = ScaffoldingSystem.get_strategy_instruction(scaffold, dim_name)
        context = memory.get_context_for_prompt()

        prev_qs = "\n".join(f"- {q}" for q in memory.previous_questions) if memory.previous_questions else "(none)"
        
        targeted = ""
        if memory.targeted_passages:
            targeted = "\n\nESSAY PASSAGES ALREADY ADDRESSED (do NOT target these again):\n"
            targeted += "\n".join(f"- \"{p}\"" for p in memory.targeted_passages)

        system_prompt = f"""You are a Socratic writing tutor. NEVER give direct answers or corrections.

Focus dimension: {dim_name}
Description: {dim.get('description', '')}

Scaffolding strategy: {scaffold.value}
Instruction: {scaffold_instruction}

CRITICAL RULES:
1. Ask ONE question at a time (1-3 sentences)
2. Build on the student MOST RECENT response specifically
3. NEVER repeat or closely rephrase any previous question. ALL previous questions:
{prev_qs}
4. Target a DIFFERENT sentence or section of the essay than any previous question
5. If the student has deflected 3+ times, name the pattern directly and offer A/B/C options
6. Be warm but intellectually honest
7. Your goal: guide them to identify ONE specific thing to change in their essay
8. Quote a SHORT phrase from the essay (in double quotes) to anchor your question
{targeted}

This is turn {turn + 1}."""

        user_msg = f"Student essay:\n---\n{essay_text}\n---\n\nDialogue so far:\n{context}\n\nGenerate a NEW Socratic question targeting a DIFFERENT part of the essay than before."

        if api_call_fn:
            # Try up to 5 times to get a non-duplicate question
            result = None
            for attempt in range(5):
                if attempt > 0:
                    user_msg = f"Student essay:\n---\n{essay_text}\n---\n\nDialogue so far:\n{context}\n\nATTEMPT {attempt + 1}: Your previous question was too similar to one already asked. You MUST target a COMPLETELY DIFFERENT sentence in the essay. Do NOT reference any of these passages: {'; '.join(memory.targeted_passages) if memory.targeted_passages else 'none yet'}."
                result = api_call_fn(system_prompt, user_msg)
                if result:
                    result = result.strip()
                    if not DialogueGenerator._is_duplicate(result, memory.previous_questions):
                        # Extract and track any quoted passages from the new question
                        import re
                        quotes = re.findall(r'"([^"]{10,})"', result)
                        memory.targeted_passages.extend(quotes)
                        return result
            # After 5 tries, return whatever we got
            if result:
                return result.strip()

        probes = DialogueGenerator.FALLBACK_PROBES.get(dimension_key, [])
        # Find first unused probe
        for probe in probes:
            if not DialogueGenerator._is_duplicate(probe, memory.previous_questions, 0.5):
                return probe
        return "What's one specific change you'd make to strengthen this part of your essay?"

    @staticmethod
    def generate_revision_prompt(essay_text: str, dimension_key: str, student_response: str,
                                 memory: MemoryManager, api_call_fn=None) -> str:
        """After student responds to a question, invite them to revise."""
        dim = VALUE_RUBRIC.get(dimension_key, {})
        dim_name = dim.get("name", dimension_key)
        context = memory.get_context_for_prompt()

        system_prompt = f"""You are a writing coach helping a student move from thinking to doing.

The student just answered a Socratic question about {dim_name} and said something worth building on.
Now you need to:
1. Echo back the useful part of what they said (quote a phrase from their response, not the essay)
2. Point at the SPECIFIC sentence or section in their essay where that insight applies - quote it
3. Invite them to revise that part right now

Your tone: collaborative. Use "let's" framing. You are doing this together.
Keep it to 2-4 sentences total.
End with something like "Go ahead and edit below - let's see what that section looks like with this idea in it."

EXAMPLE: "You just said the evidence 'only proves it works in controlled settings' - exactly right. Look at where you wrote 'this demonstrates AI tutoring works in real classrooms.' Let's revise that sentence so it matches what the evidence actually supports."

IMPORTANT: Do NOT rewrite their essay for them. Do NOT give them the answer.
Just connect their insight to the specific spot in the essay."""

        user_msg = f"Student essay:\n---\n{essay_text}\n---\n\nDialogue:\n{context}\n\nStudent latest response: {student_response}\n\nGenerate the revision invitation."

        if api_call_fn:
            result = api_call_fn(system_prompt, user_msg)
            if result:
                return result.strip()

        return f"That's a useful observation. Take a look at your essay below and try revising the part that relates to {dim_name}. Focus on the specific change you just described."

    @staticmethod
    def generate_model(essay_text: str, dimension_key: str, memory: MemoryManager,
                       api_call_fn=None) -> str:
        """Show the student a before/after example using ONE of their own sentences.
        
        This kicks in when the student understands the concept (shown through dialogue)
        but can't execute the revision. The model gives them a pattern to follow,
        not the answer for the whole essay.
        """
        dim = VALUE_RUBRIC.get(dimension_key, {})
        dim_name = dim.get("name", dimension_key)
        context = memory.get_context_for_prompt()

        system_prompt = f"""You are a writing coach. The student has been working on {dim_name} and understands what needs to change but is having trouble executing it. They have already tried revising and the score did not move.

Your job: SHOW them what the change looks like on ONE sentence from their essay.

FORMAT YOUR RESPONSE EXACTLY LIKE THIS:

1. Start with a brief, friendly acknowledgment (1 sentence). Use plain language — no jargon like "rhetorical mapping" or "genre conventions." Talk like a person.

2. Then show a before/after:

YOUR VERSION: "[copy one specific sentence from their essay that could improve]"

ONE WAY TO REVISE IT: "[show a revised version of that same sentence]"

3. Then explain the PATTERN in 1-2 plain sentences. Not "this demonstrates genre awareness" — instead something like "See the difference? The first one tells me what the passage says. The second one shows me what the author is DOING — like, what their strategy is."

4. End with: "Now try applying that same move to [one or two other specific spots in your essay]. I will not do those for you — I want to see YOUR version."

CRITICAL RULES:
- Only revise ONE sentence. Not two, not a paragraph. One.
- The revised version should be genuinely better, not just reworded.
- Explain the pattern in everyday language. Imagine you are talking to a smart friend, not a professor.
- The goal is to give them a TARGET to aim for, not do the work for them.
- Reference the specific skill in plain terms: instead of "genre conventions" say something like "showing what the author is doing, not just what the passage says" or "connecting your points so each one builds on the last" or "using specific details instead of general claims"
- NEVER use academic jargon: no "rhetorical," "discourse," "genre conventions," "disciplinary," "analytical framework"
- Keep the whole thing under 150 words."""

        user_msg = f"Student essay:\n---\n{essay_text}\n---\n\nDialogue so far (shows the student understands the concept):\n{context}\n\nDimension we are working on: {dim_name}\n\nPick ONE sentence from their essay, show a better version, explain the pattern in plain language."

        if api_call_fn:
            result = api_call_fn(system_prompt, user_msg)
            if result:
                return result.strip()

        # Fallback
        return f"Let me show you what I mean. Look at your first body paragraph opening. Instead of telling me what the passage says, try showing me what the author is DOING with that information. Like, what is their game plan? Try rewriting that opening sentence with that idea in mind, and then do the same thing for your other paragraphs."

    @staticmethod
    def generate_revision_feedback(old_essay: str, new_essay: str, dimension_key: str,
                                   old_score: int, new_score: int, memory: MemoryManager,
                                   api_call_fn=None, all_old_scores: dict = None,
                                   all_new_scores: dict = None) -> str:
        """After student revises, frame the re-score results warmly and set up next steps."""
        dim = VALUE_RUBRIC.get(dimension_key, {})
        dim_name = dim.get("name", dimension_key)

        # Build a score change summary for the AI to reference
        score_changes = ""
        if all_old_scores and all_new_scores:
            changes = []
            for key in all_old_scores:
                old_s = all_old_scores.get(key, 0)
                new_s = all_new_scores.get(key, 0)
                name = VALUE_RUBRIC.get(key, {}).get("name", key)
                if new_s > old_s:
                    changes.append(f"  {name}: {old_s} -> {new_s} (improved)")
                elif new_s < old_s:
                    changes.append(f"  {name}: {old_s} -> {new_s} (dipped)")
                else:
                    changes.append(f"  {name}: held at {old_s}")
            score_changes = "\nFull re-score results:\n" + "\n".join(changes)

        if new_score > old_score:
            scenario = "IMPROVED"
            tone_guidance = """The score went up. This is a real win. Your job:
1. CELEBRATE specifically - quote the exact edit that made the difference
2. Explain WHY it worked (not just that it did) - "adding that specific poll number made your claim verifiable instead of vague"
3. Frame the re-score positively: "I just re-scored your whole essay and [dimension] moved up"
4. If other dimensions also improved, mention that: "and your revision actually helped [other dim] too"
5. Keep momentum: "let's keep going" or "let's see what we can do with the next area"
"""
        elif new_score == old_score:
            scenario = "HELD_STEADY"
            tone_guidance = f"""The score held at {old_score}/4. The student just did real work. Honor that. Your job:
1. VALIDATE the effort and the thinking behind their edit - quote what they changed
2. Explain the gap without blame: "The idea you added is on the right track. What would push the score is [specific thing]"
3. Frame it honestly but warmly: "I re-scored your essay and {dim_name} is still at {old_score}/4 - that does not mean the revision was wasted. Sometimes it takes more than one pass to move the needle."
4. Give them a concrete next target: "Let's try [specific thing] in the next revision"
5. NEVER say "unfortunately" or "however" right after acknowledging their work. That pattern erases the validation.
"""
        else:
            scenario = "DIPPED"
            tone_guidance = f"""The score dipped from {old_score} to {new_score}. This is delicate. Your job:
1. DO NOT ALARM. This happens. Revision is messy.
2. Name what they were trying to do (charitably): "I can see you were trying to [their intention]"
3. Frame the dip gently: "The re-score came back slightly lower on {dim_name} - that can happen when you are rearranging ideas. It is not a step backward, it just means we need to fine-tune."
4. Identify what specifically shifted: quote the part that may have caused it
5. Redirect with energy: "Here is the good news - we know exactly what to look at. Let's fix [specific thing]."
6. NEVER make the student feel they broke something. Revising is brave.
"""

        system_prompt = f"""You are a writing coach giving a student feedback after they revised their essay. Their essay was just re-scored across all five dimensions.

Focus dimension: {dim_name}
Score before revision: {old_score}/4
Score after revision: {new_score}/4
Scenario: {scenario}
{score_changes}

{tone_guidance}

CRITICAL TONE RULES:
- Always acknowledge that a re-score happened. The student should know their work was evaluated fresh.
- QUOTE at least one specific phrase from their revised essay to prove you read it.
- Use "let's" framing - you are in this together.
- Keep it to 3-5 sentences. Enough to land, not so much it feels like a lecture.
- End looking forward, not backward."""

        user_msg = f"Essay BEFORE revision:\n---\n{old_essay}\n---\n\nEssay AFTER revision:\n---\n{new_essay}\n---\n\nGenerate warm, specific feedback about the re-score results."

        if api_call_fn:
            result = api_call_fn(system_prompt, user_msg)
            if result:
                return result.strip()

        # Fallback responses with re-score framing
        if new_score > old_score:
            return f"I just re-scored your essay and {dim_name} moved from {old_score} to {new_score} - your revision made a real difference. The changes you made tightened up exactly what needed tightening. Let's keep that momentum going."
        elif new_score == old_score:
            return f"I re-scored your essay after that revision, and {dim_name} is still at {old_score}/4. That does not mean the work was wasted - sometimes it takes more than one pass to move the number. I can see the thinking behind your edits, and we are getting closer. Let's try one more specific push."
        else:
            return f"I re-scored your essay and {dim_name} shifted slightly from {old_score} to {new_score}. That can happen when you are reworking things - revising is not always a straight line forward. The important thing is we can see exactly what to adjust. Let's take another look."


# ============================================================
# TUTOR ENGINE v0.3 (with revision loop)
# ============================================================

class TutorEngine:
    def __init__(self, api_call_fn=None):
        self.memory = MemoryManager()
        self.api_call_fn = api_call_fn
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.current_mode = DialogueMode.ASK

    def assess_essay(self, essay_text: str, prompt_text: str,
                     scoring_anchors=None, creative_policy=None,
                     edge_case_framework=None, passage_text=None) -> MultidimensionalAssessment:
        self.memory.essay_text = essay_text
        self.memory.original_essay = essay_text
        self.memory.essay_versions.append(essay_text)
        self._prompt_text = prompt_text
        self._scoring_anchors = scoring_anchors
        self._creative_policy = creative_policy
        self._edge_case_framework = edge_case_framework
        self._passage_text = passage_text
        assessment = AnswerEvaluator.assess(
            essay_text, prompt_text, self.api_call_fn,
            scoring_anchors=scoring_anchors,
            creative_policy=creative_policy,
            edge_case_framework=edge_case_framework,
            passage_text=passage_text,
        )
        self.memory.assessment = assessment
        self.memory.initial_assessment = assessment
        self.memory.focus_dimension = assessment.weakest_dimension
        return assessment

    def generate_opening_question(self) -> str:
        self.current_mode = DialogueMode.ASK
        scaffold = ScaffoldStrategy.POINT_TO_TEXT
        return DialogueGenerator.generate_question(
            self.memory.essay_text, self.memory.focus_dimension,
            self.memory, scaffold, 0, self.api_call_fn,
        )

    def process_response(self, student_response: str, current_question: str) -> dict:
        """SOAR cycle - returns revision_prompt when appropriate."""
        turn = len(self.memory.dialogue_history)
        # Count only ASK turns (not revision turns) for pacing
        ask_turns = sum(1 for t in self.memory.dialogue_history if t.mode == "ask")

        # Classify
        if self.api_call_fn:
            intent = IntentClassifier.classify_with_ai(student_response, current_question, self.api_call_fn)
        else:
            intent = IntentClassifier.classify(student_response)

        # Estimate level
        temp_history = self.memory.get_history_for_export()
        temp_history.append({"intent": intent.value, "response": student_response})
        level = ScaffoldingSystem.estimate_level(temp_history)

        # Select scaffold
        scaffold = ScaffoldingSystem.select_strategy(
            intent, level, ask_turns, self.memory.deflection_streak
        )

        # Record turn
        self.memory.add_turn(current_question, student_response, intent, scaffold, level, mode="ask")

        # REVISION CHECK FIRST - substantive response triggers revision
        should_revise = intent in (
            StudentIntent.DIRECT_ANSWER, StudentIntent.INSIGHT,
            StudentIntent.REVISION_PLAN,
        ) and len(student_response.split()) > 8

        if should_revise:
            revision_prompt = DialogueGenerator.generate_revision_prompt(
                self.memory.essay_text, self.memory.focus_dimension,
                student_response, self.memory, self.api_call_fn,
            )
            self.current_mode = DialogueMode.REVISE
            return {
                "intent": intent, "level": level, "scaffold": scaffold,
                "next_question": "", "revision_prompt": revision_prompt,
                "should_end": False, "should_revise": True, "turn": turn + 1,
            }

        # END CHECK — only if all dimensions met target or hard turn limit
        dims_below = 0
        if self.memory.assessment:
            dims_below = sum(1 for s in self.memory.assessment.scores if s.score < 3)
        should_end = (ask_turns >= 15) or (dims_below == 0 and ask_turns >= 2)

        if should_end:
            return {
                "intent": intent, "level": level, "scaffold": scaffold,
                "next_question": "", "revision_prompt": "",
                "should_end": True, "should_revise": False, "turn": turn + 1,
            }

        # Deflection/off-topic - ask another question
        next_q = DialogueGenerator.generate_question(
            self.memory.essay_text, self.memory.focus_dimension,
            self.memory, scaffold, turn + 1, self.api_call_fn,
        )
        return {
            "intent": intent, "level": level, "scaffold": scaffold,
            "next_question": next_q, "revision_prompt": "",
            "should_end": False, "should_revise": False, "turn": turn + 1,
        }

    def process_revision(self, new_essay: str, prompt_text: str) -> dict:
        """Student submitted a revised essay. Full re-score, advance dimensions, cycle until done."""
        old_essay = self.memory.essay_text
        old_dim_key = self.memory.focus_dimension

        # Get old score for current focus dimension
        old_focus_score = 0
        old_scores_snapshot = {}
        if self.memory.assessment:
            for s in self.memory.assessment.scores:
                old_scores_snapshot[s.dimension] = s.score
                if s.dimension == old_dim_key:
                    old_focus_score = s.score

        # Update essay
        self.memory.essay_text = new_essay
        self.memory.essay_versions.append(new_essay)

        # FULL RE-SCORE — revisions ripple across dimensions
        new_assessment = AnswerEvaluator.assess(
            new_essay, prompt_text, self.api_call_fn,
            scoring_anchors=getattr(self, '_scoring_anchors', None),
            creative_policy=getattr(self, '_creative_policy', None),
            edge_case_framework=getattr(self, '_edge_case_framework', None),
            passage_text=getattr(self, '_passage_text', None),
        )

        # Preserve initial assessment, update current
        self.memory.assessment = new_assessment

        # Get new focus dimension score
        new_focus_score = old_focus_score
        for s in new_assessment.scores:
            if s.dimension == old_dim_key:
                new_focus_score = s.score
                break

        # Build new scores snapshot
        new_scores_snapshot = {s.dimension: s.score for s in new_assessment.scores}

        # Generate feedback about the re-score with full context
        feedback = DialogueGenerator.generate_revision_feedback(
            old_essay, new_essay, old_dim_key, old_focus_score, new_focus_score,
            self.memory, self.api_call_fn,
            all_old_scores=old_scores_snapshot,
            all_new_scores=new_scores_snapshot,
        )

        # Record revision turn
        turn = len(self.memory.dialogue_history)
        self.memory.add_turn(
            question=f"[REVISION] {feedback}",
            response=f"[Student revised essay - {old_dim_key} score: {old_focus_score}->{new_focus_score}]",
            intent=StudentIntent.REVISION_PLAN,
            scaffold=ScaffoldStrategy.VALIDATE_AND_PUSH,
            level=self.memory.current_level,
            mode="revise",
            essay_before=old_essay, essay_after=new_essay,
            score_before=old_focus_score, score_after=new_focus_score,
        )

        # DIMENSION ADVANCEMENT — find next dimension to work on
        target_score = 3  # Minimum acceptable score
        
        # Check which dimensions still need work
        dims_below_target = []
        all_met = True
        for s in new_assessment.scores:
            if s.score < target_score:
                dims_below_target.append((s.dimension, s.score))
                all_met = False
        
        # Sort by score (lowest first), then by original order for ties
        dims_below_target.sort(key=lambda x: x[1])
        
        # Did the current dimension hit target?
        current_hit_target = new_focus_score >= target_score
        dimension_changed = False
        trigger_model = False
        
        if current_hit_target and dims_below_target:
            # Current dimension is good — move to next weakest
            new_dim = dims_below_target[0][0]
            self.memory.focus_dimension = new_dim
            # Clear targeted passages and stuck tracking — fresh start
            self.memory.targeted_passages = []
            self.memory.revision_attempts_on_dimension = 0
            self.memory.model_shown_for_dimension = False
            dimension_changed = True
            # Update weakest in assessment
            new_assessment.weakest_dimension = new_dim
            new_assessment.weakest_score = dims_below_target[0][1]
        elif current_hit_target and not dims_below_target:
            # All dimensions met — will end session
            pass
        else:
            # Still working on current dimension — track stuck state
            if new_focus_score <= old_focus_score:
                self.memory.revision_attempts_on_dimension += 1
                # Trigger MODEL if: revised at least once without improvement AND
                # haven't shown a model for this dimension yet
                if (self.memory.revision_attempts_on_dimension >= 1 and 
                    not self.memory.model_shown_for_dimension):
                    trigger_model = True
                    self.memory.model_shown_for_dimension = True
            else:
                # Score improved but not to target — reset stuck counter
                self.memory.revision_attempts_on_dimension = 0
        
        # Decide if session should end
        max_turns = 12  # generous but not infinite
        should_end = all_met or turn >= max_turns
        
        # Build dimension change message if needed
        dim_change_msg = ""
        if dimension_changed:
            new_dim_name = VALUE_RUBRIC.get(self.memory.focus_dimension, {}).get("name", self.memory.focus_dimension)
            new_dim_score = 0
            for s in new_assessment.scores:
                if s.dimension == self.memory.focus_dimension:
                    new_dim_score = s.score
                    break
            dim_change_msg = f"\n\n{VALUE_RUBRIC.get(old_dim_key, {}).get('name', old_dim_key)} is in solid shape now. Let us shift our focus to **{new_dim_name}** ({new_dim_score}/4) - that is where the next opportunity is."
        elif all_met:
            dim_change_msg = "\n\nAll five dimensions are at 3 or above now. That is a genuinely stronger piece of writing than what you started with."

        # Determine next mode: MODEL if stuck, otherwise ASK
        next_q = ""
        model_text = ""
        if trigger_model and not should_end:
            self.current_mode = DialogueMode.MODEL
            model_text = DialogueGenerator.generate_model(
                new_essay, self.memory.focus_dimension, self.memory, self.api_call_fn,
            )
            # Record the model turn
            self.memory.add_turn(
                question=f"[MODEL] {model_text}",
                response="[System showed before/after example]",
                intent=StudentIntent.DIRECT_ANSWER,
                scaffold=ScaffoldStrategy.VALIDATE_AND_PUSH,
                level=self.memory.current_level,
                mode="model",
            )
        elif not should_end:
            self.current_mode = DialogueMode.ASK
            scaffold = ScaffoldStrategy.VALIDATE_AND_PUSH if new_focus_score > old_focus_score else ScaffoldStrategy.POINT_TO_TEXT
            next_q = DialogueGenerator.generate_question(
                new_essay, self.memory.focus_dimension, self.memory, scaffold, turn + 1, self.api_call_fn,
            )
        else:
            self.current_mode = DialogueMode.ASK

        return {
            "feedback": feedback + dim_change_msg,
            "old_score": old_focus_score, "new_score": new_focus_score,
            "next_question": next_q,
            "model_text": model_text,
            "trigger_model": trigger_model,
            "should_end": should_end,
            "dimension_changed": dimension_changed,
            "all_scores": {s.dimension: s.score for s in new_assessment.scores},
            "dims_remaining": len(dims_below_target),
        }

    def export_session(self, reflection: str = "") -> SessionData:
        summary = self.memory.get_session_summary()
        initial = self.memory.initial_assessment.to_dict() if self.memory.initial_assessment else {}
        final = self.memory.assessment.to_dict() if self.memory.assessment else {}
        init_avg = self.memory.initial_assessment.overall_average if self.memory.initial_assessment else 0
        final_avg = self.memory.assessment.overall_average if self.memory.assessment else 0

        return SessionData(
            session_id=self.session_id,
            original_essay=self.memory.original_essay,
            final_essay=self.memory.essay_text,
            prompt_title="Argumentative Essay: Technology and Learning",
            rubric_name="AAC&U VALUE Written Communication",
            initial_assessment=initial, final_assessment=final,
            dialogue_turns=self.memory.get_history_for_export(),
            revision_count=summary.get("revision_count", 0),
            score_delta=round(final_avg - init_avg, 2),
            reflection=reflection,
            learner_level_start=summary.get("level_start", 1),
            learner_level_end=summary.get("level_end", 1),
            completed_at=datetime.now().isoformat(),
        )
