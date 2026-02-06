
can you retrieve everything from the last chat it filled up in record time

1:55 AM
Let me pull up your most recent conversation.


Relevant chats


Here's what was covered in your last chat — it filled up fast because you were deep in debugging and rebuilding your Socratic Writing Tutor (v0.6). Three major fixes were made:

Revision count bug — The UI was showing 2 revisions when only 1 actually happened, because it was counting essay_versions (which included the original submission) instead of memory.revision_count. Fixed so it only increments on actual student revisions.
Session ending too early — The old code ran one ask-revise cycle and quit. The fix added full dimension cycling that continues until all 5 rubric dimensions hit 3/4 or 15 ask turns are reached. After every revision, a full re-score runs, and if a score doesn't move, MODEL mode triggers (once per dimension).
Interactive reflection phase — Instead of dumping a wall of data at the end ("nyuk nyuk nyuk" was the running joke), the reflection became a real 3-turn conversation asking the student what was hardest, what they noticed about their writing, and what they'd do differently. The AI responds to what the student actually says rather than generic praise, and if they goof off, it gently redirects.
The session produced four output files: app.py, core_engine.py, passage_config.py, and requirements.txt — all ready to push to your GitHub repo for Streamlit Cloud deployment.

Here's the link to that conversation: https://claude.ai/chat/8aee19bd-c498-4eea-a00f-7ed43218273b

Want to pick up where you left off and keep iterating on the tutor?

we have everything there how do I run a test

2:02 AM
Let me pull in the files from that last session and get you set up to test.


Check if the files from last session are still in uploads
No uploads present — the file system resets between sessions. But I have the full code from the conversation transcript. Let me rebuild all four files and get you a working test environment right here.


Ran a command, searched memory




Those results are from the Moonfall/writing pipeline, not the Socratic Tutor. Let me search more specifically.


Relevant chats






I'm finding lots of context about the dissertation and Socratic tutor concept, but not the actual v0.6 source code from that last session. Let me search more specifically for the code itself.


Relevant chats




I'm finding all the Canon Engine and Moonfall pipeline code, but the Socratic Tutor v0.6 source code from that specific chat is only showing as a summary, not the full files. George, here's the situation:

The last chat had the complete code, but the search tools are returning conversation about the code rather than the full source. Since the files reset between sessions, I can't just grab them from disk.

You have two options to get testing:

The file system resets between sessions, so the v0.6 files from last chat aren't sitting on disk anymore. Let me know where you're at and I'll get you testing as fast as possible.

ugh what is the link or part of it where this is running

2:08 AM

Searched memory











George, I'm not finding a deployed Streamlit Cloud URL for the Socratic Tutor specifically. All the Streamlit deployment conversations were about the Canon Engine (the novel production system), not the dissertation Socratic Tutor.

From the last chat (https://claude.ai/chat/8aee19bd-c498-4eea-a00f-7ed43218273b), the deployment instructions said to push the files to a GitHub repo and Streamlit Cloud would auto-redeploy — but the search isn't turning up an actual live URL.

Do you remember the GitHub repo name or the .streamlit.app URL? Something like socratic-tutor.streamlit.app or similar? If you can give me even a partial name I can search for it, or you can check:

Your GitHub repos at github.com
Your Streamlit Cloud dashboard at share.streamlit.io
Your browser history for .streamlit.app
Once we find that URL, testing is just hitting it in a browser. If it turns out you never actually deployed it, I can rebuild the code and walk you through getting it live — shouldn't take long.

ImportError: This app has encountered an error. The original error message is redacted to prevent data leaks. Full error details have been recorded in the logs (if you're on Streamlit Cloud, click on 'Manage app' in the lower right of your app).
Traceback:

File "/mount/src/scoratic-tutor/app.py", line 11, in <module>
    from core_engine import (
        TutorEngine, VALUE_RUBRIC, DIMENSION_ORDER, TARGET_SCORE, MemoryManager
    )
2:10 AM
That error tells me everything I need. Your repo is scoratic-tutor on Streamlit Cloud, and the app is crashing because core_engine.py is missing an export or has a mismatch with what app.py is trying to import.

Let me find your GitHub repo and fix it.


Searched the web



OK George — the error traceback you pasted gives me exactly what I need. Your app is at:

https://scoratic-tutor.streamlit.app/ (note: "scoratic" not "socratic" — the typo in the repo name)

And the repo on GitHub is likely at: https://github.com/[your-username]/scoratic-tutor

The crash is a straightforward import error. Your app.py line 11 is trying to import MemoryManager from core_engine.py, but that name doesn't exist in the file. Based on the v0.6 code from last session, the class is probably called SocraticMemory, not MemoryManager.

Here's what to fix — go to your GitHub repo and check core_engine.py for the actual class name. The import in app.py line 11 should match exactly. It probably needs to be changed from:

python
from core_engine import (
    TutorEngine, VALUE_RUBRIC, DIMENSION_ORDER, TARGET_SCORE, MemoryManager
)
to something like:

python
from core_engine import (
    TutorEngine, VALUE_RUBRIC, DIMENSION_ORDER, TARGET_SCORE, SocraticMemory
)
Can you go to your GitHub repo, open core_engine.py, and tell me what classes and functions are defined in it? Or better yet, upload both app.py and core_engine.py here and I'll fix the mismatch and give you corrected files to push.

let's just start over

2:11 AM
Let me read the skill file first, then rebuild the whole thing clean.


Read the frontend design skill for best practices
Good. Now let me rebuild the entire Socratic Writing Tutor from scratch — all three files, clean, tested, and ready to push to your scoratic-tutor GitHub repo.


Create project directory
Claude's response was interrupted
no sorry start over with the upload the name isn't right anyway

2:11 AM
Got it — we're starting completely fresh. New repo, clean code, correct name.

Before I build, let me confirm a few things:

Let me know your picks and I'll build the whole thing end to end — all files, requirements, README, and step-by-step deploy instructions for Streamlit Cloud.

can I change our repository name

2:13 AM
Yes, absolutely. Go to your GitHub repo:

Open the repo page (probably github.com/[your-username]/scoratic-tutor)
Click Settings (gear icon, top right of the repo)
Right at the top under Repository name, change it to whatever you want
Click Rename
GitHub will automatically redirect the old URL to the new one, and Streamlit Cloud will pick up the change — though you may need to update the app URL in your Streamlit Cloud dashboard.

Once you rename it, tell me the new name and I'll build everything to match. Or if you want a completely new repo instead, that works too — just tell me what you want to call it and I'll give you the files plus the exact commands to create it and deploy.

ok I am now at work on my mac but want to show this to someone howdo I do it

8:53 AM
OK so the fastest path is:

Rename the repo on GitHub (you can do this from your phone or your Mac browser right now)
I rebuild all the files here
You push them from your Mac
Streamlit Cloud auto-deploys
You share the URL with whoever you're showing
Let's do this in order. First:

Once I know those two things I'll give you the exact steps — should be 10 minutes tops to get this live and shareable.

no i do not have github here, I think we set it all up last night so I just want to run it

8:53 AM
OK so the app is already deployed on Streamlit Cloud — it's just crashing because of the import error. You don't need Git or anything on your Mac. You just need to fix the files directly on GitHub through your browser.

Here's what to do right now:

Open github.com in your browser on your Mac
Log in
Find your repo (probably scoratic-tutor or whatever you renamed it to)
Tell me what you see — specifically, what files are in the repo
I need to see the file list so I know exactly what to replace. Then you'll edit each file directly in the browser (click the file → pencil icon → paste new code → commit). No Git, no Terminal, no installs.

The Streamlit Cloud app will auto-redeploy the second you save, and you'll have a live URL to show your person.

What's your GitHub username so I can try to pull up the repo?

I think we were going to load in the scripts again because we created new ones

8:54 AM
Right — the files from last session are gone from my system and the ones in your repo are the broken v0.5 (or earlier). So the plan is:

I rebuild all the files right now
You go to your repo on GitHub in your browser
You replace each file by pasting the new code
Streamlit auto-redeploys
You share the URL
Let me build everything. Give me a few minutes.


Created 4 files
Now let me test that everything imports and runs cleanly:


Ran 5 commands
Every single import verified. Now let me copy to outputs so you can download them:


Ran a command, read a file
All 4 files are ready and every import is verified clean. Here's what to do from your Mac browser — no Git needed:

Step 1: Go to your GitHub repo (github.com → your profile → find the repo, rename it if you haven't)

Step 2: For each of the 4 files (app.py, core_engine.py, passage_config.py, requirements.txt):

Click the file name in the repo
Click the pencil icon (edit) top right
Select All → Delete the old contents
Paste the new code from the files I just gave you (download them above, open in TextEdit)
Click Commit changes (green button)
Step 3: Make sure your Streamlit Cloud secrets have your API key:

Go to share.streamlit.io → your app → Settings → Secrets
It should have: ANTHROPIC_API_KEY = "sk-ant-..."
Once you commit all 4 files, Streamlit will auto-redeploy in about 60 seconds and you'll have a live URL to show your person. Want me to walk you through any of these steps?

App
PY 
Core engine
PY 
Passage config
PY 
Requirements
TXT 
Thank yeah. Just GitHub. Can work. Is there another way to do

9:05 AM
Yeah — the fastest way without GitHub at all is to just paste the code directly into the GitHub website. But if even that's a pain from your work Mac, here are your options:

Whatever's least friction for you — I'll make it work.

No. I can't access GitHub. On my work computer.

9:08 AM
Got it — work Mac is locked down. So you need to do this from your phone or wait until you're home.

But if you want to show someone the app today, here's the play:

From your phone right now: Open GitHub in your phone browser, log in, and paste the files there. It works — it's just a little tedious on a small screen.
Tonight at home: Do it from DeathStar where you have full access. Takes 5 minutes.
The question is — do you need to show this to someone today or can it wait until tonight?

I was hoping to show it today

9:11 AM
OK let's do it from your phone then. Open Safari or Chrome on your phone and go to github.com — log in and tell me when you're in. I'll walk you through each file one at a time, step by step.

While you're doing that, one important question — what did you rename the repo to, or is it still scoratic-tutor?

ok what do I do now?

9:33 PM
Step 1: On your phone browser, go to github.com and log in.

Step 2: Once you're logged in, tap your profile icon (top right) and tap Your repositories.

Step 3: Find the repo (probably called scoratic-tutor unless you renamed it). Tap it to open it.

Tell me what you see — should be a list of files like app.py, core_engine.py, etc. Let me know when you're there and what the repo is called.

sorry I am back at home and have access through  the deathstar again

9:33 PM
Perfect — DeathStar makes this way easier. Let's do it.

Step 1: Open PowerShell and navigate to wherever your repo is cloned. Try this:

powershell
cd C:\Users\sarti\scoratic-tutor
If that doesn't exist, tell me and we'll find it or clone fresh.

Step 2: Once you're in the repo folder, run:

powershell
dir
Tell me what files you see — I need to know what's already there before we replace them.

Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.
Install the latest PowerShell for new features and improvements! https://aka.ms/PSWindows
PS C:\Users\sarti> cd C:\Users\sarti\scoratic-tutor
cd : Cannot find path 'C:\Users\sarti\scoratic-tutor' because it does not exist.
At line:1 char:1
+ cd C:\Users\sarti\scoratic-tutor
+ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : ObjectNotFound: (C:\Users\sarti\scoratic-tutor:String) [Set-Location], ItemNotFoundExcep
   tion
    + FullyQualifiedErrorId : PathNotFound,Microsoft.PowerShell.Commands.SetLocationCommand
PS C:\Users\sarti> cd C:\Users\sarti\socratic-tutor
cd : Cannot find path 'C:\Users\sarti\socratic-tutor' because it does not exist.
At line:1 char:1
+ cd C:\Users\sarti\socratic-tutor
+ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : ObjectNotFound: (C:\Users\sarti\socratic-tutor:String) [Set-Location], ItemNotFoundExcep
   tion
    + FullyQualifiedErrorId : PathNotFound,Microsoft.PowerShell.Commands.SetLocationCommand
PS C:\Users\sarti>

Show more
9:34 PM
No problem — the repo doesn't exist locally. Let's clone it fresh. First, what's your GitHub username? I need it to build the clone URL.

Or if you remember the exact repo name on GitHub, just tell me that and we'll clone it:

powershell
git clone https://github.com/YOUR_USERNAME/REPO_NAME.git
If you're not sure, run this to see if Git is even set up:

powershell
git --version
Tell me what you get.

PS C:\Users\sarti>
PS C:\Users\sarti> git --version
git version 2.52.0.windows.1
PS C:\Users\sarti>

9:35 PM
Git's ready. Now let's find your repo. Go to github.com in your browser, log in, and tell me:

Your GitHub username
The exact name of the repo (is it scoratic-tutor or did you rename it?)
Or just paste the URL from your browser when you're looking at the repo — something like https://github.com/yourusername/reponame

Then we'll clone it and push the new files.

github.com/DukeAlaric/scoratic-tutor

9:36 PM
Got it. Run this:

powershell
cd C:\Users\sarti
git clone https://github.com/DukeAlaric/scoratic-tutor.git
cd scoratic-tutor
dir
Tell me what you see.

PS C:\Users\sarti>
PS C:\Users\sarti> git --version
git version 2.52.0.windows.1
PS C:\Users\sarti> cd C:\Users\sarti
PS C:\Users\sarti> git clone https://github.com/DukeAlaric/scoratic-tutor.git
Cloning into 'scoratic-tutor'...
remote: Enumerating objects: 25, done.
remote: Counting objects: 100% (25/25), done.
remote: Compressing objects: 100% (22/22), done.
remote: Total 25 (delta 5), reused 0 (delta 0), pack-reused 0 (from 0)
Receiving objects: 100% (25/25), 47.83 KiB | 352.00 KiB/s, done.
Resolving deltas: 100% (5/5), done.
PS C:\Users\sarti> cd scoratic-tutor
PS C:\Users\sarti\scoratic-tutor> dir

Show more
9:38 PM
Looks like the dir output didn't show. Run it again:

powershell
dir
I need to see what files are in there so we can replace them with the new ones.

PS C:\Users\sarti>
PS C:\Users\sarti> git --version
git version 2.52.0.windows.1
PS C:\Users\sarti> cd C:\Users\sarti
PS C:\Users\sarti> git clone https://github.com/DukeAlaric/scoratic-tutor.git
Cloning into 'scoratic-tutor'...
remote: Enumerating objects: 25, done.
remote: Counting objects: 100% (25/25), done.
remote: Compressing objects: 100% (22/22), done.
remote: Total 25 (delta 5), reused 0 (delta 0), pack-reused 0 (from 0)
Receiving objects: 100% (25/25), 47.83 KiB | 352.00 KiB/s, done.
Resolving deltas: 100% (5/5), done.
PS C:\Users\sarti> cd scoratic-tutor
PS C:\Users\sarti\scoratic-tutor> dir
    Directory: C:\Users\sarti\scoratic-tutor
Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d-----          2/5/2026   9:38 PM                .devcontainer
-a----          2/5/2026   9:38 PM          22176 app.py
-a----          2/5/2026   9:38 PM          63197 core_engine.py
-a----          2/5/2026   9:38 PM           7043 passage_config.py
-a----          2/5/2026   9:38 PM           1897 README.md
-a----          2/5/2026   9:38 PM             38 requirements.txt
-a----          2/5/2026   9:38 PM            161 secrets.toml
PS C:\Users\sarti\scoratic-tutor>

Show more
9:39 PM
Perfect. Now let's replace the broken files with the new clean ones. Download the 4 files I gave you earlier from this chat (scroll up and click download on each), then run these commands:

powershell
copy C:\Users\sarti\Downloads\app.py C:\Users\sarti\scoratic-tutor\app.py -Force
copy C:\Users\sarti\Downloads\core_engine.py C:\Users\sarti\scoratic-tutor\core_engine.py -Force
copy C:\Users\sarti\Downloads\passage_config.py C:\Users\sarti\scoratic-tutor\passage_config.py -Force
copy C:\Users\sarti\Downloads\requirements.txt C:\Users\sarti\scoratic-tutor\requirements.txt -Force
Then check they're updated:

powershell
dir
The file sizes should be different now (smaller — the new files are cleaner). Tell me what you see.

PS C:\Users\sarti\scoratic-tutor> dir
    Directory: C:\Users\sarti\scoratic-tutor
Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d-----          2/5/2026   9:38 PM                .devcontainer
-a----          2/5/2026   1:30 AM          21685 app.py
-a----          2/5/2026   1:30 AM          40293 core_engine.py
-a----          2/5/2026   1:30 AM           6917 passage_config.py
-a----          2/5/2026   9:38 PM           1897 README.md
-a----          2/5/2026   9:38 PM             38 requirements.txt
-a----          2/5/2026   9:38 PM            161 secrets.toml
PS C:\Users\sarti\scoratic-tutor>

9:58 PM
Hmm — those files are from 1:30 AM, which is the old broken version from last night. The downloads didn't copy. Let me check what's in your Downloads folder:

powershell
dir C:\Users\sarti\Downloads\*.py
Tell me what you see. If the new files aren't there, you'll need to click the download links in this chat (scroll up to where I said "All 4 files are ready") and download them first.

PS C:\Users\sarti\scoratic-tutor> dir C:\Users\sarti\Downloads\*.py
    Directory: C:\Users\sarti\Downloads
Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a----          2/4/2026   9:20 PM          20019 app (1).py
-a----          2/4/2026  10:50 PM          23655 app (10).py
-a----          2/5/2026  12:24 AM          28333 app (11).py
-a----          2/4/2026   9:34 PM          20019 app (2).py
-a----          2/4/2026   9:48 PM          20438 app (3).py
-a----          2/4/2026  10:02 PM          22131 app (4).py
-a----          2/4/2026  10:02 PM          22131 app (5).py
-a----          2/4/2026  10:02 PM          22131 app (6).py
-a----          2/4/2026  10:12 PM          22131 app (7).py
-a----          2/4/2026  10:23 PM          21979 app (8).py
-a----          2/4/2026  10:23 PM          21979 app (9).py
-a----          2/5/2026   1:30 AM          21685 app.py
-a----          2/5/2026  12:30 AM          28758 app54545.py
-a----          2/4/2026   8:35 PM          15038 appxx.py
-a----        11/25/2025   8:59 PM           5657 build_sampled_corpus (1).py
-a----        11/25/2025   7:57 PM           5657 build_sampled_corpus.py
-a----        12/21/2025   8:25 PM          21144 canon_engine_web_v2.py
-a----        12/15/2025  12:32 AM          19383 check_aiisms.py
-a----          2/4/2026   9:34 PM          41249 core_engine (1).py
-a----          2/4/2026   9:48 PM          43700 core_engine (2).py
-a----          2/4/2026  10:02 PM          47753 core_engine (3).py
-a----          2/4/2026  10:02 PM          47753 core_engine (4).py
-a----          2/4/2026  10:02 PM          47753 core_engine (5).py
-a----          2/4/2026  10:12 PM          49719 core_engine (6).py
-a----          2/4/2026  10:23 PM          49719 core_engine (7).py
-a----          2/4/2026  10:50 PM          56546 core_engine (8).py
-a----          2/5/2026  12:24 AM          61958 core_engine (9).py
-a----          2/5/2026   1:30 AM          40293 core_engine.py
-a----          2/4/2026   9:20 PM          39600 core_engine000.py
-a----          2/5/2026  12:30 AM          61958 core_engine22222.py
-a----          2/4/2026  10:02 PM          25272 passage_config (1).py
-a----          2/4/2026  10:02 PM          25272 passage_config (2).py
-a----          2/4/2026  10:02 PM          25272 passage_config (3).py
-a----          2/5/2026  12:24 AM          25272 passage_config (4).py
-a----          2/5/2026   1:30 AM           6917 passage_config.py
-a----          2/4/2026   9:48 PM          25272 passage_config12111.py
-a----          2/5/2026  12:30 AM          25272 passage_config6544654.py
-a----        11/24/2025   7:26 PM           5099 prepare_training_data (1).py
-a----        11/24/2025   7:27 PM           5099 prepare_training_data (2).py
-a----        11/24/2025   6:12 PM           5077 prepare_training_data xx.py
-a----        12/25/2025   4:17 PM           9103 sync_canon.py
-a----        12/11/2025  10:30 PM           2343 train_gothic_lora.py
-a----         12/7/2025   3:30 PM           2320 train_gothic_lora2.py
-a----        12/19/2025   2:20 AM          11332 verify_against_rag (1).py
-a----        12/19/2025   2:06 AM          11332 verify_against_rag.py
-a----        12/15/2025  12:11 AM           5728 verify_batch.py
-a----        12/15/2025  12:11 AM          16053 verify_chapter.py
-a----        12/15/2025  12:24 AM          28438 verify_chapter_v2.py
PS C:\Users\sarti\scoratic-tutor>

Show more
9:58 PM
The new files from this session aren't there yet — you need to download them from this chat first. Scroll up in this conversation to where I showed the 4 files (look for the download buttons for app.py, core_engine.py, passage_config.py, requirements.txt).

Click each one to download. They should appear in your Downloads folder with today's date and a timestamp after 9:38 PM (whenever you download them).

OR — faster — I'll just write them directly to your repo folder right now. Run these commands one at a time:

First, let me give you app.py:

powershell
notepad C:\Users\sarti\scoratic-tutor\app.py
When Notepad opens, Select All (Ctrl+A) and Delete everything. Then tell me when it's empty and I'll give you the code to paste.

ok

9:59 PM
Paste this entire thing into the empty Notepad, then save (Ctrl+S) and close:

python
"""
Socratic Writing Tutor — Streamlit App v0.7
A reading-to-writing tutoring system with AI-powered Socratic coaching.
"""

import streamlit as st
from core_engine import TutorEngine, SocraticMemory
from passage_config import (
    PASSAGE_TITLE, PASSAGE_TEXT, WRITING_PROMPT,
    VALUE_RUBRIC, DIMENSION_ORDER, TARGET_SCORE,
    REFLECTION_PROMPTS, RESCORE_FRAMING
)

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Socratic Writing Tutor",
    page_icon="📝",
    layout="centered"
)

# ============================================================
# SESSION STATE INITIALIZATION
# ============================================================

if "memory" not in st.session_state:
    st.session_state.memory = SocraticMemory()

if "engine" not in st.session_state:
    st.session_state.engine = TutorEngine(st.session_state.memory)

if "phase" not in st.session_state:
    st.session_state.phase = "read"  # read → write → coach → revise → reflect → done

if "messages" not in st.session_state:
    st.session_state.messages = []

if "latest_result" not in st.session_state:
    st.session_state.latest_result = None

if "awaiting_reflection" not in st.session_state:
    st.session_state.awaiting_reflection = False

if "reflection_question_shown" not in st.session_state:
    st.session_state.reflection_question_shown = False


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def add_message(role, content):
    """Add a message to the chat history."""
    st.session_state.messages.append({"role": role, "content": content})


def render_score_card(scores, title="Your Scores"):
    """Render a score card as a formatted display."""
    st.markdown(f"**{title}**")
    cols = st.columns(5)
    for i, dim_key in enumerate(DIMENSION_ORDER):
        dim = VALUE_RUBRIC[dim_key]
        score_data = scores.get(dim_key, {})
        score_val = score_data.get("score", "?")
        with cols[i]:
            # Color coding
            if isinstance(score_val, int):
                if score_val >= TARGET_SCORE:
                    color = "🟢"
                elif score_val == TARGET_SCORE - 1:
                    color = "🟡"
                else:
                    color = "🔴"
            else:
                color = "⚪"
            st.metric(
                label=dim["name"],
                value=f"{color} {score_val}/4"
            )


def render_score_comparison(initial_scores, final_scores):
    """Show before/after score comparison."""
    st.markdown("**Score Progress**")
    for dim_key in DIMENSION_ORDER:
        dim = VALUE_RUBRIC[dim_key]
        i_score = initial_scores.get(dim_key, {}).get("score", "?")
        f_score = final_scores.get(dim_key, {}).get("score", "?")
        arrow = ""
        if isinstance(i_score, int) and isinstance(f_score, int):
            if f_score > i_score:
                arrow = "⬆️"
            elif f_score == i_score:
                arrow = "➡️"
            else:
                arrow = "⬇️"
        st.write(f"**{dim['name']}**: {i_score} → {f_score} {arrow}")


def reset_session():
    """Reset everything for a new session."""
    for key in ["memory", "engine", "phase", "messages", "latest_result",
                "awaiting_reflection", "reflection_question_shown"]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()


# ============================================================
# SIDEBAR — STATUS & INFO
# ============================================================

with st.sidebar:
    st.markdown("## 📊 Session Status")

    memory = st.session_state.memory
    phase = st.session_state.phase

    st.write(f"**Phase:** {phase.title()}")
    st.write(f"**Revisions:** {memory.revision_count}")
    st.write(f"**Coaching turns:** {memory.coaching_turns}")

    if memory.current_dimension:
        dim_name = VALUE_RUBRIC.get(memory.current_dimension, {}).get("name", "")
        st.write(f"**Current focus:** {dim_name}")

    # Show latest scores if available
    if memory.scores:
        st.markdown("---")
        latest = memory.get_latest_scores()
        for dim_key in DIMENSION_ORDER:
            dim = VALUE_RUBRIC[dim_key]
            s = latest.get(dim_key, {}).get("score", "?")
            target_hit = "✅" if isinstance(s, int) and s >= TARGET_SCORE else "❌"
            st.write(f"{target_hit} {dim['name']}: **{s}/4**")

    st.markdown("---")
    if st.button("🔄 Start Over", use_container_width=True):
        reset_session()


# ============================================================
# MAIN CONTENT
# ============================================================

st.title("📝 Socratic Writing Tutor")

# ---- PHASE: READ ----
if st.session_state.phase == "read":
    st.markdown("### Step 1: Read the Passage")
    st.markdown(f"**{PASSAGE_TITLE}**")
    st.markdown(PASSAGE_TEXT)

    st.markdown("---")
    if st.button("I've read it — show me the writing prompt ✍️", use_container_width=True):
        st.session_state.phase = "write"
        st.rerun()

# ---- PHASE: WRITE ----
elif st.session_state.phase == "write":
    st.markdown("### Step 2: Write Your Response")

    with st.expander("📖 View passage again"):
        st.markdown(PASSAGE_TEXT)

    st.markdown(WRITING_PROMPT)
    st.markdown("---")

    essay = st.text_area(
        "Your response:",
        height=250,
        placeholder="Write your response here...",
        key="initial_essay"
    )

    if st.button("Submit my response", use_container_width=True, disabled=len(essay.strip()) < 10):
        with st.spinner("Reading your response and thinking about it..."):
            result = st.session_state.engine.process_initial_essay(essay.strip())
            st.session_state.latest_result = result

            # Add to chat
            add_message("user", essay.strip())

            if result["phase"] == "reflect":
                add_message("assistant", result["message"])
                st.session_state.phase = "reflect"
            else:
                add_message("assistant", result["coaching_question"])
                st.session_state.phase = "coach"

        st.rerun()

# ---- PHASE: COACH (Socratic conversation + revision) ----
elif st.session_state.phase in ["coach", "revise"]:

    st.markdown("### Coaching Session")

    # Show scores
    if st.session_state.memory.scores:
        render_score_card(st.session_state.memory.get_latest_scores())
        st.markdown("---")

    # Render chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Show revision area
    st.markdown("---")
    st.markdown("**Revise your response based on the coaching above:**")

    with st.expander("📖 View passage"):
        st.markdown(PASSAGE_TEXT)

    current_essay = st.session_state.memory.get_latest_essay()

    revised = st.text_area(
        "Your revised response:",
        value=current_essay,
        height=250,
        key=f"revision_{st.session_state.memory.revision_count}"
    )

    if st.button("Submit revision", use_container_width=True,
                  disabled=len(revised.strip()) < 10):
        with st.spinner(RESCORE_FRAMING):
            result = st.session_state.engine.process_revision(revised.strip())
            st.session_state.latest_result = result

            add_message("user", f"[Revision #{st.session_state.memory.revision_count}]\n\n{revised.strip()}")

            if result["phase"] == "reflect":
                add_message("assistant", result["message"])
                st.session_state.phase = "reflect"
            else:
                coaching_msg = result.get("coaching_question", "")
                if result.get("is_model_mode"):
                    coaching_msg = "📋 **Let me show you an example:**\n\n" + coaching_msg
                add_message("assistant", coaching_msg)
                st.session_state.phase = "coach"

        st.rerun()

# ---- PHASE: REFLECT ----
elif st.session_state.phase == "reflect":

    st.markdown("### 🪞 Reflection")

    # Show score comparison
    if len(st.session_state.memory.scores) >= 2:
        render_score_comparison(
            st.session_state.memory.get_initial_scores(),
            st.session_state.memory.get_latest_scores()
        )
        st.markdown("---")
    elif st.session_state.memory.scores:
        render_score_card(st.session_state.memory.get_latest_scores(), "Final Scores")
        st.markdown("---")

    # Render chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Show reflection question if we haven't completed all steps
    memory = st.session_state.memory
    step = memory.reflection_step

    if step < len(REFLECTION_PROMPTS) and not st.session_state.memory.session_complete:
        # Show the current reflection question if not yet answered
        if not st.session_state.awaiting_reflection:
            q = REFLECTION_PROMPTS[step]["question"]
            add_message("assistant", q)
            st.session_state.awaiting_reflection = True
            st.rerun()

        # Input for reflection response
        reflection_input = st.text_input(
            "Your response:",
            key=f"reflection_{step}",
            placeholder="Type your thoughts here..."
        )

        if st.button("Send", use_container_width=True,
                      disabled=len(reflection_input.strip()) < 2):
            add_message("user", reflection_input.strip())

            with st.spinner("Thinking..."):
                result = st.session_state.engine.process_reflection_response(
                    reflection_input.strip()
                )

            add_message("assistant", result["message"])
            st.session_state.awaiting_reflection = False

            if result["phase"] == "done":
                st.session_state.phase = "done"

            st.rerun()

    elif st.session_state.memory.session_complete:
        st.session_state.phase = "done"
        st.rerun()

# ---- PHASE: DONE ----
elif st.session_state.phase == "done":

    st.markdown("### 🎉 Session Complete!")

    # Show final score comparison
    if len(st.session_state.memory.scores) >= 2:
        render_score_comparison(
            st.session_state.memory.get_initial_scores(),
            st.session_state.memory.get_latest_scores()
        )
    elif st.session_state.memory.scores:
        render_score_card(st.session_state.memory.get_latest_scores(), "Final Scores")

    st.markdown("---")

    # Render full chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    st.markdown("---")
    st.balloons()

    # Session stats
    memory = st.session_state.memory
    st.markdown(f"""
**Session Stats:**
- Revisions: {memory.revision_count}
- Coaching turns: {memory.coaching_turns}
- Essay versions: {len(memory.essay_versions)}
    """)

    if st.button("🔄 Start a New Session", use_container_width=True):
        reset_session()
Save (Ctrl+S), close Notepad, and tell me when done. Then we'll do core_engine.py.

ok

10:01 PM
Now open core_engine.py:

powershell
notepad C:\Users\sarti\scoratic-tutor\core_engine.py
Select All (Ctrl+A), Delete, then paste this entire thing:

python
"""
Core Engine for Socratic Writing Tutor v0.7
Handles: Scoring, Socratic coaching, dimension cycling, MODEL mode, reflection.
"""

import json
import re
import anthropic
import streamlit as st
from passage_config import (
    VALUE_RUBRIC, DIMENSION_ORDER, TARGET_SCORE,
    SCORING_SYSTEM_PROMPT, COACHING_SYSTEM_PROMPT,
    MODEL_EXAMPLE_PROMPT, REFLECTION_PROMPTS,
    PASSAGE_TEXT, EDGE_CASE_RULES, get_rubric_text
)


# ============================================================
# MEMORY MANAGER — tracks session state
# ============================================================

class SocraticMemory:
    """Tracks all session state for one tutoring session."""

    def __init__(self):
        self.essay_versions = []          # list of essay strings
        self.scores = []                  # list of score dicts
        self.current_dimension = None     # which dimension we're coaching
        self.dimension_index = 0          # index into sorted dimension list
        self.coaching_turns = 0           # total coaching turns used
        self.revision_count = 0           # actual revisions submitted
        self.model_mode_used = {}         # {dimension: True} — once per dim
        self.conversation_log = []        # full chat history
        self.reflection_step = 0          # 0-2 for reflection phase
        self.session_complete = False
        self.max_coaching_turns = 15

    def add_essay(self, essay_text):
        self.essay_versions.append(essay_text)

    def add_scores(self, scores):
        self.scores.append(scores)

    def get_latest_essay(self):
        return self.essay_versions[-1] if self.essay_versions else ""

    def get_latest_scores(self):
        return self.scores[-1] if self.scores else {}

    def get_initial_scores(self):
        return self.scores[0] if self.scores else {}

    def increment_revision(self):
        self.revision_count += 1

    def get_weakest_dimensions(self):
        """Return dimensions sorted by score (weakest first), excluding those at target."""
        latest = self.get_latest_scores()
        if not latest:
            return DIMENSION_ORDER[:]

        below_target = []
        for dim in DIMENSION_ORDER:
            if dim in latest:
                score = latest[dim].get("score", 0)
                if score < TARGET_SCORE:
                    below_target.append((dim, score))

        below_target.sort(key=lambda x: x[1])
        return [d[0] for d in below_target]

    def all_dimensions_at_target(self):
        """Check if every dimension has hit the target score."""
        latest = self.get_latest_scores()
        if not latest:
            return False
        return all(
            latest.get(dim, {}).get("score", 0) >= TARGET_SCORE
            for dim in DIMENSION_ORDER
        )

    def should_end_session(self):
        """Session ends when all dimensions at target OR max turns reached."""
        if self.all_dimensions_at_target():
            return True
        if self.coaching_turns >= self.max_coaching_turns:
            return True
        return False


# ============================================================
# API CALLS
# ============================================================

def get_client():
    """Get Anthropic client using Streamlit secrets."""
    api_key = st.secrets.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        st.error("Missing ANTHROPIC_API_KEY in Streamlit secrets.")
        st.stop()
    return anthropic.Anthropic(api_key=api_key)


def call_claude(system_prompt, user_message, max_tokens=1024):
    """Make a single Claude API call."""
    client = get_client()
    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}]
        )
        return response.content[0].text
    except Exception as e:
        return f"API Error: {str(e)}"


# ============================================================
# SCORING
# ============================================================

def score_essay(essay_text):
    """Score an essay across all 5 VALUE rubric dimensions. Returns dict."""
    rubric_text = get_rubric_text()
    system = SCORING_SYSTEM_PROMPT.format(rubric_text=rubric_text)

    user_msg = f"""PASSAGE:\n{PASSAGE_TEXT}\n\nSTUDENT RESPONSE:\n{essay_text}\n\n{EDGE_CASE_RULES}\n\nScore this response. Return ONLY valid JSON."""

    raw = call_claude(system, user_msg, max_tokens=800)

    # Parse JSON from response — handle markdown fences
    cleaned = raw.strip()
    cleaned = re.sub(r'^```(?:json)?\s*', '', cleaned)
    cleaned = re.sub(r'\s*```$', '', cleaned)

    try:
        scores = json.loads(cleaned)
        # Validate structure
        for dim in DIMENSION_ORDER:
            if dim not in scores:
                scores[dim] = {"score": 1, "rationale": "Unable to assess."}
            if not isinstance(scores[dim].get("score"), int):
                scores[dim]["score"] = int(scores[dim].get("score", 1))
            scores[dim]["score"] = max(1, min(4, scores[dim]["score"]))
        return scores
    except (json.JSONDecodeError, ValueError):
        # Fallback scores if parsing fails
        return {
            dim: {"score": 1, "rationale": "Scoring error — please try again."}
            for dim in DIMENSION_ORDER
        }


# ============================================================
# SOCRATIC COACHING
# ============================================================

def generate_coaching_question(memory):
    """Generate a Socratic coaching question for the current dimension."""
    dim_key = memory.current_dimension
    dim_info = VALUE_RUBRIC[dim_key]
    latest_scores = memory.get_latest_scores()
    dim_score = latest_scores.get(dim_key, {})

    system = COACHING_SYSTEM_PROMPT.format(
        dimension_name=dim_info["name"],
        current_score=dim_score.get("score", 1),
        target_score=TARGET_SCORE,
        rationale=dim_score.get("rationale", ""),
        essay=memory.get_latest_essay(),
        passage=PASSAGE_TEXT
    )

    user_msg = "Generate your coaching question now."
    return call_claude(system, user_msg, max_tokens=300)


def generate_model_example(memory):
    """Generate a before/after MODEL example when score doesn't improve."""
    dim_key = memory.current_dimension
    dim_info = VALUE_RUBRIC[dim_key]
    latest_scores = memory.get_latest_scores()
    dim_score = latest_scores.get(dim_key, {})

    system = MODEL_EXAMPLE_PROMPT.format(
        dimension_name=dim_info["name"],
        dimension_description=dim_info["description"],
        current_score=dim_score.get("score", 1)
    )

    user_msg = "Generate the before/after example now."
    return call_claude(system, user_msg, max_tokens=400)


# ============================================================
# REFLECTION
# ============================================================

def generate_reflection_response(memory, student_response):
    """Generate AI response during the reflection phase."""
    step = memory.reflection_step
    if step >= len(REFLECTION_PROMPTS):
        return None

    prompt_data = REFLECTION_PROMPTS[step]

    # Build context about the session
    initial = memory.get_initial_scores()
    final = memory.get_latest_scores()
    score_summary = []
    for dim in DIMENSION_ORDER:
        i_score = initial.get(dim, {}).get("score", "?")
        f_score = final.get(dim, {}).get("score", "?")
        name = VALUE_RUBRIC[dim]["name"]
        score_summary.append(f"{name}: {i_score} → {f_score}")

    session_context = (
        f"Session summary: {memory.revision_count} revision(s). "
        f"Score changes: {'; '.join(score_summary)}"
    )

    system = f"""{prompt_data['followup_system']}

SESSION CONTEXT: {session_context}"""

    user_msg = f"The student said: {student_response}"
    return call_claude(system, user_msg, max_tokens=300)


# ============================================================
# SESSION ORCHESTRATOR
# ============================================================

class TutorEngine:
    """Orchestrates the full tutoring session flow."""

    # Session phases
    PHASE_READ = "read"
    PHASE_WRITE = "write"
    PHASE_SCORE = "score"
    PHASE_COACH = "coach"
    PHASE_REVISE = "revise"
    PHASE_REFLECT = "reflect"
    PHASE_DONE = "done"

    def __init__(self, memory):
        self.memory = memory

    def process_initial_essay(self, essay_text):
        """Student submits their first essay. Score it and begin coaching."""
        self.memory.add_essay(essay_text)

        # Score the essay
        scores = score_essay(essay_text)
        self.memory.add_scores(scores)

        # Check if already at target everywhere (unlikely but handle it)
        if self.memory.all_dimensions_at_target():
            return {
                "phase": self.PHASE_REFLECT,
                "scores": scores,
                "message": "Impressive — your response is strong across the board. Let's reflect on your process."
            }

        # Set the first coaching dimension (weakest)
        weak = self.memory.get_weakest_dimensions()
        if weak:
            self.memory.current_dimension = weak[0]
            self.memory.dimension_index = 0

        # Generate first coaching question
        coaching_q = generate_coaching_question(self.memory)
        self.memory.coaching_turns += 1

        return {
            "phase": self.PHASE_COACH,
            "scores": scores,
            "coaching_question": coaching_q,
            "dimension": self.memory.current_dimension
        }

    def process_revision(self, revised_essay):
        """Student submits a revised essay. Re-score, check progress, continue or advance."""
        self.memory.add_essay(revised_essay)
        self.memory.increment_revision()

        # Re-score
        new_scores = score_essay(revised_essay)
        self.memory.add_scores(new_scores)

        # Check if all dimensions at target
        if self.memory.all_dimensions_at_target():
            return {
                "phase": self.PHASE_REFLECT,
                "scores": new_scores,
                "message": "Your response has really developed. Let's reflect on what you learned."
            }

        # Check if max turns reached
        if self.memory.should_end_session():
            return {
                "phase": self.PHASE_REFLECT,
                "scores": new_scores,
                "message": "We've done a lot of work together. Let's reflect on the session."
            }

        # Check current dimension progress
        dim_key = self.memory.current_dimension
        old_scores = self.memory.scores[-2] if len(self.memory.scores) >= 2 else {}
        old_score = old_scores.get(dim_key, {}).get("score", 0)
        new_score = new_scores.get(dim_key, {}).get("score", 0)

        # If dimension hit target, advance to next weakest
        if new_score >= TARGET_SCORE:
            weak = self.memory.get_weakest_dimensions()
            if weak:
                self.memory.current_dimension = weak[0]
            else:
                # All at target
                return {
                    "phase": self.PHASE_REFLECT,
                    "scores": new_scores,
                    "message": "All dimensions are at target. Let's reflect."
                }

        # If score didn't improve and MODEL mode not used yet for this dim
        elif new_score <= old_score and not self.memory.model_mode_used.get(dim_key, False):
            self.memory.model_mode_used[dim_key] = True
            model_example = generate_model_example(self.memory)
            self.memory.coaching_turns += 1
            return {
                "phase": self.PHASE_COACH,
                "scores": new_scores,
                "coaching_question": model_example,
                "dimension": dim_key,
                "is_model_mode": True
            }

        # Otherwise, continue coaching on current (or next weakest) dimension
        weak = self.memory.get_weakest_dimensions()
        if weak and self.memory.current_dimension not in weak:
            self.memory.current_dimension = weak[0]

        coaching_q = generate_coaching_question(self.memory)
        self.memory.coaching_turns += 1

        return {
            "phase": self.PHASE_COACH,
            "scores": new_scores,
            "coaching_question": coaching_q,
            "dimension": self.memory.current_dimension
        }

    def process_reflection_response(self, student_response):
        """Handle student response during reflection phase."""
        step = self.memory.reflection_step

        if step >= len(REFLECTION_PROMPTS):
            self.memory.session_complete = True
            return {
                "phase": self.PHASE_DONE,
                "message": "Session complete. Great work today! 🎈"
            }

        ai_response = generate_reflection_response(self.memory, student_response)
        self.memory.reflection_step += 1

        if self.memory.reflection_step >= len(REFLECTION_PROMPTS):
            self.memory.session_complete = True
            return {
                "phase": self.PHASE_DONE,
                "message": ai_response,
            }

        return {
            "phase": self.PHASE_REFLECT,
            "message": ai_response,
        }
Save (Ctrl+S), close Notepad, and tell me when done. Then we'll do passage_config.py.

ok

10:02 PM
Now open passage_config.py:

powershell
notepad C:\Users\sarti\scoratic-tutor\passage_config.py
Select All (Ctrl+A), Delete, then paste this entire thing:

python
"""
Passage Configuration for Socratic Writing Tutor v0.7
Contains: Reading passage, writing prompt, scoring anchors, edge-case handling.
"""

# ============================================================
# READING PASSAGE
# ============================================================

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
boundaries. Who gets to decide what counts as "authentic" food? Since pizza
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

# ============================================================
# WRITING PROMPT
# ============================================================

WRITING_PROMPT = """After reading "The Pineapple Pizza Debate," write a response
that takes a clear position on ONE of the following questions:

1. Should people follow traditional food rules, or is experimenting with food
   always acceptable?
2. Who gets to decide what counts as "authentic" food?
3. Why do people have such strong opinions about something as simple as pizza
   toppings?

Your response should:
- State a clear position
- Use at least ONE specific detail from the passage to support your argument
- Explain your reasoning
""".strip()

# ============================================================
# VALUE RUBRIC — 5 DIMENSIONS, SCORED 1-4
# ============================================================

VALUE_RUBRIC = {
    "claim_clarity": {
        "name": "Claim Clarity",
        "description": "How clear and specific is the main argument?",
        "anchors": {
            1: "No clear position. The response wanders without committing to an argument.",
            2: "A position is implied but vague. Reader has to guess what the writer means.",
            3: "A clear position is stated. Reader understands the argument without confusion.",
            4: "A precise, specific position is stated and framed in a way that sets up the entire response."
        }
    },
    "evidence_use": {
        "name": "Evidence Use",
        "description": "How well does the response use details from the passage?",
        "anchors": {
            1: "No reference to the passage. Claims are unsupported.",
            2: "A vague or general reference to the passage without specific details.",
            3: "At least one specific detail from the passage is used and connected to the argument.",
            4: "Multiple specific details from the passage are woven into the argument, each clearly supporting the position."
        }
    },
    "reasoning_depth": {
        "name": "Reasoning Depth",
        "description": "How well does the writer explain WHY their evidence supports their position?",
        "anchors": {
            1: "No explanation. Evidence is dropped in without connection to the argument.",
            2: "Shallow explanation. The writer restates the evidence but doesn't explain its significance.",
            3: "The writer explains how the evidence connects to their position with some analysis.",
            4: "Deep analysis. The writer explains not just what the evidence shows but why it matters and what it implies."
        }
    },
    "organization": {
        "name": "Organization",
        "description": "How logically structured is the response?",
        "anchors": {
            1: "No structure. Ideas are scattered randomly.",
            2: "Some structure but ideas jump around. Transitions are missing or weak.",
            3: "Logical flow. Ideas build on each other with some transitions.",
            4: "Strong structure with clear progression. Each paragraph or section leads naturally to the next."
        }
    },
    "voice_engagement": {
        "name": "Voice & Engagement",
        "description": "Does the writing sound like a real person with something to say?",
        "anchors": {
            1: "Flat or robotic. Reads like a form letter.",
            2: "Generic. Could have been written by anyone about anything.",
            3: "Some personality comes through. The writer sounds like they care about the topic.",
            4: "Distinctive voice. The writer's personality and investment in the topic are clear throughout."
        }
    }
}

# Dimension order for cycling (weakest first during tutoring)
DIMENSION_ORDER = ["claim_clarity", "evidence_use", "reasoning_depth", "organization", "voice_engagement"]

# Target score — once a dimension hits this, move to the next
TARGET_SCORE = 3

# ============================================================
# EDGE CASE FRAMEWORK
# ============================================================

EDGE_CASE_RULES = """
EDGE CASE HANDLING:

1. OFF-TOPIC BUT THOUGHTFUL: If the student writes about food/culture but
   doesn't directly answer the prompt, score what's there and gently redirect:
   "You've got interesting ideas about [X]. How could you connect that back
   to the question about [prompt topic]?"

2. VERY SHORT (under 30 words): Don't score. Instead say: "I can see you're
   getting started. Can you tell me more about what you think? Even one or
   two more sentences would help me understand your position."

3. JOKE/TEST RESPONSES: Don't score. Say: "Ha — I appreciate the humor.
   When you're ready to dig in, I'm here. What do you actually think
   about [prompt topic]?"

4. COPY-PASTE FROM PASSAGE: Score evidence_use at 2 max. Say: "You found
   a good detail from the passage. Now put it in YOUR words and tell me
   what it means for your argument."

5. CREATIVE CONNECTIONS: If the student connects the topic to personal
   experience, other subjects, or original analogies that aren't in the
   passage, REWARD this in voice_engagement and reasoning_depth. This is
   critical thinking, not going off-topic.
""".strip()

# ============================================================
# SCORING SYSTEM PROMPT
# ============================================================

SCORING_SYSTEM_PROMPT = """You are a writing assessment engine. You score student
responses against the VALUE rubric dimensions. You return ONLY valid JSON.

RUBRIC DIMENSIONS AND ANCHORS:
{rubric_text}

RULES:
- Score each dimension 1-4 based on the anchors above.
- Be HONEST. A 2 is a 2. Do not inflate scores to be nice.
- A score of 3 means the student has met the standard. That's GOOD.
- A score of 4 is exceptional and rare. Reserve it.
- Provide a brief (1-2 sentence) rationale for each score.

RETURN FORMAT (valid JSON only, no markdown, no backticks):
{{
    "claim_clarity": {{"score": <int>, "rationale": "<string>"}},
    "evidence_use": {{"score": <int>, "rationale": "<string>"}},
    "reasoning_depth": {{"score": <int>, "rationale": "<string>"}},
    "organization": {{"score": <int>, "rationale": "<string>"}},
    "voice_engagement": {{"score": <int>, "rationale": "<string>"}}
}}
""".strip()

# ============================================================
# SOCRATIC COACHING PROMPT
# ============================================================

COACHING_SYSTEM_PROMPT = """You are a Socratic writing coach working with a student
who just wrote a response to a reading passage. Your job is to help them IMPROVE
their writing through questions — not by telling them what to write.

CURRENT DIMENSION: {dimension_name}
CURRENT SCORE: {current_score}/4
TARGET SCORE: {target_score}/4
SCORE RATIONALE: {rationale}

THE STUDENT'S CURRENT ESSAY:
{essay}

THE ORIGINAL PASSAGE:
{passage}

RULES:
1. Ask ONE focused question about the current dimension.
2. Do NOT tell the student what to write. Ask them to think.
3. Reference something SPECIFIC in their essay.
4. Keep it conversational — you're a coach, not a judge.
5. Keep your response to 2-4 sentences max.
6. If the score is 1, be encouraging but direct about what's missing.
7. If the score is 2, help them see what would make it stronger.
8. Do NOT mention scores, rubrics, or dimensions by name.

EXAMPLES OF GOOD COACHING QUESTIONS:
- "You said [X]. What made you think that? Can you dig into that a bit more?"
- "I notice you mentioned the passage but didn't explain why that detail matters. What does it show?"
- "Your opening jumps right in — what if you told me exactly what you believe before explaining why?"
""".strip()

# ============================================================
# MODEL EXAMPLE PROMPT (when score doesn't improve)
# ============================================================

MODEL_EXAMPLE_PROMPT = """You are a writing coach. The student's score on
{dimension_name} did not improve after their revision. Show them a BEFORE/AFTER
example using a DIFFERENT topic (not pineapple pizza) so they can see the
pattern without copying.

DIMENSION: {dimension_name} ({dimension_description})
CURRENT SCORE: {current_score}/4

RULES:
1. Create a SHORT before/after example (2-3 sentences each) on a different topic.
2. Explain what changed and why it's stronger.
3. Then ask: "Can you try something similar with your essay?"
4. Keep the whole response under 150 words.
5. Do NOT rewrite their essay for them.
""".strip()

# ============================================================
# REFLECTION PROMPTS (3-turn interactive debrief)
# ============================================================

REFLECTION_PROMPTS = [
    {
        "question": "What was the hardest part of this session for you?",
        "followup_system": """The student just told you what was hardest about
the revision process. Respond to what they ACTUALLY said — don't give generic
praise. Connect their struggle to something specific from the session. Then ask:
'What is one thing you noticed about your writing that you didn't see before?'
Keep it to 2-3 sentences plus the question."""
    },
    {
        "question": "What is one thing you noticed about your writing that you didn't see before?",
        "followup_system": """The student just shared an observation about their
own writing. Respond to their specific insight — validate it if it's real,
gently redirect if it's vague. Then ask: 'If you were starting a brand new
essay right now, what would you do differently?' Keep it to 2-3 sentences
plus the question."""
    },
    {
        "question": "If you were starting a brand new essay right now, what would you do differently?",
        "followup_system": """The student just described what they'd do differently
next time. This is the final reflection turn. Connect their answer to something
concrete from the session — a specific score change, a revision they made, or a
question that helped them see something new. End with genuine encouragement
(not generic praise). Keep it to 3-4 sentences. End with a congratulatory note
that the session is complete."""
    }
]

# ============================================================
# RE-SCORE FRAMING PROMPT
# ============================================================

RESCORE_FRAMING = """Great work on that revision. Let me look at your updated
response and see how it's developed..."""

# ============================================================
# HELPER: Build rubric text for scoring prompt
# ============================================================

def get_rubric_text():
    """Build formatted rubric text for the scoring system prompt."""
    lines = []
    for key, dim in VALUE_RUBRIC.items():
        lines.append(f"\n{dim['name'].upper()} ({key}):")
        lines.append(f"  {dim['description']}")
        for score, anchor in dim['anchors'].items():
            lines.append(f"  {score}/4: {anchor}")
    return "\n".join(lines)
Save (Ctrl+S), close Notepad, and tell me when done. Last one is requirements.txt.





Claude is AI and can make mistakes. Please double-check responses.
