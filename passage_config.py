"""
Passage Configuration for Socratic Writing Tutor v1.2

CHANGES FROM v1.1:
- Added varied coaching openers (avoids repetitive "I can see you feel strongly...")
- Added Quote Sandwich requirement for Evidence Use coaching
- Micro-celebrations for partial progress
- Conditional planning (roadmap only when Organization <= 2)
- Journey-aware celebration messages
- 4th reflection turn for transfer question
"""

import random

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
- Use academic language appropriate for a school essay

Tip: Don't overthink it - write your honest first draft. We'll work on improving it together.
""".strip()

ROADMAP_PROMPT = "Before you revise, take a moment to plan. What are the 2-3 main ideas you want your essay to cover?"

VALUE_RUBRIC = {
    "claim_clarity": {
        "name": "Claim Clarity",
        "description": "How clear and specific is the main argument?",
        "anchors": {
            1: "No clear position or buried in tangents/rhetoric.",
            2: "Position implied but vague or too casual.",
            3: "Clear position stated in academic language.",
            4: "Precise thesis with academic authority."
        }
    },
    "evidence_use": {
        "name": "Evidence Use", 
        "description": "How well does the response use details from the passage?",
        "anchors": {
            1: "No reference to passage.",
            2: "Mentions facts but doesn't integrate (data dump).",
            3: "Specific detail with signal phrase and explanation.",
            4: "Multiple details woven with clear analysis."
        }
    },
    "reasoning_depth": {
        "name": "Reasoning Depth",
        "description": "How well does the writer explain WHY?",
        "anchors": {
            1: "No explanation, only assertions.",
            2: "Shallow - restates without explaining significance.",
            3: "Explains connection with academic language.",
            4: "Deep analysis with counterarguments."
        }
    },
    "organization": {
        "name": "Organization",
        "description": "How logically structured is the response?",
        "anchors": {
            1: "No structure - stream of consciousness.",
            2: "Some structure but jumpy.",
            3: "Logical flow with transitions.",
            4: "Strong thesis-evidence-analysis progression."
        }
    },
    "voice_engagement": {
        "name": "Voice & Engagement",
        "description": "Does it sound authentic and appropriately academic?",
        "anchors": {
            1: "Flat, robotic, or speech-like rant.",
            2: "Too casual (slang, texting, performative).",
            3: "Engaged while maintaining academic tone.",
            4: "Distinctive scholarly voice."
        }
    }
}

DIMENSION_ORDER = ["claim_clarity", "evidence_use", "reasoning_depth", "organization", "voice_engagement"]
TARGET_SCORE = 3

EDGE_CASE_RULES = """Handle edge cases:
- Off-topic: gentle redirect to passage
- Very short: encourage expansion
- Jokes/sarcasm: acknowledge energy, redirect
- Word salad: identify buried claim, ask for clarity
- Pseudo-academic jargon: call out obscuring complexity
- Hostile/resistant: reframe as passion, stay supportive"""

COACHING_OPENERS = [
    "Your evidence is stronger now.",
    "You've integrated the data - nice.",
    "The facts are there.",
    "Good move with that quote.",
    "I see what you're going for.",
    "You're making progress.",
    "That revision shows effort.",
]

COACHING_OPENERS_FIRST = [
    "I can see you have ideas about this.",
    "You've taken a position - that's the start.",
    "There's a foundation here.",
    "You've got something to work with.",
]

MICRO_CELEBRATIONS = [
    "Your {dim} jumped from {old} to {new} - nice work!",
    "{dim} improved ({old} to {new}).",
    "Good progress on {dim} ({old} to {new}).",
]

QUOTE_SANDWICH_PROMPT = """Your evidence needs integration, not just dropping in.

Try the "Quote Sandwich":
1. Introduce the evidence
2. Quote the specific detail  
3. Explain why it matters

Example:
- Introduce: "The passage provides historical context."
- Quote: "Hawaiian pizza was invented in 1962 by Sam Panopoulos."
- Explain: "This shows food traditions are recent inventions themselves."

Your task: Take one fact and build a Quote Sandwich around it."""

SCORING_SYSTEM_PROMPT = """You are a writing assessment engine. Score against VALUE rubric. Return ONLY valid JSON.

RUBRIC:
{rubric_text}

RULES:
- Score 1-4 honestly. 3 = standard. 4 = exceptional.
- Casual/slang/texting = max 2 on Voice
- Speech-like rhetoric = max 2 on Voice  
- Pseudo-academic word salad = lower Claim Clarity and Reasoning
- Evidence mentioned but not explained = 2 on Evidence Use

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

RULES:
1. Ask ONE focused question
2. Reference their essay specifically
3. Keep to 2-4 sentences
4. Do NOT rewrite or give answers

BY DIMENSION:
- Claim Clarity low: Ask for one clear sentence stating position
- Evidence Use low: Ask for Quote Sandwich (introduce, quote, explain)
- Reasoning Depth low: Ask "Why does that evidence matter?"
- Organization low: Ask them to lead with strongest point
- Voice low (casual): Offer ONE academic sentence starter
- Voice low (speech-like): Ask how they'd write for a teacher

INTENT QUESTIONS (use occasionally):
- "Why did you put [X] at the end instead of beginning?"
- "What were you trying to accomplish with [phrase]?"
"""

MODEL_EXAMPLE_PROMPT = """Student's {dimension_name} score didn't improve.
Show SHORT before/after on DIFFERENT topic (social media, not pizza).
Explain what changed. Ask them to try similar. Under 100 words.

FORMAT:
**Quick Academic Register Example**
Before (Casual): "[casual]"
After (Academic): "[academic]"

**What Changed:**
- [change 1]
- [change 2]

**Your Turn:** [task]
"""

REFLECTION_PROMPTS = [
    {
        "question": "What was the hardest part of this session for you?",
        "followup": """Respond in 2-3 sentences:
1. Acknowledge what THEY said was hard
2. Normalize it: "That's common because..."
3. End with EXACTLY: "What is one thing you noticed about your writing that you didn't see before?"
No bullets. Under 75 words."""
    },
    {
        "question": "What is one thing you noticed about your writing that you didn't see before?",
        "followup": """Respond in 2-3 sentences:
1. Validate their insight
2. Explain why it matters for future writing
3. End with EXACTLY: "If you were starting a brand new essay right now, what would you do differently?"
No bullets. Under 75 words."""
    },
    {
        "question": "If you were starting a brand new essay right now, what would you do differently?",
        "followup": """Respond in 2-3 sentences:
1. Affirm their plan specifically
2. Connect to transferable skill
3. End with EXACTLY: "Where else in school or life could you use this strategy?"
No bullets. Under 75 words."""
    },
    {
        "question": "Where else in school or life could you use this strategy?",
        "followup": """Final closing. Respond in 3-4 sentences:
1. Affirm their transfer examples
2. Frame what they now OWN: "You now know how to..."
3. Congratulate warmly
NO questions. This is the end. Under 100 words."""
    }
]

RESCORE_FRAMING = "Let me look at your updated response..."

def get_rubric_text():
    lines = []
    for key, dim in VALUE_RUBRIC.items():
        lines.append(f"{dim['name']}: {dim['description']}")
        for score, anchor in dim['anchors'].items():
            lines.append(f"  {score}: {anchor}")
    return "\n".join(lines)

def get_coaching_opener(is_first=False):
    import random
    if is_first:
        return random.choice(COACHING_OPENERS_FIRST)
    return random.choice(COACHING_OPENERS)

def get_micro_celebration(dim_name, old, new):
    import random
    template = random.choice(MICRO_CELEBRATIONS)
    return template.format(dim=dim_name, old=old, new=new)

def get_celebration_opener(revisions):
    if revisions == 0:
        return "You hit all the targets on your first try.\n\nThat doesn't happen often. Here's what worked:"
    elif revisions <= 2:
        return f"You got there in just {revisions} revision{'s' if revisions > 1 else ''}.\n\nWhat changed:"
    elif revisions <= 5:
        return f"{revisions} revisions later, your essay meets the standard.\n\nWhat changed:"
    else:
        return f"It took {revisions} rounds of revision, and you pushed through.\n\nThat took persistence - here's what finally clicked:"
