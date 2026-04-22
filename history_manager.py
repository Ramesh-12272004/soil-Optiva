"""
history_manager.py
Handles saving and retrieving test history per user.
History is stored in history/<email_hash>.json
Each entry contains: test name, timestamp, summary data, conclusion, soil properties.
Graphs are NOT stored (they are BytesIO objects) — only text/numeric results are persisted.
"""

import os
import json
import hashlib
from datetime import datetime
import pandas as pd

HISTORY_DIR = "history"

def _user_file(email: str) -> str:
    h = hashlib.md5(email.encode()).hexdigest()
    os.makedirs(HISTORY_DIR, exist_ok=True)
    return os.path.join(HISTORY_DIR, f"{h}.json")

def load_history(email: str) -> list:
    path = _user_file(email)
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        return json.load(f)

def save_history(email: str, test_name: str, result: dict):
    """
    Persist a test result entry.
    Serialises DataFrames to list-of-dicts; skips BytesIO (graphs/diagrams).
    """
    history = load_history(email)

    entry = {
        "test_name": test_name,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "summary": {}
    }

    for key, value in result.items():
        if isinstance(value, pd.DataFrame):
            entry["summary"][key] = value.round(3).to_dict(orient="records")
        elif isinstance(value, str):
            entry["summary"][key] = value
        elif isinstance(value, (int, float)):
            entry["summary"][key] = value
        # BytesIO (graphs/diagrams) are skipped — they can't be JSON serialised

    history.insert(0, entry)   # newest first
    history = history[:100]    # cap at 100 entries per user

    with open(_user_file(email), "w") as f:
        json.dump(history, f, indent=2)

def clear_history(email: str):
    path = _user_file(email)
    if os.path.exists(path):
        os.remove(path)