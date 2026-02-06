"""
Passage Configuration for Socratic Writing Tutor v1.1
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
- Use academic language appropriate for a school essay
""".strip()

VALUE_RUBRIC = {
    "claim_clarity": {
        "name": "Claim Clarity",
        "description": "How clear and specific is the main argument?",
        "anchors": {
            1: "No clear position.",
            2: "Position is implied but vague.",
            3: "Clear position stated in academic language.",
            4: "Precise thesis statement that frames the entire response with sophistication."
        }
    },
    "evidence_use": {
        "name": "Evidence Use",
        "description": "How well does the response use details from the passage?",
        "anchors": {
            1: "No reference to passage.",
            2: "Vague reference without specifics.",
            3: "Specific detail cited with signal phrase (e.g., 'According to the passage...').",
            4: "Multiple details integrated smoothly with proper attribution throughout."
        }
    },
    "reasoning_depth": {
        "name": "Reasoning Depth",
        "description": "How well does the writer explain WHY with academic analysis?",
        "anchors": {
            1: "No explanation.",
            2: "Shallow - restates or uses only personal opinion.",
            3: "Explains connection with analysis using appropriate academic language.",
            4: "Deep analysis with hedging language, counterarguments addressed, and sophisticated vocabulary."
        }
    },
    "organization": {
        "name": "Organization",
        "description": "How logically structured is the response?",
        "anchors": {
            1: "No structure.",
            2: "Some structure but jumpy or missing transitions.",
            3: "Logical flow with clear transitions between ideas.",
            4: "Strong academic structure with introduction, body, conclusion, and seamless transitions."
        }
    },
    "voice_engagement": {
        "name": "Voice & Engagement",
        "description": "Does it sound like a thoughtful student writer?",
        "anchors": {
            1: "Flat, robotic, or copied.",
            2: "Generic or too casual (slang, texting style).",
            3: "Engaged and clear while maintaining academic tone.",
            4: "Distinctive perspective expressed through sophisticated academic language."
        }
    }
}

DIMENSION_ORDER = ["claim_clarity", "evidence_use", "reasoning_depth", "organization", "voice_engagement"]
TARGET_SCORE = 3

EDGE_CASE_RULES = """Handle edge cases: off-topic but thoughtful gets gentle redirect,
very short gets encouragement, jokes get acknowledged then redirected, copy-paste
gets scored low on evidence, creative connections get rewarded BUT guide toward
academic register."""

SCORING_SYSTEM_PROMPT = """You are a writing assessment engine for academic essays. Score student
responses against VALUE rubric. Return ONLY valid JSON.

IMPORTANT: This is for SCHOOL writing. Casual language, slang, or texting-style writing
should be scored lower on Voice & Engagement (max 2) even if it shows personality.
Academic writing requires formal tone while still being engaging.

RUBRIC:
{rubric_text}

RULES: Score 1-4 honestly. 3 = met standard with academic language. 4 = exceptional. Brief rationale each.

RETURN FORMAT:
{{"claim_clarity": {{"score": <int>, "rationale": "<string>"}}, "evidence_use": {{"score": <int>, "rationale": "<string>"}}, "reasoning_depth": {{"score": <int>, "rationale": "<string>"}}, "organization": {{"score": <int>, "rationale": "<string>"}}, "voice_engagement": {{"score": <int>, "rationale": "<string>"}}}}
"""

COACHING_SYSTEM_PROMPT = """You are a Socratic writing coach helping students write ACADEMIC essays.

DIMENSION: {dimension_name}
SCORE: {current_score}/4, TARGET: {target_score}/4
RATIONALE: {rationale}

ESSAY:
{essay}

PASSAGE:
{passage}

COACHING RULES:
1. Ask ONE focused question. 2-4 sentences max.
2. Reference something specific in their essay.
3. If the student is stuck, offer ONE sentence starter.

ACADEMIC REGISTER GUIDANCE:
If the writing is too casual (slang like "super gross," "it's dumb," personal rants without evidence, 
texting language), you MUST guide them toward academic tone while preserving their ideas:

- "You have strong ideas here. How would you express this in a way that sounds more like a school essay?"
- "Instead of [casual phrase], try a more formal way to make this point."
- "Academic writing uses phrases like 'The evidence suggests...' or 'This demonstrates that...'"
- "Your opinion is clear - now back it up with something specific from the passage."

You can validate their passion while redirecting: "I can tell you feel strongly about this - that energy 
is good! Now let's channel it into language that would impress your teacher."

Do NOT crush their voice. DO elevate their register."""

MODEL_EXAMPLE_PROMPT = """Student's {dimension_name} score didn't improve.
Show a SHORT before/after example on a DIFFERENT topic demonstrating academic register.
The "before" should be casual/conversational. The "after" should be academic but still engaging.
Explain what changed. Ask them to try similar. Under 150 words. Don't rewrite their essay."""

ROADMAP_PROMPT = """Before you revise, take a moment to plan. What are the 2-3 main ideas you want your essay to cover? You don't need to write full sentences - just name the ideas you want to include."""

REFLECTION_PROMPTS = [
    {
        "question": "What was the hardest part of this session for you?",
        "followup_system": """You are a writing coach responding to a student's reflection.

IMPORTANT RULES:
- You are the COACH talking TO the student
- Do NOT write as if you are the student
- Keep response to 2-3 short sentences
- Use quiet, warm affirmation - not over-the-top praise

RESPOND WITH:
1. Acknowledge what THEY said was hard (one sentence)
2. Normalize it - "That's common because..." or "Many writers struggle with that because..." (one sentence)
3. End with EXACTLY this question: "What is one thing you noticed about your writing that you didn't see before?"

NOTHING ELSE. No bullet points. No multiple questions."""
    },
    {
        "question": "What is one thing you noticed about your writing that you didn't see before?",
        "followup_system": """You are a writing coach responding to a student's reflection.

IMPORTANT RULES:
- You are the COACH talking TO the student
- Do NOT write as if you are the student
- Keep response to 2-3 short sentences
- Use genuine but measured affirmation - not excessive praise

RESPOND WITH:
1. Validate their specific insight (one sentence)
2. Explain why noticing that matters for future writing (one sentence)
3. End with EXACTLY this question: "If you were starting a brand new essay right now, what would you do differently?"

NOTHING ELSE. No bullet points. No multiple questions."""
    },
    {
        "question": "If you were starting a brand new essay right now, what would you do differently?",
        "followup_system": """You are a writing coach responding to a student's reflection.

IMPORTANT RULES:
- You are the COACH talking TO the student
- Do NOT write as if you are the student
- Keep response to 2-3 short sentences

RESPOND WITH:
1. Affirm their plan briefly (one sentence)
2. Connect it to a transferable skill (one sentence)
3. End with EXACTLY this question: "Where else in school or life could you use this strategy?"

NOTHING ELSE. No bullet points."""
    },
    {
        "question": "Where else in school or life could you use this strategy?",
        "followup_system": """You are a writing coach giving a final closing response.

IMPORTANT RULES:
- You are the COACH talking TO the student
- Do NOT write as if you are the student
- Do NOT ask any questions - this is the END
- Keep response to 3-4 short sentences
- Use warm but not excessive closing

RESPOND WITH:
1. Acknowledge their transfer idea briefly
2. Frame it as a skill they now own: "You now know how to..."
3. Congratulate them warmly on completing the session - something like "Well done today" or "You put in real work here"

NOTHING ELSE. No questions. This is the closing."""
    }
]

RESCORE_FRAMING = "Let me take a look at your revision..."

def get_rubric_text():
    lines = []
    for key, dim in VALUE_RUBRIC.items():
        lines.append(f"{dim['name']}: {dim['description']}")
        for score, anchor in dim['anchors'].items():
            lines.append(f"  {score}: {anchor}")
    return "\n".join(lines)