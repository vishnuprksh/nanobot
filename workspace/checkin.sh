#!/bin/bash
# Personal Assistant Check-in Script with Telegram notification

DATE=$(date +%Y-%m-%d)
TIME=$(date +%H:%M)
NOTE_FILE="/root/.nanobot/workspace/memory/${DATE}.md"
CHAT_ID="457681374"
BOT_TOKEN="8275254305:AAEtsrH0DQAbL5uwha9uHu-0N3TkIGFcgpA"

# Send Telegram message using curl
MESSAGE="📋 Check-in time! (${TIME})

What have you accomplished since last check-in?
What's next on your list?

Reply to this message and I'll log your response."

curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
    -d chat_id="${CHAT_ID}" \
    -d text="${MESSAGE}" \
    -d parse_mode="Markdown"

# Create daily note if it doesn't exist
if [ ! -f "$NOTE_FILE" ]; then
    echo "# ${DATE}" > "$NOTE_FILE"
    echo "" >> "$NOTE_FILE"
    echo "## Check-ins" >> "$NOTE_FILE"
    echo "" >> "$NOTE_FILE"
fi

# Add check-in entry with placeholder for user response
echo "### ${TIME} Check-in" >> "$NOTE_FILE"
echo "- **Question sent at:** ${TIME}" >> "$NOTE_FILE"
echo "- **User response:** [Awaiting reply]" >> "$NOTE_FILE"
echo "- **Progress:** " >> "$NOTE_FILE"
echo "- **Next actions:** " >> "$NOTE_FILE"
echo "" >> "$NOTE_FILE"

echo "Check-in message sent at ${TIME}"