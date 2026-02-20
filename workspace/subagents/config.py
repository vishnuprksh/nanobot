#!/usr/bin/env python3
"""
Configuration for Check-in Bot Subagent
"""

import os
from pathlib import Path

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = "8430328850:AAHGAF2_DNrj8O6kFTOyplsrLbWXiIwHPYc"
TELEGRAM_CHAT_ID = "457681374"  # Your chat ID from the logs

# Paths
WORKSPACE_ROOT = Path("/root/.nanobot/workspace")
MEMORY_DIR = WORKSPACE_ROOT / "memory"
SUBAAGENTS_DIR = WORKSPACE_ROOT / "subagents"
STATE_FILE = SUBAAGENTS_DIR / "checkin_state.json"
LOG_FILE = SUBAAGENTS_DIR / "checkin_bot.log"

# Check-in Schedule (24-hour format)
CHECKIN_TIMES = ["09:00", "12:00", "15:00", "18:00", "21:00"]

# Messages
CHECKIN_PROMPTS = {
    "morning": "🌅 Good morning! What are your top priorities for today?",
    "midday": "☀️ Midday check-in! How's your progress going?",
    "afternoon": "🌇 Afternoon check-in! Any updates or blockers?",
    "evening": "🌙 Evening check-in! What did you accomplish today?",
    "night": "🌃 Final check-in! Any reflections for tomorrow?"
}

# Determine which prompt based on time
def get_checkin_type(hour: int) -> str:
    if 6 <= hour < 10:
        return "morning"
    elif 10 <= hour < 14:
        return "midday"
    elif 14 <= hour < 17:
        return "afternoon"
    elif 17 <= hour < 21:
        return "evening"
    else:
        return "night"

# Ensure directories exist
MEMORY_DIR.mkdir(parents=True, exist_ok=True)
SUBAAGENTS_DIR.mkdir(parents=True, exist_ok=True)