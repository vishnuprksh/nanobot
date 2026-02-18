#!/bin/bash
# Personal Assistant Check-in Script

DATE=$(date +%Y-%m-%d)
TIME=$(date +%H:%M)
NOTE_FILE="/root/.nanobot/workspace/memory/${DATE}.md"

# Create daily note if it doesn't exist
if [ ! -f "$NOTE_FILE" ]; then
    echo "# ${DATE}" > "$NOTE_FILE"
    echo "" >> "$NOTE_FILE"
    echo "## Check-ins" >> "$NOTE_FILE"
    echo "" >> "$NOTE_FILE"
fi

# Add check-in entry
echo "### ${TIME} Check-in" >> "$NOTE_FILE"
echo "- Progress: " >> "$NOTE_FILE"
echo "- Next actions: " >> "$NOTE_FILE"
echo "" >> "$NOTE_FILE"

echo "Check-in logged at ${TIME}"