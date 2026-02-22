#!/bin/bash

echo "🚀 Starting Dual Bot System"
echo "==========================="

# Activate virtual environment
cd /root/.nanobot/workspace
source venv/bin/activate

echo "Virtual environment activated"

# Start the polling service
echo "Starting bot polling service..."
python3 dual_bot_polling.py &

# Save PID
PID=$!
echo $PID > /tmp/dual_bot.pid
echo "✅ Dual bot polling started with PID: $PID"

# Test sending a message from each bot
echo ""
echo "Sending test messages..."

python3 -c "
import telebot
import time

BOTS = {
    'nanobot': {
        'token': '8275254305:AAEtsrH0DQAbL5uwha9uHu-0N3TkIGFcgpA',
        'name': 'NanoBot',
        'chat_id': '457681374'
    },
    'assistant_bot': {
        'token': '8430328850:AAHGAF2_DNrj8O6kFTOyplsrLbWXiIwHPYc',
        'name': 'Personal Assistant',
        'chat_id': '457681374'
    }
}

for bot_id, config in BOTS.items():
    try:
        bot = telebot.TeleBot(config['token'])
        message = f'🚀 {config[\"name\"]} is now online! I\\'m ready to help.'
        bot.send_message(config['chat_id'], message)
        print(f'✅ {config[\"name\"]} startup message sent')
    except Exception as e:
        print(f'❌ {config[\"name\"]} failed: {e}')
"

echo ""
echo "=========================================="
echo "🎉 DUAL BOT SYSTEM IS NOW RUNNING!"
echo ""
echo "Both bots are active and listening:"
echo ""
echo "1. 🤖 NANOBOT"
echo "   Token: 8275254305:AAEtsrH0DQAbL5uwha9uHu-0N3TkIGFcgpA"
echo "   Personality: Technical AI Assistant"
echo "   Style: Concise, technical, direct"
echo ""
echo "2. 👨‍💼 PERSONAL ASSISTANT"
echo "   Token: 8430328850:AAHGAF2_DNrj8O6kFTOyplsrLbWXiIwHPYc"
echo "   Personality: Friendly Personal Assistant"
echo "   Style: Warm, supportive, task-oriented"
echo ""
echo "=========================================="
echo "📱 TEST THE SYSTEM:"
echo ""
echo "Send a message to either bot on Telegram:"
echo "- Message 'Hello' to Personal Assistant for warm greeting"
echo "- Message 'System status' to NanoBot for technical response"
echo "- Message 'Help' to either bot for context-appropriate help"
echo ""
echo "=========================================="
echo "⚙️ SYSTEM CONTROLS:"
echo ""
echo "To stop the system:"
echo "  kill \$(cat /tmp/dual_bot.pid)"
echo ""
echo "To restart:"
echo "  ./start_dual_bots.sh"
echo ""
echo "To view logs:"
echo "  tail -f nohup.out"
echo ""
echo "=========================================="
echo "🤖 BOT BEHAVIOR SUMMARY:"
echo ""
echo "NANOBOT will respond with:"
echo "- Technical explanations"
echo "- System diagnostics"
echo "- Code and automation help"
echo "- Minimal emojis (🚀, ✅, ⚠️, 🔧)"
echo ""
echo "PERSONAL ASSISTANT will respond with:"
echo "- Friendly greetings"
echo "- Task management help"
echo "- Schedule planning"
echo "- Encouraging tone with emojis (✨, 📅, ✅, 🎯)"
echo ""
echo "Both bots maintain separate conversation histories!"
echo "=========================================="