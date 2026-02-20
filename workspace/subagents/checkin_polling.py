#!/usr/bin/env python3
"""
Polling Service for Check-in Bot
Continuously checks for user responses and logs them automatically.
"""

import os
import json
import time
import logging
import requests
from datetime import datetime
from pathlib import Path

try:
    from config import (
        TELEGRAM_BOT_TOKEN,
        TELEGRAM_CHAT_ID,
        WORKSPACE_ROOT,
        MEMORY_DIR,
        STATE_FILE,
        LOG_FILE
    )
except ImportError:
    # Fallback configuration
    WORKSPACE_ROOT = Path("/root/.nanobot/workspace")
    MEMORY_DIR = WORKSPACE_ROOT / "memory"
    STATE_FILE = WORKSPACE_ROOT / "subagents" / "checkin_state.json"
    LOG_FILE = WORKSPACE_ROOT / "subagents" / "checkin_bot.log"
    TELEGRAM_BOT_TOKEN = "8430328850:AAHGAF2_DNrj8O6kFTOyplsrLbWXiIwHPYc"
    TELEGRAM_CHAT_ID = "457681374"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("checkin_polling")

class CheckinPollingService:
    def __init__(self):
        self.bot_token = TELEGRAM_BOT_TOKEN
        self.chat_id = TELEGRAM_CHAT_ID
        self.state_file = str(STATE_FILE)
        self.memory_dir = str(MEMORY_DIR)
        self.last_update_id = 0
        
        # Ensure directories exist
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        os.makedirs(self.memory_dir, exist_ok=True)
        
        logger.info(f"Check-in Polling Service initialized for chat {self.chat_id}")
    
    def load_state(self):
        """Load agent state from file."""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading state: {e}")
                return {}
        return {
            "last_checkin_time": None,
            "pending_responses": [],
            "message_history": [],
            "active_checkins": {},
            "last_update_id": 0
        }
    
    def save_state(self, state):
        """Save agent state to file."""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving state: {e}")
    
    def get_updates(self):
        """Get updates from Telegram API."""
        url = f"https://api.telegram.org/bot{self.bot_token}/getUpdates"
        params = {
            "offset": self.last_update_id + 1,
            "timeout": 30,
            "allowed_updates": ["message"]
        }
        
        try:
            response = requests.get(url, params=params, timeout=35)
            if response.status_code == 200:
                data = response.json()
                if data.get("ok"):
                    updates = data.get("result", [])
                    if updates:
                        self.last_update_id = updates[-1]["update_id"]
                    return updates
                else:
                    logger.error(f"Telegram API error: {data}")
            else:
                logger.error(f"HTTP error: {response.status_code}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
        
        return []
    
    def process_message(self, message):
        """Process incoming message."""
        # Only process messages from our chat
        if str(message.get("chat", {}).get("id")) != self.chat_id:
            return False
        
        message_id = message.get("message_id")
        text = message.get("text", "").strip()
        date = message.get("date")
        
        if not text:
            return False
        
        # Check if this is a reply to a check-in message
        reply_to = message.get("reply_to_message")
        if reply_to:
            # This is a reply to a previous message
            original_message_id = reply_to.get("message_id")
            original_text = reply_to.get("text", "")
            
            if "Check-in" in original_text or "check-in" in original_text.lower():
                # This is a check-in response!
                logger.info(f"Check-in response received: {text[:50]}...")
                
                # Load state
                state = self.load_state()
                
                # Find which check-in this belongs to
                checkin_id = None
                for cid, data in state.get("active_checkins", {}).items():
                    if data.get("message_id") == original_message_id:
                        checkin_id = cid
                        break
                
                if checkin_id:
                    # Update the daily note
                    self.log_response(state, checkin_id, text)
                    
                    # Send acknowledgment
                    self.send_acknowledgment(message_id, text)
                    
                    return True
        
        return False
    
    def log_response(self, state, checkin_id, response_text):
        """Log user response to daily note."""
        checkin_data = state["active_checkins"].get(checkin_id)
        if not checkin_data:
            logger.warning(f"No check-in data found for {checkin_id}")
            return False
        
        date_str = checkin_data["date"]
        time_str = checkin_data["time"]
        note_file = os.path.join(self.memory_dir, f"{date_str}.md")
        
        if not os.path.exists(note_file):
            logger.error(f"Daily note not found: {note_file}")
            return False
        
        # Read the file and update the specific check-in
        with open(note_file, 'r') as f:
            lines = f.readlines()
        
        updated = False
        for i, line in enumerate(lines):
            if f"### {time_str} Check-in" in line and f"Message ID: {checkin_data['message_id']}" in line:
                # Find the user response line and update it
                for j in range(i, min(i + 10, len(lines))):
                    if "**User response:**" in lines[j]:
                        lines[j] = f"- **User response:** {response_text}\n"
                        updated = True
                        break
                break
        
        if updated:
            with open(note_file, 'w') as f:
                f.writelines(lines)
            
            # Update state
            state["active_checkins"][checkin_id]["status"] = "responded"
            state["active_checkins"][checkin_id]["response"] = response_text
            state["active_checkins"][checkin_id]["response_time"] = datetime.now().strftime("%H:%M")
            self.save_state(state)
            
            logger.info(f"Logged response for check-in at {time_str}: {response_text[:50]}...")
            return True
        
        logger.warning(f"Could not find check-in entry for update")
        return False
    
    def send_acknowledgment(self, original_message_id, response_text):
        """Send acknowledgment for check-in response."""
        # Truncate if too long
        truncated = response_text[:100] + "..." if len(response_text) > 100 else response_text
        
        message = f"""✅ Check-in response logged!

Your update has been saved to your daily notes.

**Response:** {truncated}

Continue with your work! The next check-in will be in 3 hours."""
        
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "Markdown",
            "reply_to_message_id": original_message_id
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            if response.json().get("ok"):
                logger.info("Acknowledgment sent successfully")
                return True
        except Exception as e:
            logger.error(f"Error sending acknowledgment: {e}")
        
        return False
    
    def run(self):
        """Main polling loop."""
        logger.info("Starting check-in polling service...")
        
        # Load initial state
        state = self.load_state()
        if "last_update_id" in state:
            self.last_update_id = state["last_update_id"]
        
        while True:
            try:
                updates = self.get_updates()
                
                for update in updates:
                    if "message" in update:
                        self.process_message(update["message"])
                
                # Save update ID periodically
                state = self.load_state()
                state["last_update_id"] = self.last_update_id
                self.save_state(state)
                
                # Sleep between polls
                time.sleep(1)
                
            except KeyboardInterrupt:
                logger.info("Polling service stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in polling loop: {e}")
                time.sleep(5)

def main():
    """Main function."""
    print("Starting Check-in Polling Service...")
    print(f"Bot Token: {TELEGRAM_BOT_TOKEN[:10]}...")
    print(f"Chat ID: {TELEGRAM_CHAT_ID}")
    print(f"State file: {STATE_FILE}")
    print(f"Log file: {LOG_FILE}")
    print("\nPress Ctrl+C to stop\n")
    
    service = CheckinPollingService()
    service.run()

if __name__ == "__main__":
    main()