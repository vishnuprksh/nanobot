#!/bin/bash

# Setup Check-in System with Existing Telegram Bot
# This configures the subagent system to use your existing Telegram bot

set -e

echo "=========================================="
echo "CHECK-IN SYSTEM SETUP"
echo "=========================================="

# Check Python dependencies
echo "Checking Python dependencies..."
python3 -c "import requests" 2>/dev/null || {
    echo "Installing requests library..."
    pip3 install requests
}

# Verify configuration
echo "Verifying configuration..."
if [ ! -f "config.py" ]; then
    echo "Creating config.py..."
    cat > config.py << 'EOF'
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
EOF
fi

# Make scripts executable
echo "Making scripts executable..."
chmod +x checkin_agent.py checkin_polling.py

# Test the bot token
echo "Testing Telegram bot token..."
python3 -c "
import requests
try:
    token = '8430328850:AAHGAF2_DNrj8O6kFTOyplsrLbWXiIwHPYc'
    response = requests.get(f'https://api.telegram.org/bot{token}/getMe', timeout=10)
    if response.json().get('ok'):
        print('✅ Bot token is valid!')
        bot_name = response.json()['result']['first_name']
        print(f'🤖 Bot name: {bot_name}')
    else:
        print('❌ Bot token is invalid')
except Exception as e:
    print(f'❌ Error testing bot: {e}')
"

# Test sending a message
echo -e "\nTesting message sending..."
read -p "Send test message? (y/n): " send_test
if [[ $send_test == "y" || $send_test == "Y" ]]; then
    python3 checkin_agent.py --message "🚀 Test message from Check-in System Setup"
    if [ $? -eq 0 ]; then
        echo "✅ Test message sent successfully!"
    else
        echo "❌ Failed to send test message"
    fi
fi

# Setup systemd service
echo -e "\nSetting up systemd service..."
sudo cp checkin_bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable checkin-bot

echo -e "\nStarting polling service..."
sudo systemctl start checkin-bot
sleep 2
sudo systemctl status checkin-bot --no-pager

# Update cron jobs
echo -e "\nUpdating cron jobs..."
current_cron=$(crontab -l 2>/dev/null || true)

# Remove old checkin.sh entries
new_cron=$(echo "$current_cron" | grep -v "checkin.sh" | grep -v "^#")

# Add new check-in schedule
checkin_schedule="# Check-in schedule (using Python agent)
0 9,12,15,18,21 * * * cd /root/.nanobot/workspace/subagents && /usr/bin/python3 checkin_agent.py --scheduled >> /var/log/checkin.log 2>&1
# Backup schedule (every 4 hours)
0 */4 * * * /root/.nanobot/workspace/backup.sh >> /var/log/nanobot_backup.log 2>&1"

# Combine
echo -e "$new_cron\n$checkin_schedule" | crontab -

echo -e "\nNew cron jobs:"
crontab -l

# Create log files
echo -e "\nCreating log files..."
touch /var/log/checkin.log
touch /var/log/nanobot_backup.log
chmod 644 /var/log/checkin.log /var/log/nanobot_backup.log

echo "=========================================="
echo "SETUP COMPLETE!"
echo "=========================================="
echo ""
echo "✅ System configured with your existing Telegram bot"
echo "✅ Polling service installed and running"
echo "✅ Cron jobs updated"
echo "✅ Log files created"
echo ""
echo "📋 Next steps:"
echo "1. Check Telegram for test message (if sent)"
echo "2. Verify service is running: sudo systemctl status checkin-bot"
echo "3. Check logs: sudo journalctl -u checkin-bot -f"
echo "4. Manual test: python3 checkin_agent.py --scheduled"
echo ""
echo "🚀 The system will now:"
echo "   • Send check-ins at 9 AM, 12 PM, 3 PM, 6 PM, 9 PM"
echo "   • Automatically log your responses"
echo "   • Send acknowledgments when you reply"
echo "   • Run backups every 4 hours"
echo ""
echo "To stop the service: sudo systemctl stop checkin-bot"
echo "To view logs: sudo journalctl -u checkin-bot -f"
echo "=========================================="