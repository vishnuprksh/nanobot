#!/bin/bash

# Setup script for dual bot system

echo "🤖 Setting up Dual Bot System"
echo "=============================="

# Check Python dependencies
echo "Checking dependencies..."
python3 -c "import telebot" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing python-telegram-bot..."
    pip3 install pyTelegramBotAPI
else
    echo "✅ pyTelegramBotAPI already installed"
fi

# Create necessary directories
echo "Creating directories..."
mkdir -p /root/.nanobot/workspace/bot_logs
mkdir -p /root/.nanobot/workspace/bot_data

# Test bot configurations
echo "Testing bot configurations..."
python3 -c "
from bot_config import BOT_CONFIGS, TOKEN_TO_BOT
print(f'✅ Loaded {len(BOT_CONFIGS)} bot configurations')
print(f'✅ Token mapping: {len(TOKEN_TO_BOT)} tokens')
for bot_id, config in BOT_CONFIGS.items():
    print(f'  - {config[\"name\"]}: {bot_id}')
"

# Test message handler
echo "Testing message handler..."
python3 -c "
try:
    from dual_bot_handler import DualBotHandler
    print('✅ DualBotHandler imported successfully')
    
    handler = DualBotHandler()
    print(f'✅ Initialized {len(handler.bots)} bots')
    
    # Quick test
    test_token = list(BOT_CONFIGS.values())[0]['token']
    result = handler.process_incoming(test_token, 'Test message')
    print(f'✅ Test message processed: {result[\"success\"]}')
    
except Exception as e:
    print(f'❌ Error: {e}')
"

# Update checkin.sh to use nanobot (for consistency)
echo "Updating checkin.sh to use nanobot token..."
CURRENT_TOKEN=$(grep -o 'BOT_TOKEN="[^"]*"' /root/.nanobot/workspace/checkin.sh | head -1)
NANOBOT_TOKEN="8275254305:AAEtsrH0DQAbL5uwha9uHu-0N3TkIGFcgpA"

if [[ "$CURRENT_TOKEN" != *"$NANOBOT_TOKEN"* ]]; then
    echo "Updating checkin.sh token to nanobot..."
    sed -i "s/BOT_TOKEN=\"[^\"]*\"/BOT_TOKEN=\"$NANOBOT_TOKEN\"/g" /root/.nanobot/workspace/checkin.sh
    echo "✅ Updated checkin.sh"
else
    echo "✅ checkin.sh already uses nanobot token"
fi

# Create systemd service for bot polling
echo "Creating systemd service..."
cat > /etc/systemd/system/dual-bot.service << EOF
[Unit]
Description=Dual Telegram Bot Handler
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/.nanobot/workspace
ExecStart=/usr/bin/python3 /root/.nanobot/workspace/dual_bot_polling.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Created systemd service"

# Create polling script
echo "Creating polling script..."
cat > /root/.nanobot/workspace/dual_bot_polling.py << 'EOF'
#!/usr/bin/env python3
"""
Polling service for dual bot system
Listens to both bots and routes messages appropriately
"""

import time
import telebot
import threading
from bot_config import BOT_CONFIGS
from dual_bot_handler import DualBotHandler

class DualBotPolling:
    def __init__(self):
        self.handler = DualBotHandler()
        self.bot_threads = []
        self.running = True
        
    def start_bot_polling(self, bot_id, config):
        """Start polling for a specific bot"""
        print(f"Starting polling for {config['name']}...")
        
        bot = telebot.TeleBot(config['token'])
        
        @bot.message_handler(func=lambda message: True)
        def handle_all_messages(message):
            print(f"📨 [{config['name']}] Received: {message.text}")
            
            # Process message through handler
            result = self.handler.process_incoming(config['token'], message.text)
            
            if result['success']:
                print(f"✅ [{config['name']}] Response sent")
            else:
                print(f"❌ [{config['name']}] Failed to send response")
        
        # Start polling in this thread
        print(f"🚀 {config['name']} polling started")
        bot.infinity_polling()
    
    def start(self):
        """Start polling for all bots"""
        print("🤖 Starting Dual Bot Polling Service")
        print("=" * 50)
        
        for bot_id, config in BOT_CONFIGS.items():
            thread = threading.Thread(
                target=self.start_bot_polling,
                args=(bot_id, config),
                daemon=True
            )
            thread.start()
            self.bot_threads.append(thread)
            print(f"✅ {config['name']} thread started")
        
        print("\n✅ All bots started. Press Ctrl+C to stop.")
        
        # Keep main thread alive
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping bots...")
            self.running = False
    
    def stop(self):
        """Stop all bot polling"""
        self.running = False
        for thread in self.bot_threads:
            thread.join(timeout=5)
        print("✅ All bots stopped")

if __name__ == "__main__":
    service = DualBotPolling()
    service.start()
EOF

chmod +x /root/.nanobot/workspace/dual_bot_polling.py
echo "✅ Created polling script"

# Test the system
echo "Running quick test..."
python3 /root/.nanobot/workspace/dual_bot_handler.py

echo ""
echo "🎉 Setup Complete!"
echo ""
echo "Next steps:"
echo "1. Start the service: sudo systemctl start dual-bot"
echo "2. Enable on boot: sudo systemctl enable dual-bot"
echo "3. Check status: sudo systemctl status dual-bot"
echo "4. View logs: sudo journalctl -u dual-bot -f"
echo ""
echo "Both bots will now:"
echo "  - Receive messages independently"
echo "  - Respond with appropriate personalities"
echo "  - Maintain separate conversation histories"
echo ""
echo "Test by sending messages to either bot on Telegram!"