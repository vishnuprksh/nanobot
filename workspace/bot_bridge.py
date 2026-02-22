#!/usr/bin/env python3
"""
Telegram Bot Bridge
Connects vpk_assistant_bot to nanobot with assistant personality context
"""

import os
import sys
import json
import logging
import requests
from datetime import datetime
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Bot configurations
ASSISTANT_BOT_TOKEN = "8430328850:AAHGAF2_DNrj8O6kFTOyplsrLbWXiIwHPYc"  # vpk_assistant_bot
NANOBOT_BOT_TOKEN = "8275254305:AAEtsrH0DQAbL5uwha9uHu-0N3TkIGFcgpA"  # dreams_nanobot
USER_CHAT_ID = "457681374"

class BotBridge:
    def __init__(self):
        self.last_update_id = 0
        self.message_context = {}  # Store context for threaded conversations
        
    def get_assistant_updates(self):
        """Get new messages from assistant bot"""
        url = f"https://api.telegram.org/bot{ASSISTANT_BOT_TOKEN}/getUpdates"
        params = {
            "offset": self.last_update_id + 1,
            "timeout": 30
        }
        
        try:
            response = requests.get(url, params=params, timeout=35)
            if response.status_code == 200:
                data = response.json()
                if data.get("ok") and data.get("result"):
                    return data["result"]
        except Exception as e:
            logger.error(f"Error getting updates from assistant bot: {e}")
        return []
    
    def send_via_nanobot(self, text: str, is_reply: bool = False, original_message: dict = None):
        """Send message through nanobot (main AI bot)"""
        url = f"https://api.telegram.org/bot{NANOBOT_BOT_TOKEN}/sendMessage"
        
        # Add context prefix if it's a reply from assistant bot
        if is_reply and original_message:
            # Extract user's message text
            user_msg = original_message.get("text", "")
            
            # Create context-aware prompt
            context_text = f"🔧 [Assistant Bot Context]\n"
            context_text += f"User message via Assistant Bot: '{user_msg}'\n"
            context_text += f"Please respond as a task-focused productivity assistant.\n"
            context_text += f"Be concise, structured, and focused on tasks/check-ins.\n"
            context_text += f"Response:\n{text}"
            
            final_text = context_text
        else:
            final_text = text
        
        data = {
            "chat_id": USER_CHAT_ID,
            "text": final_text,
            "parse_mode": "Markdown"
        }
        
        try:
            response = requests.post(url, json=data)
            if response.status_code == 200:
                logger.info("Message forwarded via nanobot")
                return True
            else:
                logger.error(f"Failed to forward message: {response.text}")
        except Exception as e:
            logger.error(f"Error forwarding message: {e}")
        return False
    
    def send_via_assistant(self, text: str):
        """Send message directly via assistant bot"""
        url = f"https://api.telegram.org/bot{ASSISTANT_BOT_TOKEN}/sendMessage"
        
        # Style for assistant bot
        styled_text = f"🤖 {text}"
        
        data = {
            "chat_id": USER_CHAT_ID,
            "text": styled_text,
            "parse_mode": "Markdown"
        }
        
        try:
            response = requests.post(url, json=data)
            if response.status_code == 200:
                logger.info("Message sent via assistant bot")
                return True
            else:
                logger.error(f"Failed to send via assistant: {response.text}")
        except Exception as e:
            logger.error(f"Error sending via assistant: {e}")
        return False
    
    def process_assistant_message(self, update: dict):
        """Process message from assistant bot"""
        message = update.get("message", {})
        chat_id = str(message.get("chat", {}).get("id"))
        user_message = message.get("text", "").strip()
        
        if not user_message:
            return
        
        # Update last update ID
        self.last_update_id = update["update_id"]
        
        logger.info(f"Assistant bot message: {user_message[:100]}")
        
        # Check if this is a reply to a check-in
        is_checkin_reply = self._is_checkin_reply(user_message)
        
        if is_checkin_reply:
            # Process check-in reply
            self._handle_checkin_reply(user_message, message)
        else:
            # Forward to nanobot with assistant context
            self._forward_to_nanobot(user_message, message)
    
    def _is_checkin_reply(self, message: str) -> bool:
        """Check if this is a reply to a check-in message"""
        checkin_keywords = ["accomplish", "working on", "next", "progress", "task", "done"]
        message_lower = message.lower()
        
        # Simple heuristic: if message mentions check-in related terms
        for keyword in checkin_keywords:
            if keyword in message_lower:
                return True
        
        # Also check if it's likely a progress update (short, task-focused)
        if len(message.split()) <= 20:  # Short messages are often check-in replies
            return True
            
        return False
    
    def _handle_checkin_reply(self, user_message: str, original_message: dict):
        """Handle check-in replies directly"""
        # Log to daily note
        self._log_checkin_response(user_message)
        
        # Send acknowledgment via assistant bot
        response = self._generate_checkin_response(user_message)
        self.send_via_assistant(response)
    
    def _log_checkin_response(self, response_text: str):
        """Log check-in response to daily note"""
        date_str = datetime.now().strftime("%Y-%m-%d")
        note_file = f"/root/.nanobot/workspace/memory/{date_str}.md"
        
        # Find the latest check-in entry and update it
        try:
            if os.path.exists(note_file):
                with open(note_file, 'r') as f:
                    content = f.read()
                
                # Find the last "Awaiting reply" and replace it
                lines = content.split('\n')
                updated = False
                
                for i in range(len(lines)-1, -1, -1):
                    if "[Awaiting reply]" in lines[i]:
                        lines[i] = f"- **User response:** {response_text}"
                        updated = True
                        break
                
                if updated:
                    with open(note_file, 'w') as f:
                        f.write('\n'.join(lines))
                    logger.info(f"Logged check-in response to {note_file}")
        except Exception as e:
            logger.error(f"Error logging check-in response: {e}")
    
    def _generate_checkin_response(self, user_message: str) -> str:
        """Generate response for check-in replies"""
        # Simple rule-based responses for check-ins
        if any(word in user_message.lower() for word in ["done", "completed", "finished"]):
            return "✅ Great progress! What's the next task on your list?"
        elif any(word in user_message.lower() for word in ["working", "progress", "doing"]):
            return "📊 Thanks for the update! Keep going. Need help with anything specific?"
        elif any(word in user_message.lower() for word in ["next", "will", "going to"]):
            return "🎯 Good plan! I'll check in with you later to see how it went."
        elif len(user_message.split()) < 5:
            return "👍 Got it! I've logged your update."
        else:
            return "📝 Thanks for the detailed update! I've logged it in your daily notes."
    
    def _forward_to_nanobot(self, user_message: str, original_message: dict):
        """Forward message to nanobot with assistant context"""
        # First, acknowledge receipt via assistant bot
        self.send_via_assistant("🔄 Forwarding to AI assistant...")
        
        # Then forward to nanobot with context
        # The nanobot will see the context and respond appropriately
        context_message = f"🔧 [From Assistant Bot]\nUser: {user_message}\n\nPlease respond as a task-focused productivity assistant."
        self.send_via_nanobot(context_message, is_reply=True, original_message=original_message)
    
    def run(self):
        """Main polling loop"""
        logger.info("Starting Telegram Bot Bridge...")
        logger.info(f"Assistant Bot: vpk_assistant_bot")
        logger.info(f"Forwarding to: dreams_nanobot (NanoBot)")
        
        # Test connections
        print("\n🔧 Testing bot connections...")
        
        # Test assistant bot
        url = f"https://api.telegram.org/bot{ASSISTANT_BOT_TOKEN}/getMe"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                bot_info = response.json()
                if bot_info.get("ok"):
                    print(f"✅ Assistant Bot: {bot_info['result']['username']} is online")
                else:
                    print(f"❌ Assistant Bot: Connection failed")
            else:
                print(f"❌ Assistant Bot: HTTP error {response.status_code}")
        except Exception as e:
            print(f"❌ Assistant Bot: Connection error - {e}")
        
        # Test nanobot
        url = f"https://api.telegram.org/bot{NANOBOT_BOT_TOKEN}/getMe"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                bot_info = response.json()
                if bot_info.get("ok"):
                    print(f"✅ NanoBot: {bot_info['result']['username']} is online")
                else:
                    print(f"❌ NanoBot: Connection failed")
            else:
                print(f"❌ NanoBot: HTTP error {response.status_code}")
        except Exception as e:
            print(f"❌ NanoBot: Connection error - {e}")
        
        print("\n🎯 Bridge is running. Messages to Assistant Bot will be forwarded to NanoBot.")
        print("Press Ctrl+C to stop\n")
        
        while True:
            try:
                updates = self.get_assistant_updates()
                for update in updates:
                    self.process_assistant_message(update)
                
                time.sleep(1)
                
            except KeyboardInterrupt:
                logger.info("Shutting down bot bridge...")
                break
            except Exception as e:
                logger.error(f"Error in polling loop: {e}")
                time.sleep(5)

def main():
    """Main entry point"""
    bridge = BotBridge()
    bridge.run()

if __name__ == "__main__":
    main()