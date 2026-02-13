"""
Passage Configuration for Socratic Writing Tutor v1.2

CHANGES FROM v1.1:
- Added varied coaching openers (avoids repetitive "I can see you feel strongly...")
- Added Quote Sandwich requirement for Evidence Use coaching
- Added "Why did you choose that?" intent-probing questions
- Improved reflection prompts with session-specific follow-ups
- Added 4th reflection turn for transfer question
- Academic register requirements in rubric anchors
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
- Use academic language appropriate for a school essay""".strip()

# Roadmap prompt - only shown when Organization <= 2
ROADMAP_PROMPT = """Before you revise, take a moment to plan. What are the 2-3 main ideas you want your essay to cover? You don't need to write full sentences - just name the ideas you want to include."""

VALUE_RUBRIC = {
    "claim_clarity": {
        "name": "Claim Clarity",
        "description": "How clear and specific is the main argument?",
        "anchors": {
            1: "No clear position or position is buried in tangents/rhetoric.",
            2: "Position is implied but vague or stated too casually.",
            3: "Clear position stated in academic language.",
            4: "Precise thesis that frames entire response with academic authority."
        }
    },
    "evidence_use": {
        "name": "Evidence Use",
        "description": "How well does the response use details from the passage?",
        "anchors": {
            1: "No reference to passage or only vague allusions.",
            2: "Mentions facts but doesn't integrate them (data dump).",
            3: "Specific detail cited with signal phrase and brief explanation.",
            4: "Multiple details woven into argument with clear analysis of each."
        }
    },
    "reasoning_depth": {
        "name": "Reasoning Depth",
        "description": "How well does the writer explain WHY?",
        "anchors": {
            1: "No explanation or only assertions without support.",
            2: "Shallow - restates evidence without explaining its significance.",
            3: "Explains connection with analysis using appropriate academic language.",
            4: "Deep analysis showing implications and addressing counterarguments."
        }
    },
    "organization": {
        "name": "Organization",
        "description": "How logically structured is the response?",
        "anchors": {
            1: "No structure - stream of consciousness or scattered ideas.",
            2: "Some structure but jumpy or missing transitions.",
            3: "Logical flow with transitions connecting ideas.",
            4: "Strong progression with clear thesis-evidence-analysis structure."
        }
    },
    "voice_engagement": {
        "name": "Voice & Engagement",
        "description": "Does it sound authentic and appropriately academic?",
        "anchors": {
            1: "Flat, robotic, or reads like a speech/rant rather than essay.",
            2: "Generic or too casual (slang, texting style, performative rhetoric).",
            3: "Engaged and clear while maintaining academic tone.",
            4: "Distinctive scholarly voice that balances personality with precision."
        }
    }
}

DIMENSION_ORDER = ["claim_clarity", "evidence_use", "reasoning_depth", "organization", "voice_engagement"]
TARGET_SCORE = 3

EDGE_CASE_RULES = """Handle edge cases:
- Off-topic but thoughtful: gentle redirect to passage
- Very short (< 3 sentences): encourage expansion with specific question
- Jokes/sarcasm: acknowledge the energy, redirect to academic task
- Copy-paste quotes: score low on evidence, ask for explanation
- Word salad/rhetoric: identify buried claim, ask for clarity
- Pseudo-academic jargon: call out complexity that obscures meaning
- Hostile/resistant: reframe as passion, stay supportive, redirect"""

# VARIED COACHING OPENERS - randomly selected to avoid repetition
COACHING_OPENERS = [
    "Your evidence is stronger now.",
    "You've integrated the data — nice.",
    "The facts are there.",
    "Good move with that quote.",
    "I see what you're going for here.",
    "You're making progress.",
    "That revision shows effort.",
]

COACHING_OPENERS_FIRST_TRY = [
    "I can see you have ideas about this topic.",
    "You've taken a position — that's the starting point.",
    "There's a foundation here to build on.",
    "You've got something to work with.",
]

PRE_VALIDATION_SYSTEM_PROMPT = """You are a writing readiness checker. Do a QUICK scan of a student's draft BEFORE formal assessment. You are NOT scoring — you are checking whether the draft has the basic components for a productive tutoring session.

PASSAGE THE STUDENT READ:
{passage_text}

WRITING PROMPT:
{writing_prompt}

Check the draft against these 5 objectives. For each, return a status and a brief, encouraging tip if something is missing or weak.

OBJECTIVES:
1. POSITION: Does the draft take a clear stance? (Not just summarizing or asking questions)
2. EVIDENCE: Does it reference ANY specific details from the passage? (Names, dates, statistics)
3. REASONING: Does it attempt to explain WHY? (Any "because" or "this means" language)
4. STRUCTURE: Is there more than one idea or paragraph? (Not a single sentence)
5. TONE: Does it use academic language rather than texting, slang, or speech-style?

Return ONLY valid JSON:
{{
    "overall_ready": true/false,
    "checks": [
        {{
            "objective": "POSITION",
            "status": "present" | "weak" | "missing",
            "tip": "Brief encouraging suggestion if weak/missing, empty string if present"
        }},
        {{
            "objective": "EVIDENCE",
            "status": "present" | "weak" | "missing",
            "tip": "..."
        }},
        {{
            "objective": "REASONING",
            "status": "present" | "weak" | "missing",
            "tip": "..."
        }},
        {{
            "objective": "STRUCTURE",
            "status": "present" | "weak" | "missing",
            "tip": "..."
        }},
        {{
            "objective": "TONE",
            "status": "present" | "weak" | "missing",
            "tip": "..."
        }}
    ],
    "summary": "One sentence of encouragement about what's working and what to add"
}}

RULES:
- Be ENCOURAGING, not punitive. This is a helper, not a gatekeeper.
- "present" = clearly there. "weak" = attempted but needs work. "missing" = not attempted.
- overall_ready = true if at least 3 of 5 are "present" or "weak" (not missing).
- Tips should explain WHY this element matters for good writing, not just say what's missing. You are a tutor — help them understand the purpose behind each writing move.
- Keep tips under 25 words. Be specific.
- If draft is very short (< 2 sentences), overall_ready = false.
- NEVER suggest specific words to write."""

SCORING_SYSTEM_PROMPT = """You are a writing assessment engine. Score student
responses against the VALUE rubric. Return ONLY valid JSON.

RUBRIC:
{rubric_text}

SCORING RULES:
- Score 1-4 honestly. 3 = met standard. 4 = exceptional.
- Casual language, slang, or texting-style should be scored lower on Voice (max 2).
- Performative rhetoric (speech-like, campaign-style) should be scored lower on Voice (max 2).
- Pseudo-academic word salad should be scored lower on Claim Clarity and Reasoning.
- Evidence that is mentioned but not explained should be scored 2 on Evidence Use.
- Brief rationale for each score.

RETURN FORMAT:
{{"claim_clarity": {{"score": <int>, "rationale": "<string>"}}, "evidence_use": {{"score": <int>, "rationale": "<string>"}}, "reasoning_depth": {{"score": <int>, "rationale": "<string>"}}, "organization": {{"score": <int>, "rationale": "<string>"}}, "voice_engagement": {{"score": <int>, "rationale": "<string>"}}}}
"""

COACHING_SYSTEM_PROMPT = """You are a Socratic writing coach. Ask questions, don't tell answers.

DIMENSION TO FOCUS ON: {dimension_name}
CURRENT SCORE: {current_score}/4
TARGET: {target_score}/4
RATIONALE: {rationale}

STUDENT'S ESSAY:
{essay}

PASSAGE:
{passage}

COACHING RULES:
1. Ask ONE focused question that helps them discover the problem themselves
2. Reference their essay specifically - quote a phrase if helpful
3. Keep it to 2-4 sentences max
4. Do NOT rewrite their essay or give them the answer

SPECIAL COACHING BY DIMENSION:
- If Claim Clarity is low: Ask them to state their position in one clear sentence
- If Evidence Use is low: Ask them to use a "Quote Sandwich" - introduce, quote, explain
- If Reasoning Depth is low: Ask "Why does that evidence matter for your argument?"
- If Organization is low: Ask them to identify their strongest point and lead with it
- If Voice is low (too casual): Offer ONE academic sentence starter as an option
- If Voice is low (too speech-like): Ask how they'd write this for a teacher, not an audience

INTENT-PROBING QUESTIONS (use occasionally):
- "Why did you choose to put [X] at the end instead of the beginning?"
- "What were you trying to accomplish with [specific phrase]?"
- "If you had to cut one sentence, which would it be and why?"

If writing is too casual (slang like 'super gross', 'it's just pizza'):
- Guide toward academic tone without crushing their voice
- Offer sentence starters: "The evidence suggests..." "This demonstrates that..."
- Validate passion while redirecting: "I can tell you feel strongly — now let's channel it into language that would impress your teacher"
"""

MODEL_EXAMPLE_PROMPT = """Student's {dimension_name} score didn't improve after revision.
Show a SHORT before/after example on a DIFFERENT topic (social media, not pizza).
Explain specifically what changed and why it's stronger.
Ask them to try a similar transformation.

IMPORTANT:
- Keep example under 100 words
- Don't rewrite their essay
- If the issue is pseudo-academic jargon, show how simpler language is actually clearer
- If the issue is casual/speech-like, show academic register shift

EXAMPLE FORMAT:
**Quick Academic Register Example**
Before (Casual): "[casual version]"
After (Academic): "[academic version]"

**What Changed:**
- [specific change 1]
- [specific change 2]

**Your Turn:** [specific task for them]
"""

# QUOTE SANDWICH PROMPT - used when Evidence Use is stuck
QUOTE_SANDWICH_PROMPT = """Your evidence needs to be integrated, not just dropped in.

Try the "Quote Sandwich" approach:
1. **Introduce** the evidence (set it up)
2. **Quote** the specific detail from the passage
3. **Explain** why it matters for your argument

Example:
- Introduce: "The passage provides historical context that supports innovation."
- Quote: "Hawaiian pizza was invented in 1962 by Sam Panopoulos."
- Explain: "This shows that food traditions are actually quite recent inventions themselves."

**Your task:** Take one fact from the passage and build a Quote Sandwich around it."""

REFLECTION_PROMPTS = [
    {
        "question": "What was the hardest part of this session for you?",
        "followup_system": """You are a writing coach responding to a student's reflection.

IMPORTANT RULES:
- You are the COACH talking TO the student
- Do NOT write as if you are the student
- Keep response to 2-3 short sentences

RESPOND WITH:
1. Acknowledge what THEY said was hard (reference their specific words)
2. Normalize it briefly - "That's common because..." (one sentence)
3. End with EXACTLY this question: "What is one thing you noticed about your writing that you didn't see before?"

NOTHING ELSE. No bullet points. No multiple questions. Keep under 75 words."""
    },
    {
        "question": "What is one thing you noticed about your writing that you didn't see before?",
        "followup_system": """You are a writing coach responding to a student's reflection.

IMPORTANT RULES:
- You are the COACH talking TO the student
- Keep response to 2-3 short sentences

RESPOND WITH:
1. Validate their specific insight (reference what they said)
2. Explain why noticing that matters for future writing (one sentence)
3. End with EXACTLY this question: "If you were starting a brand new essay right now, what would you do differently?"

NOTHING ELSE. No bullet points. No multiple questions. Keep under 75 words."""
    },
    {
        "question": "If you were starting a brand new essay right now, what would you do differently?",
        "followup_system": """You are a writing coach responding to a student's reflection.

IMPORTANT RULES:
- You are the COACH talking TO the student
- Keep response to 2-3 short sentences

RESPOND WITH:
1. Affirm their plan specifically (reference what THEY said they would do differently)
2. Connect it to a transferable skill: "This approach of [X] is powerful because..."
3. End with EXACTLY this question: "Where else in school or life could you use this strategy?"

NOTHING ELSE. No bullet points. No multiple questions. Keep under 75 words."""
    },
    {
        "question": "Where else in school or life could you use this strategy?",
        "followup_system": """You are a writing coach giving a final closing response.

IMPORTANT RULES:
- You are the COACH talking TO the student
- Do NOT ask any questions - this is the END
- Keep response to 3-4 short sentences

RESPOND WITH:
1. Affirm their transfer examples (reference what THEY said)
2. Frame what they now OWN: "You now know how to..."
3. Congratulate them warmly: "Well done today - you put in real work here..."

NOTHING ELSE. No questions. No bullet points. This is the closing. Keep under 100 words."""
    }
]

# Session-aware celebration messages - varies based on journey
CELEBRATION_MESSAGES = {
    "first_try": [
        "You hit all the targets on your first try.",
        "That doesn't happen often. Here's what worked:",
    ],
    "quick_success": [  # 1-2 revisions
        "You got there in just {revisions} revision{s}.",
        "What changed:",
    ],
    "solid_work": [  # 3-5 revisions
        "{revisions} revisions later, your essay meets the standard.",
        "What changed:",
    ],
    "persistence": [  # 6+ revisions
        "It took {revisions} rounds of revision, and you pushed through.",
        "What changed:",
    ],
    "adversarial": [  # 8+ revisions - acknowledge the journey
        "It took {revisions} rounds of revision, and you pushed through.",
        "That took persistence — here's what finally clicked:",
    ]
}

RESCORE_FRAMING = "Let me look at your updated response..."

MICRO_CELEBRATION_TEMPLATES = [
    "Your {dimension} jumped from {old} to {new} — nice work!",
    "{dimension} improved from {old} to {new}.",
    "Good progress on {dimension} ({old} → {new}).",
]

def get_rubric_text():
    lines = []
    for key, dim in VALUE_RUBRIC.items():
        lines.append(f"{dim['name']}: {dim['description']}")
        for score, anchor in dim['anchors'].items():
            lines.append(f"  {score}: {anchor}")
    return "\n".join(lines)
