#!/bin/bash

echo "🔍 Dual Bot System Monitor"
echo "=========================="

# Check if bots are running
if [ -f /tmp/dual_bot.pid ]; then
    PID=$(cat /tmp/dual_bot.pid)
    if ps -p $PID > /dev/null 2>&1; then
        echo "✅ Dual bot system is RUNNING (PID: $PID)"
    else
        echo "❌ Dual bot system is NOT RUNNING (PID file exists but process dead)"
        rm /tmp/dual_bot.pid
    fi
else
    echo "❌ Dual bot system is NOT RUNNING (No PID file)"
fi

echo ""
echo "📊 Bot Status:"

# Test nanobot
echo -n "🤖 NanoBot: "
cd /root/.nanobot/workspace && source venv/bin/activate && python3 -c "
import telebot
try:
    bot = telebot.TeleBot('8275254305:AAEtsrH0DQAbL5uwha9uHu-0N3TkIGFcgpA')
    info = bot.get_me()
    print('✅ ONLINE -', info.username)
except Exception as e:
    print('❌ OFFLINE -', str(e))
"

# Test assistant bot
echo -n "👨‍💼 Personal Assistant: "
cd /root/.nanobot/workspace && source venv/bin/activate && python3 -c "
import telebot
try:
    bot = telebot.TeleBot('8430328850:AAHGAF2_DNrj8O6kFTOyplsrLbWXiIwHPYc')
    info = bot.get_me()
    print('✅ ONLINE -', info.username)
except Exception as e:
    print('❌ OFFLINE -', str(e))
"

echo ""
echo "📁 Configuration Files:"
ls -la /root/.nanobot/workspace/*.py | grep -E "(bot|config|handler)"
echo ""
echo "📈 Message History:"
if [ -d "/root/.nanobot/workspace/bot_logs" ]; then
    ls -la /root/.nanobot/workspace/bot_logs/
else
    echo "No logs directory found"
fi

echo ""
echo "🔄 Check-in Script Status:"
grep "BOT_TOKEN=" /root/.nanobot/workspace/checkin.sh
echo ""
echo "🛠️ Quick Commands:"
echo "  Start:   ./start_dual_bots.sh"
echo "  Stop:    kill \$(cat /tmp/dual_bot.pid)"
echo "  Monitor: ./bot_monitor.sh"
echo "  Test:    python3 test_bots.py"