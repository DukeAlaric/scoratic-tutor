# 🏛️ Socratic Writing Tutor

**AI-powered writing assessment with Socratic dialogue — because a score without a conversation is just a number.**

## What This Is

A Streamlit application that combines rubric-based writing assessment with Socratic tutoring. Unlike scoring-only systems that return grades and corrections, this tool uses AI to engage students in guided questioning about their weakest writing dimension, developing metacognition and self-assessment capacity.

## How It Works

1. **Write** — Student responds to an argumentative essay prompt
2. **Assess** — AI scores the essay against the AAC&U VALUE Written Communication Rubric (5 dimensions, 4 levels)
3. **Dialogue** — AI enters Socratic dialogue targeting the weakest dimension (asks questions, never gives answers)
4. **Reflect** — Student articulates what they discovered and plans specific revisions

## The Differentiator

| | Scoring-Only Systems | Socratic Tutor |
|---|---|---|
| **Process** | Submit → Score → Corrections | Submit → Score → Guided Dialogue |
| **Output** | "Your thesis scored 2/4. Fix it." | "What were you trying to accomplish here?" |
| **Theory** | Behaviorist (stimulus/response) | Constructivist (knowledge through inquiry) |
| **Student learns** | WHAT is wrong | WHY and how to think differently |

## Rubric

**AAC&U VALUE Written Communication Rubric** — Open Educational Resource  
Used by 2,000+ institutions nationally. Five dimensions:
- Context & Purpose
- Content Development
- Genre & Disciplinary Conventions
- Sources & Evidence
- Syntax & Mechanics

Source: [AAC&U VALUE Rubrics](https://www.aacu.org/value/rubrics/value-rubrics-written-communication)

## Setup

### Quick Start (Demo Mode)
```bash
pip install -r requirements.txt
streamlit run app.py
```
Demo mode uses pre-written Socratic questions. No API key needed.

### Live Mode (Claude API)
```bash
export ANTHROPIC_API_KEY=your_key_here
pip install -r requirements.txt
streamlit run app.py
```
Or enter your API key in the sidebar after launching.

### Deploy to Replit
1. Create new Replit project (Python)
2. Upload `app.py` and `requirements.txt`
3. Set `ANTHROPIC_API_KEY` in Replit Secrets
4. Run command: `streamlit run app.py --server.port 8080 --server.address 0.0.0.0`

## Research Context

- **Bloom's 2-Sigma Problem (1984)**: One-on-one tutoring produces 2 standard deviation improvement
- **Google LearnLM (2024)**: AI Socratic tutoring works at scale, but gap exists in interpretive domains
- **Research Question**: Can practitioner-built AI Socratic tutoring tools produce measurable writing improvement in adult learners?

## Dissertation Instrument

This tool is designed as a research instrument for doctoral dissertation work at American College of Education. The pre/post study design:

1. **Pre-test**: Student writes essay, scored against VALUE rubric
2. **Intervention**: 3-5 Socratic tutoring sessions over 4 weeks
3. **Post-test**: Student writes new essay, scored against VALUE rubric
4. **Analysis**: Compare pre/post scores + qualitative analysis of dialogue transcripts

All session data exports as JSON for analysis.

## License & IP

- **Code**: MIT License
- **Rubric**: AAC&U VALUE Rubrics (Open Educational Resource)
- **Essay Prompt**: Original (free for educational use)
- **No institutional IP** was used in the creation of this tool

## Author

George Sartiano  
Ed.D. Candidate, Instructional Technology  
American College of Education
