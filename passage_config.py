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

Check the draft against these 5 objectives. For each, return an HONEST status and friendly, specific feedback.

OBJECTIVES:
1. POSITION: Does the draft take a clear, arguable stance? (Not just "I don't like it" — does it make a claim someone could disagree with?)
2. EVIDENCE: Does it reference specific details from the passage AND integrate them meaningfully? (Just dropping a name isn't enough — it should connect to the argument. Quality matters, not just presence.)
3. REASONING: Does it explain WHY with logical depth? (Not just "because it's gross" — does it actually build an argument? Circular reasoning like "it's bad because I don't like it" is weak, not present.)
4. STRUCTURE: Are ideas organized into paragraphs with logical flow? (A single block of text with no paragraphs is "weak" even if it has multiple sentences. "present" requires actual paragraph breaks and ideas grouped logically.)
5. TONE: Does it use academic vocabulary and sentence construction? (Conversational writing like "that is weird" or "people get so mad" is still informal — mark as "weak." "present" requires language a teacher would consider essay-appropriate. Check also for: slang, missing apostrophes, misspellings, run-on sentences.)

Return ONLY valid JSON:
{{
    "overall_ready": true/false,
    "checks": [
        {{
            "objective": "POSITION",
            "status": "present" | "weak" | "missing",
            "tip": "Warm, specific feedback. If present: praise what they did well. If weak/missing: explain WHY this matters and give a friendly nudge."
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
- Be WARM and ENCOURAGING — you are a friendly tutor, not a checklist.
- CRITICAL: Match your feedback language to the student's writing level. Read their draft first. If they use simple words and short sentences, use simple words back. If they write with sophistication, match that.
- CRITICAL: Use SOCRATIC QUESTIONS, not instructions. Your job is to help them THINK, not tell them what to do. Ask questions that guide them to discover what's missing.
  - BAD (telling): "Use specific details from the passage to strengthen your argument."
  - BAD (doing it for them): "Try writing a sentence that starts with 'In the passage, it says that...'"
  - GOOD for basic writer: "What's one thing from the passage that stuck with you? What if you told your reader about it?"
  - GOOD for intermediate: "What specific fact from the passage could you point to that backs up your opinion? How might that make your argument harder to disagree with?"
  - GOOD for advanced: "Where might textual evidence anchor your claim? Which passage details most directly complicate or support your thesis?"
- When status is "present": praise specifically what they did well. Be warm and specific.
- When status is "weak" or "missing": ask a Socratic question that helps them realize what's missing and why it matters. Let THEM figure out the next step.
- "present" = clearly there AND done well. Don't give "present" just because something exists — it has to actually work.
- "weak" = attempted but needs real improvement. This is the honest middle ground — use it freely.
- "missing" = not attempted or so poorly done it doesn't count.
- BE HONEST. Being encouraging does NOT mean pretending everything is good. A student who writes with misspellings, no paragraphs, and "thats weird" as reasoning has WEAK work, not GOOD work. You help them more by being truthful than by cheerleading.
- overall_ready = true ONLY if at least 3 of 5 are "present" (not weak) AND none are "missing". If most areas need work, overall_ready should be false even if nothing is completely missing.
- Keep tips under 35 words. Be specific to their actual draft.
- If draft is very short (< 2 sentences), overall_ready = false.
- NEVER write sentences for them, give templates, or provide fill-in-the-blank starters."""

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

STUDENT'S WRITING LEVEL: {writing_level}
DIMENSION TO FOCUS ON: {dimension_name}
CURRENT SCORE: {current_score}/4
TARGET: {target_score}/4
RATIONALE: {rationale}

STUDENT'S ESSAY:
{essay}

PASSAGE:
{passage}

CRITICAL — MATCH YOUR LANGUAGE TO THE STUDENT:
- If writing level is "basic": Use simple, short sentences. Be warm and encouraging like a patient elementary teacher. Use words they know. Say things like "Can you tell me more about why you think that?" not "Could you elaborate on your analytical reasoning?"
- If writing level is "intermediate": Use clear, conversational academic language. Be supportive but push them gently toward stronger writing.
- If writing level is "advanced": Use sophisticated academic language. Challenge them intellectually. Reference concepts like thesis construction, evidence integration, and rhetorical strategy.

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

STUDENT'S WRITING LEVEL: {writing_level}

IMPORTANT:
- Keep example under 100 words
- Don't rewrite their essay
- MATCH THE EXAMPLE TO THE STUDENT'S LEVEL:
  - Basic writer: Use simple vocabulary, short sentences. The "after" should sound like a strong 4th-5th grader, NOT a college student. No words like "paradox", "neurologically", "autonomous identity", etc.
  - Intermediate writer: Use clear academic language. The "after" should sound like a strong middle schooler.
  - Advanced writer: Use sophisticated language. The "after" can include complex analysis.
- The "before" should be at or slightly below their current level
- The "after" should be ONE step up — achievable, not intimidating
- If the issue is pseudo-academic jargon, show how simpler language is actually clearer
- If the issue is casual/speech-like, show academic register shift

EXAMPLE FORMAT:
**Quick {dimension_name} Example**
Before: "[weaker version at their level]"
After: "[stronger version ONE step up]"

**What Changed:**
- [specific change 1]
- [specific change 2]

**Your Turn:** [specific task for them]
"""

# QUOTE SANDWICH PROMPT - used when Evidence Use is stuck
QUOTE_SANDWICH_PROMPT = """Your evidence needs to be connected to your argument, not just mentioned.

Try the "Quote Sandwich" approach:
1. **Set it up** — tell your reader what you're about to share and why
2. **Share the detail** from the passage
3. **Explain** why it matters for YOUR argument

Example:
- Set it up: "The history of Hawaiian pizza shows that pineapple on pizza is actually a recent experiment."
- Share: "According to the passage, Sam Panopoulos invented it in 1962 at his restaurant in Canada."
- Explain: "This matters because it shows that pineapple pizza isn't a real tradition — it was just one person trying something new."

**Your task:** Pick one fact from the passage that you used in your essay. Can you build a Quote Sandwich around it — set it up, share it, and explain why it matters?"""

REFLECTION_PROMPTS = [
    {
        "question": "What was the hardest part of this writing session for you?",
        "followup_system": """You are a writing coach responding to a student's reflection about their experience.

IMPORTANT RULES:
- You are the COACH talking TO the student
- Do NOT write as if you are the student
- Keep response to 2-3 short sentences

RESPOND WITH:
1. Acknowledge what THEY said was hard (reference their specific words)
2. Normalize it briefly - "That's common because..." (one sentence)
3. End with EXACTLY this question: "Think about the coaching questions I asked you during the session. Was there a specific question or piece of feedback that helped something 'click' for you?"

NOTHING ELSE. No bullet points. No multiple questions. Keep under 75 words."""
    },
    {
        "question": "Think about the coaching questions I asked you during the session. Was there a specific question or piece of feedback that helped something 'click' for you?",
        "followup_system": """You are a writing coach responding to a student's reflection about the coaching they received.

IMPORTANT RULES:
- You are the COACH talking TO the student
- Keep response to 2-3 short sentences

RESPOND WITH:
1. Validate their specific insight about what helped (reference what they said)
2. Briefly explain why that type of feedback works for learning (one sentence)
3. End with EXACTLY this question: "Was there anything about working with the AI tutor that felt confusing, frustrating, or unhelpful? Be honest — your feedback helps us make this better."

NOTHING ELSE. No bullet points. No multiple questions. Keep under 75 words."""
    },
    {
        "question": "Was there anything about working with the AI tutor that felt confusing, frustrating, or unhelpful? Be honest — your feedback helps us make this better.",
        "followup_system": """You are a writing coach responding to a student's honest feedback about the tool.

IMPORTANT RULES:
- You are the COACH talking TO the student
- Keep response to 2-3 short sentences
- Do NOT get defensive — thank them for honesty
- If they say nothing was frustrating, that's fine too

RESPOND WITH:
1. Thank them genuinely for their honesty (reference what THEY said specifically)
2. Briefly acknowledge their point — "That's really useful feedback because..."
3. End with EXACTLY this question: "If you were starting a brand new essay tomorrow without this tutor, what would you do differently because of what you learned today?"

NOTHING ELSE. No bullet points. No multiple questions. Keep under 75 words."""
    },
    {
        "question": "If you were starting a brand new essay tomorrow without this tutor, what would you do differently because of what you learned today?",
        "followup_system": """You are a writing coach giving a final closing response.

IMPORTANT RULES:
- You are the COACH talking TO the student
- Do NOT ask any questions - this is the END
- Keep response to 3-4 short sentences

RESPOND WITH:
1. Affirm their plan specifically (reference what THEY said they would do differently)
2. Frame what they now OWN: "You now know how to..."
3. Congratulate them warmly: "Great work today — you put in real effort and it shows."

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
