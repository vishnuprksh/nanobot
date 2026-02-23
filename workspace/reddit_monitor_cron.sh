#!/bin/bash
# Daily Reddit Monitor Cron Script
# Runs at 8:00 AM daily: 1) Scrapes Reddit 2) Submits new tools to Firebase 3) Sends report

cd /root/.nanobot/workspace

# Activate virtual environment if exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

echo "========================================"
echo "Daily Reddit Monitor & Firebase Submission"
echo "Started at: $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================"

# Step 1: Run Reddit monitor
echo "Step 1: Running Reddit monitor..."
python3 reddit_monitor.py > /tmp/reddit_monitor_output.txt 2>&1
REDDIT_EXIT=$?

# Get the report
REPORT=$(cat /tmp/reddit_monitor_output.txt | grep -A 100 "Daily PKMS Tools Update" || echo "No report generated")

# Step 2: Run Firebase submission
echo "Step 2: Submitting new tools to Firebase..."
python3 firebase_submitter.py > /tmp/firebase_submitter_output.txt 2>&1
FIREBASE_EXIT=$?

# Get Firebase results
FIREBASE_SUMMARY=$(tail -20 /tmp/firebase_submitter_output.txt)
echo "$FIREBASE_SUMMARY"

# Combine reports
COMBINED_REPORT="📊 *Daily PKMS Tools Update - $(date '+%Y-%m-%d')*

$REPORT

🚀 *Firebase Submission Results:*
$FIREBASE_SUMMARY

📁 *System Status:*
- Reddit Monitor: $(if [ $REDDIT_EXIT -eq 0 ]; then echo "✅ Success"; else echo "❌ Failed"; fi)
- Firebase Submit: $(if [ $FIREBASE_EXIT -eq 0 ]; then echo "✅ Success"; else echo "❌ Failed"; fi)
- Time: $(date '+%H:%M:%S')
"

# Send via Telegram (using your main bot)
BOT_TOKEN="8275254305:AAEtsrH0DQAbL5uwha9uHu-0N3TkIGFcgpA"
CHAT_ID="457681374"

# Send the combined report
curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
    -d chat_id="${CHAT_ID}" \
    -d text="$COMBINED_REPORT" \
    -d parse_mode="Markdown" \
    > /dev/null

echo "========================================"
echo "Daily process completed at: $(date '+%Y-%m-%d %H:%M:%S')"
echo "Reddit Monitor: $(if [ $REDDIT_EXIT -eq 0 ]; then echo "✅"; else echo "❌"; fi)"
echo "Firebase Submit: $(if [ $FIREBASE_EXIT -eq 0 ]; then echo "✅"; else echo "❌"; fi)"
echo "Report sent to Telegram"
echo "========================================"