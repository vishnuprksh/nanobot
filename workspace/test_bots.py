#!/usr/bin/env python3
"""
Test script to verify both bots can send messages
"""

import telebot
import time

# Bot configurations
BOTS = {
    "nanobot": {
        "token": "8275254305:AAEtsrH0DQAbL5uwha9uHu-0N3TkIGFcgpA",
        "name": "NanoBot",
        "chat_id": "457681374"
    },
    "assistant_bot": {
        "token": "8430328850:AAHGAF2_DNrj8O6kFTOyplsrLbWXiIwHPYc",
        "name": "Personal Assistant",
        "chat_id": "457681374"
    }
}

def test_bot_sending():
    """Test that both bots can send messages"""
    print("🤖 Testing Bot Message Sending")
    print("=" * 50)
    
    for bot_id, config in BOTS.items():
        try:
            bot = telebot.TeleBot(config["token"])
            message = f"Test message from {config['name']} at {time.strftime('%H:%M:%S')}"
            
            print(f"\nSending test message via {config['name']}...")
            sent_msg = bot.send_message(config["chat_id"], message)
            
            if sent_msg.message_id:
                print(f"✅ SUCCESS: {config['name']} sent message (ID: {sent_msg.message_id})")
                print(f"   Message: {message}")
            else:
                print(f"❌ FAILED: {config['name']} - No message ID returned")
                
        except Exception as e:
            print(f"❌ ERROR: {config['name']} - {str(e)}")
    
    print("\n" + "=" * 50)
    print("Test complete! Check your Telegram for messages from both bots.")

if __name__ == "__main__":
    # Activate virtual environment
    import sys
    sys.path.insert(0, '/root/.nanobot/workspace/venv/lib/python3.12/site-packages')
    
    test_bot_sending()