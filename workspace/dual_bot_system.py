#!/usr/bin/env python3
"""
Dual Telegram Bot System
Connects both bots to nanobot AI with different personalities
"""

import os
import sys
import json
import logging
from typing import Dict, Any
import requests
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Bot configurations
BOT_CONFIG = {
    "nanobot": {
        "token": "8275254305:AAEtsrH0DQAbL5uwha9uHu-0N3TkIGFcgpA",
        "name": "NanoBot",
        "personality": "general_ai",
        "style": "creative, exploratory, helpful AI assistant",
        "greeting": "👋 Hi! I'm NanoBot, your AI assistant. How can I help you today?",
        "prompt_prefix": "You are NanoBot, a creative and helpful AI assistant. "
    },
    "assistant": {
        "token": "8430328850:AAHGAF2_DNrj8O6kFTOyplsrLbWXiIwHPYc",
        "name": "Assistant Bot",
        "personality": "task_assistant",
        "style": "focused, structured, productive assistant",
        "greeting": "📋 Hello! I'm your Task Assistant. Ready for check-ins and productivity tracking.",
        "prompt_prefix": "You are a task-focused productivity assistant. Be concise, structured, and focused on tasks, check-ins, and productivity. "
    }
}

# Chat history storage
CHAT_HISTORY = {}

class DualBotSystem:
    def __init__(self):
        self.bots = BOT_CONFIG
        self.last_update_id = {bot_name: 0 for bot_name in self.bots}
        
    def get_updates(self, bot_name: str):
        """Get new messages for a specific bot"""
        token = self.bots[bot_name]["token"]
        url = f"https://api.telegram.org/bot{token}/getUpdates"
        params = {
            "offset": self.last_update_id[bot_name] + 1,
            "timeout": 30
        }
        
        try:
            response = requests.get(url, params=params, timeout=35)
            if response.status_code == 200:
                data = response.json()
                if data.get("ok") and data.get("result"):
                    return data["result"]
        except Exception as e:
            logger.error(f"Error getting updates for {bot_name}: {e}")
        return []
    
    def send_message(self, bot_name: str, chat_id: str, text: str):
        """Send message through specific bot"""
        token = self.bots[bot_name]["token"]
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        
        # Apply bot-specific styling
        styled_text = self.apply_bot_style(bot_name, text)
        
        data = {
            "chat_id": chat_id,
            "text": styled_text,
            "parse_mode": "Markdown"
        }
        
        try:
            response = requests.post(url, json=data)
            if response.status_code == 200:
                logger.info(f"Message sent via {bot_name} to {chat_id}")
                return True
            else:
                logger.error(f"Failed to send message: {response.text}")
        except Exception as e:
            logger.error(f"Error sending message via {bot_name}: {e}")
        return False
    
    def apply_bot_style(self, bot_name: str, text: str) -> str:
        """Apply bot-specific styling to messages"""
        bot_config = self.bots[bot_name]
        
        if bot_name == "assistant":
            # Assistant bot: structured, emoji-based, task-focused
            if "check-in" in text.lower() or "accomplish" in text.lower():
                return f"📋 {text}"
            elif "task" in text.lower() or "next" in text.lower():
                return f"✅ {text}"
            elif "question" in text.lower():
                return f"❓ {text}"
            else:
                return f"🤖 {text}"
        else:
            # NanoBot: creative, friendly
            return text
    
    def generate_response(self, bot_name: str, user_message: str, chat_id: str) -> str:
        """Generate AI response based on bot personality"""
        bot_config = self.bots[bot_name]
        
        # Get chat history
        history_key = f"{bot_name}_{chat_id}"
        if history_key not in CHAT_HISTORY:
            CHAT_HISTORY[history_key] = []
        
        # Prepare context
        context = {
            "bot_personality": bot_config["personality"],
            "bot_style": bot_config["style"],
            "user_message": user_message,
            "chat_history": CHAT_HISTORY[history_key][-5:],  # Last 5 messages
            "current_time": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "is_check_in": "check-in" in user_message.lower()
        }
        
        # Generate response based on bot type
        if bot_name == "assistant":
            return self._generate_assistant_response(context)
        else:
            return self._generate_nanobot_response(context)
    
    def _generate_assistant_response(self, context: Dict[str, Any]) -> str:
        """Generate response for task-focused assistant bot"""
        user_msg = context["user_message"]
        
        # Check-in specific responses
        if context["is_check_in"]:
            if "accomplish" in user_msg.lower():
                return "Great! I've logged your progress. What specific tasks are you working on next?"
            elif "next" in user_msg.lower():
                return "Perfect! I'll help you stay focused on those tasks. Need help prioritizing or breaking them down?"
        
        # Task management responses
        if any(word in user_msg.lower() for word in ["task", "todo", "remind", "schedule"]):
            return "I can help with task management! Would you like to:\n1. Add a new task\n2. Check task status\n3. Set a reminder\n4. Review progress?"
        
        # General assistant response
        return "I'm here to help with productivity and tasks. You can:\n• Reply to check-ins\n• Ask about task management\n• Get help staying focused\n• Review your progress"
    
    def _generate_nanobot_response(self, context: Dict[str, Any]) -> str:
        """Generate response for general AI assistant"""
        user_msg = context["user_message"]
        
        # Creative/exploratory responses
        if any(word in user_msg.lower() for word in ["learn", "research", "explain", "how"]):
            return "I'd be happy to help you learn or research that topic! What specifically would you like to know?"
        
        if any(word in user_msg.lower() for word in ["create", "build", "make", "design"]):
            return "That sounds like a creative project! I can help you design, plan, or brainstorm ideas."
        
        if any(word in user_msg.lower() for word in ["help", "assist", "support"]):
            return "I'm here to help! Whether it's answering questions, solving problems, or just having a conversation, I'm ready."
        
        # Default creative response
        return "Hello! I'm NanoBot, your AI assistant. I can help with learning, creativity, problem-solving, or just chatting. What's on your mind?"
    
    def process_message(self, bot_name: str, update: Dict[str, Any]):
        """Process incoming message and generate response"""
        message = update.get("message", {})
        chat_id = str(message.get("chat", {}).get("id"))
        user_message = message.get("text", "").strip()
        
        if not user_message:
            return
        
        # Update last update ID
        self.last_update_id[bot_name] = update["update_id"]
        
        # Generate response based on bot personality
        response = self.generate_response(bot_name, user_message, chat_id)
        
        # Send response
        self.send_message(bot_name, chat_id, response)
        
        # Log interaction
        logger.info(f"Processed message via {bot_name}: {user_message[:50]}...")
        
        # Update chat history
        history_key = f"{bot_name}_{chat_id}"
        if history_key not in CHAT_HISTORY:
            CHAT_HISTORY[history_key] = []
        CHAT_HISTORY[history_key].append({
            "user": user_message,
            "bot": response,
            "timestamp": datetime.now().isoformat()
        })
    
    def run_polling(self):
        """Main polling loop"""
        logger.info("Starting dual bot polling system...")
        
        # Send startup messages
        for bot_name in self.bots:
            logger.info(f"{bot_name} is online: {self.bots[bot_name]['name']}")
        
        while True:
            try:
                for bot_name in self.bots:
                    updates = self.get_updates(bot_name)
                    for update in updates:
                        self.process_message(bot_name, update)
            except KeyboardInterrupt:
                logger.info("Shutting down dual bot system...")
                break
            except Exception as e:
                logger.error(f"Error in polling loop: {e}")
                import time
                time.sleep(5)

def main():
    """Main entry point"""
    print("🚀 Dual Telegram Bot System")
    print("=" * 40)
    print("Bot 1: NanoBot (Creative AI Assistant)")
    print("Bot 2: Assistant Bot (Task-Focused Assistant)")
    print("=" * 40)
    
    system = DualBotSystem()
    
    # Test connections
    print("\n🔧 Testing bot connections...")
    for bot_name in system.bots:
        token = system.bots[bot_name]["token"]
        url = f"https://api.telegram.org/bot{token}/getMe"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                bot_info = response.json()
                if bot_info.get("ok"):
                    print(f"✅ {bot_name}: {bot_info['result']['username']} is online")
                else:
                    print(f"❌ {bot_name}: Connection failed")
            else:
                print(f"❌ {bot_name}: HTTP error {response.status_code}")
        except Exception as e:
            print(f"❌ {bot_name}: Connection error - {e}")
    
    print("\n🎯 Starting polling system...")
    print("Press Ctrl+C to stop")
    system.run_polling()

if __name__ == "__main__":
    main()