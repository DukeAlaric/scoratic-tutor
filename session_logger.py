"""
Session Logger for Socratic Writing Tutor
Automatically logs session data to Google Sheets for dissertation research.

Setup:
1. Create a Google Cloud project and enable Google Sheets API
2. Create a service account and download the JSON credentials
3. Share your Google Sheet with the service account email
4. Add the credentials JSON to Streamlit secrets as [gcp_service_account]
"""

import json
import uuid
from datetime import datetime

import streamlit as st

# Google Sheets imports - graceful fallback if not configured
try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSHEETS_AVAILABLE = True
except ImportError:
    GSHEETS_AVAILABLE = False


def get_session_id() -> str:
    """Get or create a unique session ID."""
    if 'session_id' not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())[:8]
    return st.session_state.session_id


def get_gsheets_connection():
    """Connect to Google Sheets using Streamlit secrets."""
    if not GSHEETS_AVAILABLE:
        return None
    
    try:
        creds_dict = st.secrets.get("gcp_service_account", None)
        if not creds_dict:
            return None
        
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = Credentials.from_service_account_info(dict(creds_dict), scopes=scopes)
        client = gspread.authorize(creds)
        
        sheet_url = st.secrets.get("sheets", {}).get("spreadsheet_url", None)
        if sheet_url:
            return client.open_by_url(sheet_url)
        
        sheet_name = st.secrets.get("sheets", {}).get("spreadsheet_name", "Socratic Tutor Sessions")
        return client.open(sheet_name)
    except Exception as e:
        # Silently fail — don't break the app if logging fails
        return None


def ensure_worksheet(spreadsheet, name: str, headers: list):
    """Get or create a worksheet with the given headers."""
    try:
        ws = spreadsheet.worksheet(name)
    except gspread.WorksheetNotFound:
        ws = spreadsheet.add_worksheet(title=name, rows=1000, cols=len(headers))
        ws.append_row(headers)
    return ws


def log_phase_transition(phase: str, engine, extra_data: dict = None):
    """Log a phase transition to Google Sheets. Called every time the phase changes."""
    session_id = get_session_id()
    timestamp = datetime.now().isoformat()
    
    spreadsheet = get_gsheets_connection()
    if not spreadsheet:
        return  # Logging not configured, skip silently
    
    try:
        # === SESSION LOG worksheet — one row per phase transition ===
        session_ws = ensure_worksheet(spreadsheet, "Session Log", [
            "Session ID", "Timestamp", "Phase", "Essay Version #",
            "Essay Text", "Scores JSON", "Coaching Message",
            "Reflection Q", "Reflection A", "Extra"
        ])
        
        # Build the row
        essay_num = len(engine.memory.essays)
        latest_essay = engine.memory.get_latest_essay() if engine.memory.essays else ""
        
        scores_json = ""
        if engine.memory.scores_history:
            latest_scores = engine.memory.get_latest_scores()
            scores_json = json.dumps({
                dim: {"score": data.get("score", 0), "rationale": data.get("rationale", "")}
                for dim, data in latest_scores.items()
            })
        
        coaching_msg = engine.memory.coaching_history[-1] if engine.memory.coaching_history else ""
        
        reflection_q = ""
        reflection_a = ""
        if engine.memory.reflection_responses:
            from passage_config import REFLECTION_PROMPTS
            idx = len(engine.memory.reflection_responses) - 1
            if idx < len(REFLECTION_PROMPTS):
                reflection_q = REFLECTION_PROMPTS[idx]["question"]
            reflection_a = engine.memory.reflection_responses[-1]
        
        extra = json.dumps(extra_data) if extra_data else ""
        
        session_ws.append_row([
            session_id, timestamp, phase, essay_num,
            latest_essay[:5000],  # Truncate to stay within cell limits
            scores_json, coaching_msg[:5000],
            reflection_q, reflection_a[:2000], extra
        ])
        
    except Exception:
        pass  # Never break the app due to logging failure


def log_complete_session(engine):
    """Log the full session summary when complete. One row per session."""
    session_id = get_session_id()
    timestamp = datetime.now().isoformat()
    
    spreadsheet = get_gsheets_connection()
    if not spreadsheet:
        return
    
    try:
        summary_ws = ensure_worksheet(spreadsheet, "Session Summary", [
            "Session ID", "Completed At", "Total Revisions", "Coaching Turns",
            "Essay Versions", "Reflection Turns",
            "Initial Essay", "Final Essay",
            "Initial Scores", "Final Scores",
            "All Reflections JSON", "All Scores JSON",
            "Session Complete"
        ])
        
        stats = engine.get_session_stats()
        
        initial_essay = engine.memory.essays[0] if engine.memory.essays else ""
        final_essay = engine.memory.get_latest_essay()
        
        initial_scores = ""
        final_scores = ""
        all_scores = []
        if engine.memory.scores_history:
            initial_scores = json.dumps({
                dim: data.get("score", 0) 
                for dim, data in engine.memory.scores_history[0].items()
            })
            final_scores = json.dumps({
                dim: data.get("score", 0) 
                for dim, data in engine.memory.get_latest_scores().items()
            })
            for i, scores in enumerate(engine.memory.scores_history):
                all_scores.append({
                    "version": i + 1,
                    "scores": {dim: data.get("score", 0) for dim, data in scores.items()}
                })
        
        # Build reflection pairs
        from passage_config import REFLECTION_PROMPTS
        reflections = []
        for i, resp in enumerate(engine.memory.reflection_responses):
            q = REFLECTION_PROMPTS[i]["question"] if i < len(REFLECTION_PROMPTS) else f"Q{i+1}"
            reflections.append({"question": q, "response": resp})
        
        summary_ws.append_row([
            session_id, timestamp, stats["revisions"], stats["coaching_turns"],
            stats["essay_versions"], stats["reflection_turns"],
            initial_essay[:5000], final_essay[:5000],
            initial_scores, final_scores,
            json.dumps(reflections), json.dumps(all_scores),
            "YES"
        ])
        
    except Exception:
        pass


def build_export_json(engine) -> str:
    """Build a complete session export as JSON string for local download."""
    from passage_config import REFLECTION_PROMPTS
    
    session_data = {
        "session_id": get_session_id(),
        "export_timestamp": datetime.now().isoformat(),
        "session_stats": engine.get_session_stats(),
        "essays": [],
        "scores_history": [],
        "coaching_history": engine.memory.coaching_history,
        "reflection_responses": [],
        "messages": []
    }
    
    for i, essay in enumerate(engine.memory.essays):
        session_data["essays"].append({
            "version": i + 1,
            "type": "initial" if i == 0 else f"revision_{i}",
            "text": essay
        })
    
    for i, scores in enumerate(engine.memory.scores_history):
        score_entry = {"version": i + 1}
        for dim, data in scores.items():
            score_entry[dim] = {
                "score": data.get("score", 0),
                "rationale": data.get("rationale", "")
            }
        session_data["scores_history"].append(score_entry)
    
    for i, resp in enumerate(engine.memory.reflection_responses):
        session_data["reflection_responses"].append({
            "question": REFLECTION_PROMPTS[i]["question"] if i < len(REFLECTION_PROMPTS) else f"Q{i+1}",
            "response": resp
        })
    
    return json.dumps(session_data, indent=2, default=str)
