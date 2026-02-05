"""
Controlled Stimulus Package — Socratic Writing Tutor v0.3
===========================================================
Passage + Prompt + Scoring Anchors + Edge-Case Guidance

Topic: Pineapple on Pizza (low ego threat, high engagement, universal access)

Design Principles:
- Everyone reads the same ~450-word passage presenting both sides
- Everyone responds to the same analytical prompt
- Scoring uses VALUE rubric with CONCRETE ANCHORS at each level
- Edge-case guidance helps the AI distinguish 3 from 4
- Creative/unexpected connections are explicitly rewarded

License: Original work — free for educational and research use.
"""

# ============================================================
# THE PASSAGE (~450 words)
# ============================================================

READING_PASSAGE = {
    "title": "The Great Pineapple Debate: A Food Fight with Surprising Depth",
    "body": (
        "In 2017, the president of Iceland made international headlines when he jokingly "
        "told a group of high school students that, if he had the power, he would ban "
        "pineapple as a pizza topping. The comment went viral. Within hours, thousands of "
        "people around the world were arguing passionately about fruit on pizza. It was "
        "funny — but the intensity was real.\n\n"

        "Hawaiian pizza — topped with pineapple and ham — was invented in 1962 by Sam "
        "Panopoulos, a Greek-Canadian restaurant owner in Ontario. He was experimenting "
        "with Chinese-American sweet-and-sour flavors and decided to try canned pineapple "
        "on a pizza. Customers loved it. Within a decade, Hawaiian pizza had spread across "
        "North America and beyond. Today it is consistently ranked among the top five most "
        "popular pizza varieties worldwide, and some surveys place it at number one in "
        "Australia.\n\n"

        "Opponents of pineapple on pizza often frame their objection in terms of culinary "
        "tradition. Pizza, they argue, is an Italian creation with a specific identity: "
        "dough, tomato sauce, cheese, and savory toppings. Adding sweet fruit disrupts the "
        "flavor profile that defines the dish. Italian celebrity chef Gordon Ramsay has "
        "famously called pineapple on pizza an abomination, and a 2016 YouGov poll found "
        "that it was the single most disliked topping in the United States, with 56% of "
        "respondents saying they disapproved of it.\n\n"

        "Supporters counter that food traditions are never static. Tomatoes themselves were "
        "not part of Italian cooking until the 16th century, when they were imported from "
        "the Americas and initially regarded with suspicion. The combination of sweet and "
        "savory is fundamental to many of the world's great cuisines, from Chinese "
        "sweet-and-sour dishes to Moroccan tagines with dried fruit. Food scientists note "
        "that pineapple's acidity can cut through the richness of cheese and meat, creating "
        "a balanced flavor experience — similar to how a squeeze of lemon brightens a "
        "heavy dish.\n\n"

        "What makes this debate interesting is not really about pizza. It is about how "
        "people think about tradition, authenticity, and taste. Research in food psychology "
        "suggests that what people consider 'disgusting' in food is largely cultural, not "
        "biological. A combination that feels wrong in one culture — like fruit with cheese "
        "— may feel completely natural in another. The pineapple debate, beneath its silly "
        "surface, is actually a small window into how we construct rules about what belongs "
        "and what doesn't — and how fiercely we defend those rules even when we can't fully "
        "explain them."
    ),
    "word_count": 407,
    "source_note": "Original synthesis — free for educational and research use.",
}


# ============================================================
# THE PROMPT
# ============================================================

WRITING_PROMPT = {
    "title": "Analytical Response: The Pineapple Debate",
    "instructions": (
        "After reading the passage above, write a 250–400 word response to the "
        "following question:\n\n"
        "**Does the passage make a stronger case for or against pineapple on pizza? "
        "Explain your reasoning using specific details from the text, and discuss "
        "what the debate reveals about how people think about food, tradition, or "
        "cultural rules.**\n\n"
        "Your response should:\n"
        "- Take a clear position\n"
        "- Reference specific evidence from the passage\n"
        "- Go beyond summary to analyze *why* the evidence matters\n"
        "- Be well-organized and clearly written"
    ),
    "license": "Original prompt — free for educational and research use.",
}


# ============================================================
# SCORING ANCHORS (VALUE Rubric with concrete examples)
# ============================================================
# Each dimension has:
#   - Level descriptors (standard VALUE language)
#   - Concrete "looks like" examples at each level
#   - Edge-case guidance for distinguishing adjacent levels
#   - Creative connection reward criteria

SCORING_ANCHORS = {
    "context_and_purpose": {
        "name": "Context & Purpose",
        "dimension_key": "context_and_purpose",
        "anchors": {
            4: {
                "descriptor": "Demonstrates thorough understanding of context, audience, and purpose.",
                "looks_like": (
                    "The response clearly addresses the analytical prompt, not just 'pineapple opinions.' "
                    "It shows awareness that the reader needs evidence, not just preference. "
                    "The writer shapes the entire response around a clear analytical purpose — "
                    "e.g., 'The passage actually argues for pineapple, but not for the reasons you'd expect.' "
                    "Every paragraph serves that purpose."
                ),
                "example_signal": "Opening frames the analysis, not just the topic. Conclusion returns to the analytical question.",
            },
            3: {
                "descriptor": "Demonstrates adequate consideration of context, audience, and purpose.",
                "looks_like": (
                    "The response addresses the prompt and has a clear position. "
                    "It reads like an essay, not a text message. "
                    "But the purpose may drift — e.g., starts analyzing the passage, "
                    "then shifts to personal pizza preferences without connecting back."
                ),
                "example_signal": "Has a thesis. Mostly stays on task. Audience awareness is present but inconsistent.",
            },
            2: {
                "descriptor": "Demonstrates awareness of context, audience, and purpose.",
                "looks_like": (
                    "The response is about the right topic but treats the prompt as 'write about pineapple on pizza' "
                    "rather than 'analyze what the passage argues.' May read like a blog post or rant. "
                    "Position exists but is stated as preference rather than analytical claim."
                ),
                "example_signal": "'I think pineapple is good on pizza because I like it.' Topic: correct. Task: missed.",
            },
            1: {
                "descriptor": "Demonstrates minimal attention to context, audience, and purpose.",
                "looks_like": (
                    "Response ignores the passage entirely, or treats the prompt as a yes/no question. "
                    "'Pineapple is disgusting. End of story.' No engagement with the analytical task."
                ),
                "example_signal": "No thesis. No reference to the passage. No awareness of audience.",
            },
        },
        "edge_case_3v4": (
            "The key distinction: a 3 answers the prompt. A 4 shapes the entire response around a "
            "deliberate analytical strategy. If the writer has a thesis AND every paragraph serves it "
            "AND the conclusion does more than repeat the thesis, it's a 4. If any section drifts "
            "into personal opinion disconnected from the analysis, it's a 3."
        ),
    },

    "content_development": {
        "name": "Content Development",
        "dimension_key": "content_development",
        "anchors": {
            4: {
                "descriptor": "Uses compelling content to illustrate mastery, shaping the whole work.",
                "looks_like": (
                    "The response doesn't just cite the passage — it interrogates it. "
                    "'The passage notes that 56% of Americans dislike pineapple topping, "
                    "but then points out that tomatoes were once rejected too. That parallel "
                    "undermines the tradition argument by showing that today's staple was yesterday's "
                    "abomination.' The writer is doing analytical work, not just reporting facts."
                ),
                "example_signal": "Evidence is used to BUILD an argument, not just decorate one.",
            },
            3: {
                "descriptor": "Uses relevant content to explore ideas within context.",
                "looks_like": (
                    "The response cites specific details from the passage — the YouGov poll, "
                    "Sam Panopoulos, the Iceland president — and uses them to support a position. "
                    "But the analysis stays surface-level: 'This shows that people disagree' "
                    "rather than 'This reveals something about how tradition works.'"
                ),
                "example_signal": "Good evidence selection. Analysis tells you WHAT but not WHY IT MATTERS.",
            },
            2: {
                "descriptor": "Uses appropriate content to develop ideas through most of the work.",
                "looks_like": (
                    "Mentions a few details from the passage but mostly argues from personal experience. "
                    "'The passage talks about how pineapple is popular in Australia. "
                    "I personally think it tastes great because the sweetness balances the cheese.' "
                    "Some passage engagement, but the argument runs on opinion."
                ),
                "example_signal": "Some evidence from text, but personal experience carries the argument.",
            },
            1: {
                "descriptor": "Uses content to develop simple ideas in some parts of the work.",
                "looks_like": (
                    "Vague or no references to the passage. 'People have lots of opinions about pizza.' "
                    "May summarize the passage without taking a position."
                ),
                "example_signal": "Summary without analysis, or opinion without evidence.",
            },
        },
        "edge_case_3v4": (
            "A 3 cites evidence and connects it to a claim. A 4 explains WHY the evidence matters — "
            "it does interpretive work. The test: does the writer say something about the evidence "
            "that isn't obvious from just reading the passage? If they're making a move the passage "
            "doesn't explicitly make, that's a 4."
        ),
        "creative_connection_guidance": (
            "IMPORTANT: If a student draws an unexpected but valid connection — comparing the pineapple "
            "debate to Star Trek's treatment of alien food customs, or to generational arguments about "
            "music, or to how languages evolve — this should be REWARDED as a 4 in content development, "
            "not penalized. The VALUE rubric rewards 'compelling content that illustrates mastery.' "
            "An unexpected analogy that genuinely illuminates the argument IS mastery. "
            "The test is not 'did they stay inside the passage' but 'did the connection deepen the analysis?'"
        ),
    },

    "genre_and_conventions": {
        "name": "Genre & Disciplinary Conventions",
        "dimension_key": "genre_and_conventions",
        "anchors": {
            4: {
                "descriptor": "Detailed attention to conventions including organization, content, presentation, and style.",
                "looks_like": (
                    "Clear intro → body → conclusion structure. Thesis is arguable, not just a fact. "
                    "Transitions connect ideas logically ('However, the passage complicates this by...'). "
                    "Counterargument is acknowledged. Tone is appropriate for analytical writing — "
                    "can be conversational but not sloppy."
                ),
                "example_signal": "Reads like a confident short essay. Structure serves the argument.",
            },
            3: {
                "descriptor": "Consistent use of important conventions for organization, content, and style.",
                "looks_like": (
                    "Has paragraphs, has a thesis, mostly follows essay conventions. "
                    "But transitions may be mechanical ('Another reason is...') or the "
                    "counterargument may be missing. Organization works but doesn't enhance."
                ),
                "example_signal": "Follows the formula. Structure is present but doesn't add meaning.",
            },
            2: {
                "descriptor": "Follows basic expectations for organization, content, and presentation.",
                "looks_like": (
                    "Has some paragraph breaks but organization is loose. "
                    "May jump between points without transitions. Reads more like a freewrite "
                    "than an essay. Thesis may be buried or implied."
                ),
                "example_signal": "You can follow the argument, but it takes work.",
            },
            1: {
                "descriptor": "Attempts to use a consistent system for basic organization.",
                "looks_like": (
                    "Wall of text or very short. No clear structure. "
                    "Stream of consciousness. 'So basically pineapple is fine I mean why not "
                    "people eat weird stuff all the time and the passage says...'"
                ),
                "example_signal": "No paragraphs, no thesis, no structure.",
            },
        },
        "edge_case_3v4": (
            "A 3 follows conventions. A 4 uses them strategically. If the structure actively helps "
            "the argument — e.g., saving the strongest point for last, or opening with the "
            "counterargument to dismantle it — that's a 4. If the structure is correct but "
            "interchangeable (paragraphs could be reordered without loss), it's a 3."
        ),
    },

    "sources_and_evidence": {
        "name": "Sources & Evidence",
        "dimension_key": "sources_and_evidence",
        "anchors": {
            4: {
                "descriptor": "Skillful use of credible, relevant sources to develop ideas.",
                "looks_like": (
                    "Cites specific details from the passage BY NAME or SPECIFICITY: "
                    "'the 2016 YouGov poll,' 'Sam Panopoulos in 1962,' 'food scientists note that acidity...' "
                    "Uses multiple pieces of evidence and CONNECTS them to each other. "
                    "'While the poll shows widespread dislike, the passage's point about tomato history "
                    "suggests that popular opinion is a poor measure of culinary legitimacy.'"
                ),
                "example_signal": "Named sources. Multiple evidence points. Evidence talks to each other.",
            },
            3: {
                "descriptor": "Consistent use of credible, relevant sources to support ideas.",
                "looks_like": (
                    "References specific facts from the passage — the percentage, the inventor, "
                    "the Iceland story — and uses them to support claims. But evidence is deployed "
                    "one-at-a-time rather than synthesized. Each paragraph has its own fact; "
                    "facts don't interact."
                ),
                "example_signal": "Good evidence. Used in parallel, not in conversation.",
            },
            2: {
                "descriptor": "Attempts to use credible and/or relevant sources to support ideas.",
                "looks_like": (
                    "Vague references: 'the passage mentions a poll' or 'some chef said it's bad.' "
                    "Details are imprecise or paraphrased to the point of inaccuracy. "
                    "May have only one piece of evidence for the whole response."
                ),
                "example_signal": "'The passage says some people don't like it.' True but unspecific.",
            },
            1: {
                "descriptor": "Demonstrates an attempt to use sources.",
                "looks_like": (
                    "'According to the passage, pineapple on pizza is debated.' "
                    "Or no reference to the passage at all — pure opinion."
                ),
                "example_signal": "Token reference or none.",
            },
        },
        "edge_case_3v4": (
            "A 3 uses evidence correctly. A 4 uses evidence in CONVERSATION — connecting "
            "two or more pieces of evidence to build a point neither makes alone. "
            "If the response has 3+ specific citations AND at least one moment where "
            "two pieces of evidence are explicitly linked, it's a 4. "
            "If evidence points stand alone supporting separate claims, it's a 3."
        ),
        "creative_connection_guidance": (
            "If a student brings in valid outside knowledge — e.g., 'This is like how sushi was "
            "considered disgusting in America until the 1980s' — this counts as evidence IF it "
            "genuinely supports the analytical point. Outside connections that deepen the argument "
            "should push toward a 4, not be penalized for going 'off-text.' The rubric says "
            "'credible, relevant sources' — a relevant analogy from general knowledge IS a source."
        ),
    },

    "syntax_and_mechanics": {
        "name": "Syntax & Mechanics",
        "dimension_key": "syntax_and_mechanics",
        "anchors": {
            4: {
                "descriptor": "Graceful language that communicates meaning with clarity and fluency.",
                "looks_like": (
                    "Sentences vary in length and structure. Word choices are precise. "
                    "The writing has a voice — you can hear the writer thinking. "
                    "Virtually no errors. Reads smoothly aloud."
                ),
                "example_signal": "You notice the WRITING, not just the ideas. Has style.",
            },
            3: {
                "descriptor": "Straightforward language that generally conveys meaning. Few errors.",
                "looks_like": (
                    "Clear and readable. Sentences work but don't surprise. "
                    "A few minor errors (comma splice, its/it's) that don't impede meaning. "
                    "Functional but not distinctive."
                ),
                "example_signal": "Competent. You don't stumble. But you don't stop to admire either.",
            },
            2: {
                "descriptor": "Language generally conveys meaning, though with some errors.",
                "looks_like": (
                    "Meaning comes through but sentences are choppy, repetitive, or run-on. "
                    "Some errors that slow the reader down. Word choices are vague "
                    "('stuff,' 'things,' 'a lot')."
                ),
                "example_signal": "You have to re-read some sentences. Meaning is recoverable but effortful.",
            },
            1: {
                "descriptor": "Language sometimes impedes meaning because of errors.",
                "looks_like": (
                    "Frequent errors in grammar, spelling, or sentence structure that make "
                    "it hard to understand the argument. May be texting style applied to essay."
                ),
                "example_signal": "You're unsure what the writer means in places.",
            },
        },
        "edge_case_3v4": (
            "A 3 is clear. A 4 has VOICE. The test: could you identify this writer's style "
            "if you read their work without a name on it? If the language is correct but "
            "could have been written by anyone, it's a 3. If there's a distinctive quality — "
            "humor, precision, rhythm, a well-placed short sentence after a long one — it's a 4. "
            "NOTE: Casual or conversational tone is NOT automatically a demerit. "
            "A writer who uses informality deliberately and effectively can earn a 4."
        ),
    },
}


# ============================================================
# CREATIVE CONNECTION POLICY
# ============================================================
# This is injected into the assessment prompt so the AI knows
# how to handle unexpected but valid student moves.

CREATIVE_CONNECTION_POLICY = (
    "IMPORTANT SCORING PRINCIPLE — Rewarding Creative Connections:\n\n"
    "Students may draw unexpected analogies or bring in outside knowledge to support "
    "their analysis. Examples:\n"
    "- Comparing the pineapple debate to how languages evolve ('ain't' was once unacceptable)\n"
    "- Connecting food rules to Star Trek's depiction of alien cultural norms\n"
    "- Drawing parallels to music gatekeeping ('rock isn't real music')\n"
    "- Relating it to fashion rules ('you can't wear white after Labor Day')\n\n"
    "These connections should be REWARDED, not penalized, IF:\n"
    "1. The connection genuinely illuminates the analytical point\n"
    "2. The student explains HOW it connects (not just drops it in)\n"
    "3. It deepens the argument rather than replacing it\n\n"
    "A creative connection that meets these criteria should push the score UP in both "
    "Content Development and Sources & Evidence. The VALUE rubric's highest level "
    "describes 'compelling content that illustrates mastery' — an unexpected analogy "
    "that works IS mastery.\n\n"
    "However, a creative reference that is merely mentioned without analytical connection "
    "('This is like that one Star Trek episode') should not receive extra credit. "
    "The connection must do analytical work."
)


# ============================================================
# EDGE-CASE DECISION FRAMEWORK
# ============================================================
# When the AI is torn between adjacent scores, use these rules.

EDGE_CASE_FRAMEWORK = (
    "SCORING DECISION FRAMEWORK — When Torn Between Adjacent Scores:\n\n"
    "When a response seems to fall between two levels (e.g., 'is this a 3 or a 4?'), "
    "apply these tiebreaker principles:\n\n"
    "1. LOOK FOR THE MOVE: Does the response do something with the evidence, or just "
    "present it? Doing something = higher score.\n\n"
    "2. COUNT THE CONNECTIONS: How many distinct pieces of evidence from the passage "
    "are cited with specificity? 0-1 = Level 2. 2-3 = Level 3. 3+ with synthesis = Level 4.\n\n"
    "3. CHECK THE 'SO WHAT': After each piece of evidence, does the writer explain "
    "why it matters? If yes for most evidence → higher score. If evidence just sits "
    "there → lower score.\n\n"
    "4. REWARD RISK: If the student attempts something ambitious — a creative analogy, "
    "an unusual structural choice, a counterintuitive reading of the passage — and it "
    "mostly works, score the attempt generously. We want to encourage intellectual risk. "
    "A partially successful ambitious move is worth more than a safe, competent one.\n\n"
    "5. THE VOICE TEST (Syntax only): Read the response aloud. If you hear a human "
    "voice with personality, lean toward 4. If it sounds like it could be anyone, lean "
    "toward 3. If you stumble while reading, lean toward 2.\n\n"
    "6. WHEN IN TRUE DOUBT: Score the higher level. This is a formative assessment "
    "designed to encourage growth, not a gatekeeping mechanism. Benefit of the doubt "
    "goes to the student."
)


# ============================================================
# APP CONFIGURATION
# ============================================================
# Wire this into the Streamlit app as the default passage/prompt

APP_CONFIG = {
    "passage": READING_PASSAGE,
    "prompt": WRITING_PROMPT,
    "scoring_anchors": SCORING_ANCHORS,
    "creative_policy": CREATIVE_CONNECTION_POLICY,
    "edge_case_framework": EDGE_CASE_FRAMEWORK,
    "rubric_name": "AAC&U VALUE Written Communication (with scoring anchors)",
}
