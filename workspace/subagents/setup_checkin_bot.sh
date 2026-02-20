#!/bin/bash
# Setup script for Check-in Telegram Bot

echo "========================================"
echo "Check-in Bot Setup"
echo "========================================"

echo ""
echo "STEP 1: Create a new Telegram bot for check-ins"
echo ""
echo "1. Open Telegram and search for @BotFather"
echo "2. Send /newbot command"
echo "3. Choose a name (e.g., 'My Check-in Bot')"
echo "4. Choose a username (e.g., 'my_checkin_bot')"
echo "5. Copy the bot token provided by BotFather"
echo ""
read -p "Have you created the bot? (y/n): " created

if [ "$created" != "y" ]; then
    echo "Please create the bot first and then run this script again."
    exit 1
fi

echo ""
echo "STEP 2: Configure the bot token"
echo ""
read -p "Enter your check-in bot token: " bot_token

if [ -z "$bot_token" ]; then
    echo "Error: Bot token cannot be empty."
    exit 1
fi

echo ""
echo "STEP 3: Get your chat ID"
echo ""
echo "1. Send a message to your new bot (@my_checkin_bot)"
echo "2. Then run: curl -s https://api.telegram.org/bot${bot_token}/getUpdates"
echo "3. Look for 'chat': {'id': YOUR_CHAT_ID}"
echo ""
read -p "Enter your chat ID (press Enter to use default 457681374): " chat_id

if [ -z "$chat_id" ]; then
    chat_id="457681374"
fi

echo ""
echo "STEP 4: Update configuration files"
echo ""

# Update the Python agent
PYTHON_AGENT="/root/.nanobot/workspace/subagents/checkin_agent.py"
if [ -f "$PYTHON_AGENT" ]; then
    sed -i "s/YOUR_CHECKIN_BOT_TOKEN_HERE/$bot_token/" "$PYTHON_AGENT"
    echo "✓ Updated checkin_agent.py with bot token"
else
    echo "✗ Python agent not found: $PYTHON_AGENT"
fi

# Create environment config file
CONFIG_FILE="/root/.nanobot/workspace/subagents/checkin_config.json"
cat > "$CONFIG_FILE" << EOF
{
    "bot_token": "$bot_token",
    "chat_id": "$chat_id",
    "checkin_schedule": ["09:00", "12:00", "15:00", "18:00", "21:00"],
    "workspace_dir": "/root/.nanobot/workspace",
    "polling_interval": 30
}
EOF
echo "✓ Created config file: $CONFIG_FILE"

echo ""
echo "STEP 5: Test the bot"
echo ""
read -p "Send a test message now? (y/n): " test_msg

if [ "$test_msg" = "y" ]; then
    python3 /root/.nanobot/workspace/subagents/checkin_agent.py
fi

echo ""
echo "STEP 6: Set up webhook (optional) or polling service"
echo ""
echo "Option A: Webhook (recommended for production)"
echo "  Requires a public URL with HTTPS"
echo ""
echo "Option B: Polling service (simpler)"
echo "  Create a systemd service to run polling script"
echo ""
read -p "Choose method (A/B, press Enter for B): " method

if [ "$method" = "A" ]; then
    echo ""
    echo "Webhook setup:"
    echo "1. You need a public URL with HTTPS"
    echo "2. Run: curl -F \"url=https://your-domain.com/webhook\" https://api.telegram.org/bot${bot_token}/setWebhook"
    echo "3. Create a web server to handle updates"
else
    echo ""
    echo "Polling setup:"
    echo "Creating polling script..."
    
    # Create polling script
    POLLING_SCRIPT="/root/.nanobot/workspace/subagents/checkin_polling.py"
    cat > "$POLLING_SCRIPT" << 'EOF'
#!/usr/bin/env python3
"""
Polling script for Check-in Bot.
Runs continuously and checks for new messages.
"""

import os
import sys
import time
import json
import logging
import requests
from datetime import datetime
from checkin_agent import CheckinAgent

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/root/.nanobot/workspace/subagents/checkin_polling.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("checkin_polling")

def poll_updates(agent, offset=None):
    """Poll Telegram for updates."""
    url = f"https://api.telegram.org/bot{agent.bot_token}/getUpdates"
    params = {"timeout": 30}
    
    if offset:
        params["offset"] = offset
    
    try:
        response = requests.get(url, params=params, timeout=35)
        data = response.json()
        
        if data.get("ok"):
            return data["result"]
        else:
            logger.error(f"Telegram API error: {data}")
            return []
    except Exception as e:
        logger.error(f"Error polling updates: {e}")
        return []

def process_update(agent, update):
    """Process a single update."""
    if "message" in update:
        message = update["message"]
        message_id = message.get("message_id")
        chat_id = message.get("chat", {}).get("id")
        text = message.get("text", "")
        
        # Check if this is a reply to a check-in message
        reply_to = message.get("reply_to_message")
        if reply_to:
            replied_message_id = reply_to.get("message_id")
            
            # Log the response
            success = agent.log_response(replied_message_id, text)
            if success:
                logger.info(f"Logged response to message {replied_message_id}: {text[:50]}...")
                
                # Send acknowledgment
                ack_url = f"https://api.telegram.org/bot{agent.bot_token}/sendMessage"
                ack_payload = {
                    "chat_id": chat_id,
                    "text": f"✓ Response logged!\n\nYour update has been saved to your daily notes.",
                    "reply_to_message_id": message_id
                }
                requests.post(ack_url, json=ack_payload, timeout=10)
            else:
                logger.warning(f"Failed to log response for message {replied_message_id}")
    
    return update["update_id"]

def main():
    """Main polling loop."""
    logger.info("Starting Check-in Bot polling service")
    
    agent = CheckinAgent()
    offset = None
    
    # Check if bot token is configured
    if agent.bot_token == "YOUR_CHECKIN_BOT_TOKEN_HERE":
        logger.error("Bot token not configured! Run setup_checkin_bot.sh first.")
        sys.exit(1)
    
    logger.info(f"Bot initialized. Chat ID: {agent.chat_id}")
    
    try:
        while True:
            logger.debug("Polling for updates...")
            updates = poll_updates(agent, offset)
            
            if updates:
                for update in updates:
                    new_offset = process_update(agent, update)
                    if new_offset:
                        offset = new_offset + 1
                
                # Save state after processing updates
                agent.save_state()
            
            # Sleep before next poll
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Polling stopped by user")
    except Exception as e:
        logger.error(f"Polling error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
EOF
    
    chmod +x "$POLLING_SCRIPT"
    echo "✓ Created polling script: $POLLING_SCRIPT"
    
    # Create systemd service file
    SERVICE_FILE="/etc/systemd/system/checkin-bot.service"
    if [ ! -f "$SERVICE_FILE" ]; then
        cat > "$SERVICE_FILE" << EOF
[Unit]
Description=Check-in Bot Polling Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/.nanobot/workspace/subagents
ExecStart=/usr/bin/python3 /root/.nanobot/workspace/subagents/checkin_polling.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
        echo "✓ Created systemd service: $SERVICE_FILE"
        echo ""
        echo "To enable and start the service:"
        echo "  sudo systemctl daemon-reload"
        echo "  sudo systemctl enable checkin-bot"
        echo "  sudo systemctl start checkin-bot"
        echo ""
        echo "To check status:"
        echo "  sudo systemctl status checkin-bot"
        echo "  journalctl -u checkin-bot -f"
    else
        echo "✓ Systemd service already exists: $SERVICE_FILE"
    fi
fi

echo ""
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "Summary:"
echo "1. Bot token configured"
echo "2. Chat ID set to: $chat_id"
echo "3. Configuration files created"
echo "4. Polling script ready"
echo ""
echo "Next steps:"
echo "1. Update cron jobs to use the new agent"
echo "2. Start the polling service"
echo "3. Test the complete system"
echo ""
echo "To update cron:"
echo "  Edit /etc/crontab and change checkin.sh to:"
echo "  */30 9-21 * * * root /usr/bin/python3 /root/.nanobot/workspace/subagents/checkin_agent.py --scheduled"
echo ""