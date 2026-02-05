# Socratic Writing Tutor v0.5

AI-powered writing instruction using Socratic dialogue, live revision, and modeling — built for doctoral research at American College of Education.

## What it does

Students read a short passage, write an analytical response, and then work with an AI tutor that:

1. **Assesses** their writing across 5 dimensions (AAC&U VALUE rubric)
2. **Asks** Socratic questions to help them see what could improve
3. **Models** a before/after example when they are stuck (shows, does not tell)
4. **Prompts revision** and re-scores the full essay after every edit
5. **Cycles** through all dimensions until each hits the target score

## Quick Start (Streamlit Cloud)

1. Fork this repo
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account
4. Select this repo, branch `main`, file `app.py`
5. In **Advanced Settings**, add your secret:
   ```
   ANTHROPIC_API_KEY = "sk-ant-your-key-here"
   ```
6. Click **Deploy**

Your app will be live at `https://your-app-name.streamlit.app`

## Files

| File | Purpose |
|------|---------|
| `app.py` | Streamlit UI |
| `core_engine.py` | Tutor engine — assessment, dialogue, scaffolding, modeling |
| `passage_config.py` | Reading passage, writing prompt, scoring anchors |
| `requirements.txt` | Python dependencies |

## Architecture

```
Read passage -> Write response -> Assess (5 dimensions)
    |
ASK: Socratic question about weakest dimension
    |
Student responds -> REVISE: edit essay
    |
Full re-score -> score moved? -> next dimension or next question
    |
Score stuck? -> MODEL: show before/after example -> REVISE again
    |
All dimensions at target -> REFLECT: session complete
```

## License

- Code: MIT
- AAC&U VALUE Rubric: Open Educational Resource (OER)
- Reading passage: Original work, free for educational use
