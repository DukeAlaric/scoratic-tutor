"""
Passage Configuration for Socratic Writing Tutor v0.6
All content is original or OER.
"""

READING_PASSAGE = """
**The Great Pineapple Debate**

In 1962, Sam Panopoulos, a Greek-born restaurant owner in Ontario, Canada, placed canned
pineapple on a pizza and inadvertently started one of the most passionate food arguments in
modern history. More than sixty years later, the question of whether pineapple belongs on pizza
continues to divide friends, families, and even world leaders.

Supporters of pineapple on pizza argue that the combination of sweet and savory flavors is not
only legitimate but backed by basic food science. The Maillard reaction between the fruit's
sugars and the cheese's proteins creates complex flavor compounds that many palates find
appealing. Hawaiian pizza -- typically topped with pineapple and ham -- is now ranked among
the top five most popular pizza varieties worldwide, suggesting that millions of people enjoy it
as more than a novelty.

Critics counter that pizza is rooted in Italian culinary tradition, and that adding tropical fruit
violates the balance of flavors that defines a well-made pie. In 2017, Icelandic President
Gudni Th. Johannesson joked that he would ban pineapple on pizza if he could, sparking
international headlines. A 2021 YouGov survey found that 56% of respondents in several
countries expressed disapproval of the topping, with "it doesn't belong" cited more often than
any specific flavor complaint.

Food psychologists note that much of the debate has little to do with taste. People's food
preferences are shaped by cultural identity, childhood exposure, and social belonging. Rejecting
pineapple on pizza often functions as a form of cultural gatekeeping -- a way of signaling
allegiance to "authentic" food traditions. Meanwhile, embracing it can be an act of culinary
openness, a refusal to let tradition dictate personal enjoyment. The pineapple debate, in other
words, is rarely about pineapple. It is about how people decide what is acceptable, who gets to
make that decision, and why the answer matters to them at all.
"""

WRITING_PROMPT = """
**Your Task:**

After reading "The Great Pineapple Debate," write an analytical response (3-5 paragraphs)
that addresses this question:

**Does the passage make a stronger case for or against pineapple on pizza? Explain your
reasoning using specific details from the text.**

In your response:
- Take a clear position
- Support your argument with evidence from the passage
- Consider what the debate reveals beyond just pizza

Write your response below.
"""

SCORING_ANCHORS = {
    "context_and_purpose": {
        "name": "Context & Purpose",
        "description": "Does the writer demonstrate understanding of the task, audience, and purpose?",
        "levels": {
            4: "The writer clearly understands they are analyzing the passage, not just sharing their pizza opinion. The response guides the reader through reasoning. The thesis does real work.",
            3: "Has a thesis. Mostly stays on task. Audience awareness is present but inconsistent.",
            2: "Reads more like a personal reaction than an analysis. Purpose is unclear.",
            1: "Unclear what the writer is trying to do. May ignore the prompt entirely."
        }
    },
    "content_development": {
        "name": "Content Development",
        "description": "How thoroughly does the writer develop their argument?",
        "levels": {
            4: "The argument is built, not just stated. Ideas connect logically, evidence is explained, and the writer shows WHY evidence supports their point. Addresses complexity.",
            3: "Has an argument with some evidence. Development is uneven -- some points explained, others just asserted.",
            2: "States a position with thin reasoning. Evidence mentioned but not explained.",
            1: "Little to no development. Opinion with no support, or summary without a position."
        }
    },
    "genre_and_conventions": {
        "name": "Genre & Disciplinary Conventions",
        "description": "Does the writer show what the author is DOING, not just what the passage says?",
        "levels": {
            4: "Names what the author is doing -- 'the author uses X to show Y.' This is analysis, not summary.",
            3: "Some analytical moves but inconsistent. Sometimes explains strategy, sometimes just restates.",
            2: "Mostly summary. Tells what the passage contains but not what the author does with it.",
            1: "No awareness of genre. Casual opinion or disconnected facts."
        }
    },
    "sources_and_evidence": {
        "name": "Sources & Evidence",
        "description": "How effectively does the writer use specific details from the passage?",
        "levels": {
            4: "Evidence is specific (names, numbers, references), well-chosen, clearly connected to the argument. Multiple pieces work together.",
            3: "Some specific evidence but connections to argument are sometimes weak.",
            2: "Vague references without specifics, or specifics without connection to argument.",
            1: "No engagement with the passage. Unsupported claims or pure opinion."
        }
    },
    "syntax_and_mechanics": {
        "name": "Syntax & Mechanics",
        "description": "How well does the writer control language?",
        "levels": {
            4: "Sentences are varied and purposeful. Writing flows. Grammar is clean. Word choice is precise.",
            3: "Generally clear with some variety. Occasional awkward phrasing.",
            2: "Functional but flat. Same sentence patterns. Some errors interfere with clarity.",
            1: "Frequent errors make meaning unclear."
        }
    }
}

EDGE_CASE_FRAMEWORK = """
When scoring falls between two levels, use these tiebreakers:
1. If writing shows awareness of the skill even if execution is inconsistent, score higher.
2. If a single strong moment elevates an otherwise weaker response, weight it.
3. If errors are careless (typos) rather than conceptual, don't penalize analytical score.
4. If the writer takes a creative approach that serves the analytical purpose, reward it.
5. If the writer addresses complexity a simpler response would avoid, that is higher-level thinking.
6. When in true doubt, score the higher level. This is formative, not gatekeeping.
"""

CREATIVE_CONNECTION_POLICY = """
Students may make unexpected connections -- comparing pineapple gatekeeping to music
snobbery, relating food traditions to their own community, referencing pop culture, or drawing
analogies to entirely different domains. REWARD these when they:
- Do analytical work (the connection illuminates something about the passage)
- Show higher-order thinking (synthesis, evaluation, application)
- Demonstrate genuine engagement with ideas, not just surface topic

Score the thinking, not the topic.
"""
