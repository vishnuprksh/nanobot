#!/usr/bin/env python3
"""
Check-in Agent: Handles automated check-ins and user responses via Telegram.
This runs as a background subagent.
"""

import os
import json
import time
import logging
import requests
from datetime import datetime
from pathlib import Path

# Import configuration
try:
    from config import (
        TELEGRAM_BOT_TOKEN, 
        TELEGRAM_CHAT_ID,
        WORKSPACE_ROOT,
        MEMORY_DIR,
        STATE_FILE,
        CHECKIN_TIMES,
        CHECKIN_PROMPTS,
        get_checkin_type
    )
except ImportError:
    # Fallback configuration
    WORKSPACE_ROOT = Path("/root/.nanobot/workspace")
    MEMORY_DIR = WORKSPACE_ROOT / "memory"
    STATE_FILE = WORKSPACE_ROOT / "subagents" / "checkin_state.json"
    TELEGRAM_BOT_TOKEN = "8430328850:AAHGAF2_DNrj8O6kFTOyplsrLbWXiIwHPYc"
    TELEGRAM_CHAT_ID = "457681374"
    CHECKIN_TIMES = ["09:00", "12:00", "15:00", "18:00", "21:00"]
    
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

# Setup logging

# Setup logging
LOG_FILE = str(WORKSPACE_ROOT / "subagents" / "checkin_agent.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("checkin_agent")

class CheckinAgent:
    def __init__(self):
        self.state_file = str(STATE_FILE)
        self.memory_dir = str(MEMORY_DIR)
        self.bot_token = TELEGRAM_BOT_TOKEN
        self.chat_id = TELEGRAM_CHAT_ID
        
        # Ensure directories exist
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        os.makedirs(self.memory_dir, exist_ok=True)
        
        # Load or initialize state
        self.state = self.load_state()
        
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
            "active_checkins": {}
        }
    
    def save_state(self):
        """Save agent state to file."""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.state, f, indent=2)
            logger.debug("State saved successfully")
        except Exception as e:
            logger.error(f"Error saving state: {e}")
    
    def send_checkin(self, custom_message=None):
        """Send a check-in message via Telegram."""
        current_time = datetime.now().strftime("%H:%M")
        current_hour = datetime.now().hour
        date_str = datetime.now().strftime("%Y-%m-%d")
        
        # Get check-in type based on time
        checkin_type = get_checkin_type(current_hour)
        
        if custom_message:
            message = f"📋 {custom_message}\n\nTime: {current_time}"
        else:
            # Use appropriate prompt based on time of day
            base_prompt = CHECKIN_PROMPTS.get(checkin_type, "📋 Check-in time!")
            message = f"""{base_prompt}

⏰ Time: {current_time}

**What have you accomplished since last check-in?**
**What's next on your list?**

Reply to this message and I'll log your response automatically!"""

        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            payload = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "Markdown"
            }
            
            response = requests.post(url, json=payload, timeout=10)
            response_data = response.json()
            
            if response_data.get("ok"):
                message_id = response_data["result"]["message_id"]
                logger.info(f"Check-in sent successfully. Message ID: {message_id}")
                
                # Save to state
                checkin_id = f"{date_str}_{current_time.replace(':', '')}"
                self.state["active_checkins"][checkin_id] = {
                    "message_id": message_id,
                    "time": current_time,
                    "date": date_str,
                    "status": "sent",
                    "response": None
                }
                
                # Update daily note
                self.update_daily_note(date_str, current_time, message_id)
                
                self.save_state()
                return True, message_id
            else:
                logger.error(f"Failed to send message: {response_data}")
                return False, None
                
        except Exception as e:
            logger.error(f"Error sending check-in: {e}")
            return False, None
    
    def update_daily_note(self, date_str, time_str, message_id):
        """Update the daily note file with check-in entry."""
        note_file = os.path.join(self.memory_dir, f"{date_str}.md")
        
        # Create file if it doesn't exist
        if not os.path.exists(note_file):
            with open(note_file, 'w') as f:
                f.write(f"# {date_str}\n\n")
                f.write("## Check-ins\n\n")
        
        # Add check-in entry
        with open(note_file, 'a') as f:
            f.write(f"### {time_str} Check-in (Message ID: {message_id})\n")
            f.write(f"- **Question sent at:** {time_str}\n")
            f.write(f"- **User response:** [Awaiting reply]\n")
            f.write(f"- **Progress:** \n")
            f.write(f"- **Next actions:** \n\n")
        
        logger.info(f"Updated daily note: {note_file}")
    
    def log_response(self, message_id, response_text):
        """Log user response to daily note."""
        # Find the check-in by message_id
        checkin_id = None
        checkin_data = None
        
        for cid, data in self.state.get("active_checkins", {}).items():
            if data.get("message_id") == message_id:
                checkin_id = cid
                checkin_data = data
                break
        
        if not checkin_id:
            logger.warning(f"No check-in found for message ID: {message_id}")
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
            if f"### {time_str} Check-in (Message ID: {message_id})" in line:
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
            self.state["active_checkins"][checkin_id]["status"] = "responded"
            self.state["active_checkins"][checkin_id]["response"] = response_text
            self.save_state()
            
            logger.info(f"Logged response for check-in at {time_str}")
            return True
        
        logger.warning(f"Could not find check-in entry for update")
        return False
    
    def get_updates(self):
        """Get updates from Telegram (webhook or polling)."""
        # This would be called by a webhook or polling mechanism
        # For now, returns pending responses
        pending = self.state.get("pending_responses", [])
        self.state["pending_responses"] = []
        self.save_state()
        return pending
    
    def run_scheduled_checkin(self):
        """Run a scheduled check-in (called by cron)."""
        logger.info("Running scheduled check-in")
        success, message_id = self.send_checkin()
        
        if success:
            logger.info(f"Scheduled check-in completed. Message ID: {message_id}")
        else:
            logger.error("Failed to send scheduled check-in")
        
        return success

def main():
    """Main function with command line arguments."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Check-in Agent")
    parser.add_argument("--scheduled", action="store_true", help="Run scheduled check-in")
    parser.add_argument("--test", action="store_true", help="Test the agent")
    parser.add_argument("--message", type=str, help="Custom check-in message")
    
    args = parser.parse_args()
    
    agent = CheckinAgent()
    
    if args.scheduled:
        logger.info("Running scheduled check-in via command line")
        success, message_id = agent.send_checkin()
        
        if success:
            print(f"✓ Scheduled check-in sent. Message ID: {message_id}")
            logger.info(f"Scheduled check-in completed. Message ID: {message_id}")
        else:
            print("✗ Failed to send scheduled check-in")
            logger.error("Failed to send scheduled check-in")
            
    elif args.message:
        success, message_id = agent.send_checkin(args.message)
        
        if success:
            print(f"✓ Custom check-in sent. Message ID: {message_id}")
            logger.info(f"Custom check-in sent. Message ID: {message_id}")
        else:
            print("✗ Failed to send custom check-in")
            logger.error("Failed to send custom check-in")
            
    else:  # Default test mode
        print("Testing check-in agent...")
        success, message_id = agent.send_checkin()
        
        if success:
            print(f"✓ Check-in sent successfully! Message ID: {message_id}")
            print(f"✓ State saved to: {agent.state_file}")
            print(f"✓ Daily note updated")
        else:
            print("✗ Failed to send check-in")
            print("Please check:")
            print("1. Is CHECKIN_BOT_TOKEN set correctly?")
            print("2. Is the bot token valid?")
            print("3. Is the chat ID correct?")

if __name__ == "__main__":
    main()