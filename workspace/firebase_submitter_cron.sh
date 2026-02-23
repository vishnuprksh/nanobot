#!/bin/bash
# Cron script for Firebase app submission
# Runs daily after Reddit scraper to submit new tools

set -e

LOG_FILE="/root/.nanobot/workspace/firebase_submitter.log"
PYTHON_SCRIPT="/root/.nanobot/workspace/firebase_submitter.py"
VENV_PATH="/root/.nanobot/workspace/venv/bin/activate"

echo "========================================" >> "$LOG_FILE"
echo "Firebase Submission Cron - $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"

# Check if Python script exists
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "ERROR: Python script not found at $PYTHON_SCRIPT" >> "$LOG_FILE"
    exit 1
fi

# Activate virtual environment if exists
if [ -f "$VENV_PATH" ]; then
    source "$VENV_PATH"
    echo "Activated virtual environment" >> "$LOG_FILE"
fi

# Run the submission script
echo "Starting Firebase submission..." >> "$LOG_FILE"
python3 "$PYTHON_SCRIPT" >> "$LOG_FILE" 2>&1

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "Firebase submission completed successfully" >> "$LOG_FILE"
else
    echo "Firebase submission failed with exit code: $EXIT_CODE" >> "$LOG_FILE"
fi

echo "========================================" >> "$LOG_FILE"
echo "Cron job completed" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"

exit $EXIT_CODE