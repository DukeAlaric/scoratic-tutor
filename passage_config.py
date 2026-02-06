"""
Passage Configuration for Socratic Writing Tutor v0.7
"""

PASSAGE_TITLE = "The Pineapple Pizza Debate"

PASSAGE_TEXT = """
The debate over whether pineapple belongs on pizza has divided food lovers for
decades. Hawaiian pizza, topped with pineapple and ham, was actually invented in
1962 by Sam Panopoulos, a Greek-Canadian restaurant owner in Ontario, Canada.
Despite its name, the pizza has no connection to Hawaii.

Supporters of pineapple on pizza argue that the sweet and savory combination
creates a unique flavor profile. The acidity of the pineapple can cut through
the richness of the cheese and meat, creating a balanced bite. Many chefs point
out that sweet-savory pairings are common in cuisines worldwide, from Chinese
sweet and sour dishes to Moroccan tagines with dried fruits.

Critics, however, argue that the moisture from pineapple makes the pizza soggy
and that fruit has no place on a savory dish. Italian pizza purists are
especially vocal, with some chefs calling it an offense to traditional pizza-
making. In 2017, the President of Iceland even jokingly said he would ban
pineapple pizza if he could.

The debate raises interesting questions about food traditions and cultural
boundaries. Who gets to decide what counts as authentic food? Since pizza
itself evolved from simple flatbreads and has been adapted by nearly every
culture, some argue that gatekeeping toppings contradicts pizza's own history
of evolution and adaptation.

Recent surveys suggest that pineapple pizza remains popular despite the
controversy. A 2019 YouGov poll found that about 12 percent of Americans
preferred Hawaiian pizza, making it one of the more popular specialty styles.
Whether you love it or hate it, the pineapple pizza debate shows how something
as simple as a topping can spark passionate disagreement about taste, tradition,
and cultural identity.
""".strip()

WRITING_PROMPT = """After reading "The Pineapple Pizza Debate," write a response
that takes a clear position on ONE of the following questions:

1. Should people follow traditional food rules, or is experimenting with food
   always acceptable?
2. Who gets to decide what counts as authentic food?
3. Why do people have such strong opinions about something as simple as pizza
   toppings?

Your response should:
- State a clear position
- Use at least ONE specific detail from the passage to support your argument
- Explain your reasoning
""".strip()

VALUE_RUBRIC = {
    "claim_clarity": {
        "name": "Claim Clarity",
        "description": "How clear and specific is the main argument?",
        "anchors": {
            1: "No clear position.",
            2: "Position is implied but vague.",
            3: "Clear position stated.",
            4: "Precise position that frames entire response."
        }
    },
    "evidence_use": {
        "name": "Evidence Use",
        "description": "How well does the response use details from the passage?",
        "anchors": {
            1: "No reference to passage.",
            2: "Vague reference without specifics.",
            3: "One specific detail used and connected.",
            4: "Multiple details woven into argument."
        }
    },
    "reasoning_depth": {
        "name": "Reasoning Depth",
        "description": "How well does the writer explain WHY?",
        "anchors": {
            1: "No explanation.",
            2: "Shallow - restates without explaining.",
            3: "Explains connection with analysis.",
            4: "Deep analysis of implications."
        }
    },
    "organization": {
        "name": "Organization",
        "description": "How logically structured is the response?",
        "anchors": {
            1: "No structure.",
            2: "Some structure but jumpy.",
            3: "Logical flow with transitions.",
            4: "Strong progression throughout."
        }
    },
    "voice_engagement": {
        "name": "Voice & Engagement",
        "description": "Does it sound like a real person?",
        "anchors": {
            1: "Flat or robotic.",
            2: "Generic.",
            3: "Some personality.",
            4: "Distinctive voice throughout."
        }
    }
}

DIMENSION_ORDER = ["claim_clarity", "evidence_use", "reasoning_depth", "organization", "voice_engagement"]
TARGET_SCORE = 3

EDGE_CASE_RULES = """Handle edge cases: off-topic but thoughtful gets gentle redirect,
very short gets encouragement, jokes get acknowledged then redirected, copy-paste
gets scored low on evidence, creative connections get rewarded."""

SCORING_SYSTEM_PROMPT = """You are a writing assessment engine. Score student
responses against VALUE rubric. Return ONLY valid JSON.

RUBRIC:
{rubric_text}

RULES: Score 1-4 honestly. 3 = met standard. 4 = exceptional. Brief rationale each.

RETURN FORMAT:
{{"claim_clarity": {{"score": <int>, "rationale": "<string>"}}, "evidence_use": {{"score": <int>, "rationale": "<string>"}}, "reasoning_depth": {{"score": <int>, "rationale": "<string>"}}, "organization": {{"score": <int>, "rationale": "<string>"}}, "voice_engagement": {{"score": <int>, "rationale": "<string>"}}}}
"""

COACHING_SYSTEM_PROMPT = """You are a Socratic writing coach. Ask questions, don't tell.

DIMENSION: {dimension_name}
SCORE: {current_score}/4, TARGET: {target_score}/4
RATIONALE: {rationale}

ESSAY:
{essay}

PASSAGE:
{passage}

Ask ONE focused question. 2-4 sentences max. Reference their essay specifically."""

MODEL_EXAMPLE_PROMPT = """Student's {dimension_name} score didn't improve.
Show a SHORT before/after example on a DIFFERENT topic. Explain what changed.
Ask them to try similar. Under 150 words. Don't rewrite their essay."""

REFLECTION_PROMPTS = [
    {"question": "What was the hardest part of this session for you?",
     "followup_system": """The student just told you what was hardest. Respond in 2-3 sentences:
1. Acknowledge their specific struggle (reference what they said)
2. Normalize it - explain why that's a common challenge for writers
3. Share ONE brief tip related to their struggle

Then ask exactly this: 'What is one thing you noticed about your writing that you did not see before?'

Do NOT ask multiple questions. Keep total response under 75 words."""},
    
    {"question": "What is one thing you noticed about your writing that you didn't see before?",
     "followup_system": """The student shared an observation about their writing. Respond in 2-3 sentences:
1. Validate their insight if it's real (or gently redirect if vague)
2. Explain WHY that insight matters - connect it to a principle they can use again
3. Make it actionable

Then ask exactly this: 'If you were starting a brand new essay right now, what would you do differently?'

Do NOT ask multiple questions. Keep total response under 75 words."""},
    
    {"question": "If you were starting a brand new essay right now, what would you do differently?",
     "followup_system": """The student described what they'd do differently. This is the FINAL reflection turn. Respond in 3-4 sentences:
1. Affirm their plan specifically (reference what they said)
2. Connect it to something concrete from the session - a score change, a revision, or a coaching question that helped
3. Frame it as a skill they now OWN: 'You now know how to...'
4. End with genuine encouragement and congratulations

Do NOT ask any questions. This is the closing. Keep total response under 100 words."""}
]
RESCORE_FRAMING = "Great work on that revision. Let me look at your updated response..."

def get_rubric_text():
    lines = []
    for key, dim in VALUE_RUBRIC.items():
        lines.append(f"{dim['name']}: {dim['description']}")
        for score, anchor in dim['anchors'].items():
            lines.append(f"  {score}: {anchor}")
    return "\n".join(lines)
