#!/bin/bash
# Daily Reddit Monitor Cron Script
# Runs at 8:00 AM daily and sends report via Telegram

cd /root/.nanobot/workspace

# Activate virtual environment if exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run the monitor
python3 reddit_monitor.py > /tmp/reddit_monitor_output.txt 2>&1

# Get the report
REPORT=$(cat /tmp/reddit_monitor_output.txt | grep -A 100 "Daily PKMS Tools Update" || echo "No report generated")

# Send via Telegram (using your main bot)
BOT_TOKEN="8275254305:AAEtsrH0DQAbL5uwha9uHu-0N3TkIGFcgpA"
CHAT_ID="457681374"

# Send the report
curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
    -d chat_id="${CHAT_ID}" \
    -d text="${REPORT}" \
    -d parse_mode="Markdown" \
    > /dev/null

echo "Reddit monitor report sent at $(date)"