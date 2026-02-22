#!/usr/bin/env python3
"""
Dual Bot Message Handler
Routes messages to appropriate personality and responds accordingly
"""

import json
import os
from datetime import datetime
import telebot
from bot_config import BOT_CONFIGS, detect_bot_from_token, get_personality_prompt

class DualBotHandler:
    def __init__(self):
        self.bots = {}
        self.message_history = {}
        self.setup_bots()
        
    def setup_bots(self):
        """Initialize both Telegram bots"""
        for bot_id, config in BOT_CONFIGS.items():
            try:
                bot = telebot.TeleBot(config["token"])
                self.bots[bot_id] = {
                    "instance": bot,
                    "config": config,
                    "chat_id": config["chat_id"]
                }
                print(f"✅ Initialized {config['name']} ({bot_id})")
            except Exception as e:
                print(f"❌ Failed to initialize {bot_id}: {e}")
    
    def get_bot_context(self, bot_id):
        """Get context for a bot based on message history"""
        history = self.message_history.get(bot_id, [])
        if not history:
            return "No previous conversation."
        
        # Get last 5 messages for context
        recent = history[-5:]
        context_lines = []
        for msg in recent:
            role = "User" if msg.get("from_user") else "Assistant"
            context_lines.append(f"{role}: {msg.get('text', '')}")
        
        return "\n".join(context_lines)
    
    def save_message(self, bot_id, text, from_user=True):
        """Save message to history"""
        if bot_id not in self.message_history:
            self.message_history[bot_id] = []
        
        self.message_history[bot_id].append({
            "timestamp": datetime.now().isoformat(),
            "from_user": from_user,
            "text": text,
            "bot": bot_id
        })
        
        # Keep only last 20 messages
        if len(self.message_history[bot_id]) > 20:
            self.message_history[bot_id] = self.message_history[bot_id][-20:]
    
    def generate_response(self, bot_id, user_message):
        """Generate response based on bot personality"""
        config = BOT_CONFIGS[bot_id]
        
        # Get conversation context
        context = self.get_bot_context(bot_id)
        
        # Save user message
        self.save_message(bot_id, user_message, from_user=True)
        
        # Get personality prompt
        prompt = get_personality_prompt(bot_id, context, user_message)
        
        # Generate response (in real implementation, this would call AI)
        # For now, return a placeholder based on personality
        if bot_id == "nanobot":
            response = self._generate_nanobot_response(user_message)
        else:  # assistant_bot
            response = self._generate_assistant_response(user_message)
        
        # Save assistant response
        self.save_message(bot_id, response, from_user=False)
        
        return response
    
    def _generate_nanobot_response(self, message):
        """Generate NanoBot-style response"""
        responses = {
            "greeting": "Hello! I'm NanoBot, your technical assistant. How can I help with system administration or development today? 🚀",
            "help": "I can help with: 1) System configuration, 2) Automation scripts, 3) Debugging, 4) Code review, 5) Task automation. What do you need? 🔧",
            "checkin": "Check-in received. Current system status: All systems operational. Backup schedule active. Next check-in scheduled. ✅",
            "default": f"Technical analysis: {message}. Recommend checking system logs and reviewing configuration. Would you like me to run diagnostics? ⚙️"
        }
        
        message_lower = message.lower()
        if "hello" in message_lower or "hi" in message_lower:
            return responses["greeting"]
        elif "help" in message_lower:
            return responses["help"]
        elif "check" in message_lower or "status" in message_lower:
            return responses["checkin"]
        else:
            return responses["default"]
    
    def _generate_assistant_response(self, message):
        """Generate Personal Assistant-style response"""
        responses = {
            "greeting": "Hi there! 👋 I'm your personal assistant. Ready to help with tasks, schedules, or anything else you need today! ✨",
            "help": "I can help you with: 1) Task management 📝, 2) Schedule planning 📅, 3) Reminders ⏰, 4) Check-ins ✅, 5) Productivity tips 🎯. What would you like to focus on?",
            "checkin": "Thanks for checking in! 📋 How's your day going? Want to review your tasks or schedule something for later? I'm here to help! 💫",
            "default": f"Got it! Regarding '{message}', let me help with that. Would you like me to add it to your task list or schedule a reminder? 📌"
        }
        
        message_lower = message.lower()
        if "hello" in message_lower or "hi" in message_lower:
            return responses["greeting"]
        elif "help" in message_lower:
            return responses["help"]
        elif "check" in message_lower or "how are you" in message_lower:
            return responses["checkin"]
        else:
            return responses["default"]
    
    def send_message(self, bot_id, text):
        """Send message through appropriate bot"""
        if bot_id not in self.bots:
            print(f"❌ Bot {bot_id} not initialized")
            return False
        
        try:
            bot_info = self.bots[bot_id]
            bot = bot_info["instance"]
            chat_id = bot_info["chat_id"]
            
            bot.send_message(chat_id, text)
            print(f"✅ Sent message via {bot_info['config']['name']}: {text[:50]}...")
            return True
        except Exception as e:
            print(f"❌ Failed to send message via {bot_id}: {e}")
            return False
    
    def process_incoming(self, token, message_text):
        """Process incoming message from any bot"""
        bot_id = detect_bot_from_token(token)
        print(f"📩 Message received via {bot_id}: {message_text[:50]}...")
        
        # Generate appropriate response
        response = self.generate_response(bot_id, message_text)
        
        # Send response back through same bot
        success = self.send_message(bot_id, response)
        
        return {
            "bot_id": bot_id,
            "bot_name": BOT_CONFIGS[bot_id]["name"],
            "response": response,
            "success": success
        }

def test_bots():
    """Test both bots are working"""
    handler = DualBotHandler()
    
    print("\n🧪 Testing bot initialization...")
    for bot_id in handler.bots:
        print(f"  {BOT_CONFIGS[bot_id]['name']}: ✅ Active")
    
    print("\n🧪 Testing message processing...")
    test_messages = [
        ("Hi there!", "assistant_bot"),
        ("System status?", "nanobot"),
        ("Can you help me?", "assistant_bot"),
        ("Run diagnostics", "nanobot")
    ]
    
    for message, expected_bot in test_messages:
        # Use appropriate token based on expected bot
        token = BOT_CONFIGS[expected_bot]["token"]
        result = handler.process_incoming(token, message)
        print(f"\n  Test: '{message}'")
        print(f"    Bot: {result['bot_name']}")
        print(f"    Response: {result['response'][:60]}...")
        print(f"    Success: {result['success']}")

if __name__ == "__main__":
    print("🤖 Dual Bot Handler")
    print("=" * 50)
    test_bots()