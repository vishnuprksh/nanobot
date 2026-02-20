# Check-in Subagent System

A dedicated subagent system for handling automated check-ins and user responses via a separate Telegram bot.

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Main Agent    │    │  Check-in Agent │    │  Telegram Bot   │
│   (nanobot)     │◄──►│   (Subagent)    │◄──►│   (Dedicated)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                      │                      │
         ▼                      ▼                      ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Daily Notes    │    │  State & Config │    │  User Responses │
│  (memory/)      │    │  (JSON files)   │    │  (Telegram)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Features

1. **Automated Check-ins**: Sends scheduled check-in messages (9 AM, 12 PM, 3 PM, 6 PM, 9 PM)
2. **Response Logging**: Automatically logs user responses to daily notes
3. **State Management**: Tracks check-in status and user responses
4. **Dedicated Bot**: Uses separate Telegram bot for check-ins only
5. **Flexible Scheduling**: Can run via cron or polling service

## Setup Instructions

### Step 1: Create a New Telegram Bot

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` command
3. Choose a name (e.g., "My Check-in Bot")
4. Choose a username (e.g., "my_checkin_bot")
5. Copy the bot token provided

### Step 2: Run Setup Script

```bash
chmod +x /root/.nanobot/workspace/subagents/setup_checkin_bot.sh
./setup_checkin_bot.sh
```

### Step 3: Configure Cron Jobs

Update your cron jobs to use the new agent:

```bash
# Replace the existing checkin.sh cron entries with:
*/30 9-21 * * * root /usr/bin/python3 /root/.nanobot/workspace/subagents/checkin_agent.py --scheduled
```

### Step 4: Start Polling Service

```bash
# Enable and start the service
sudo systemctl daemon-reload
sudo systemctl enable checkin-bot
sudo systemctl start checkin-bot

# Check status
sudo systemctl status checkin-bot
journalctl -u checkin-bot -f
```

## Files

- `checkin_agent.py` - Main agent logic
- `checkin_polling.py` - Polling service for real-time responses
- `setup_checkin_bot.sh` - Setup script
- `checkin_config.json` - Configuration file
- `checkin_state.json` - State persistence
- `checkin_agent.log` - Agent logs
- `checkin_polling.log` - Polling logs

## Usage

### Manual Check-in
```bash
python3 checkin_agent.py --test
```

### Scheduled Check-in (via cron)
```bash
python3 checkin_agent.py --scheduled
```

### Custom Message
```bash
python3 checkin_agent.py --message "Custom check-in message"
```

### Start Polling Service
```bash
python3 checkin_polling.py
```

## How It Works

1. **Check-in Sent**: Agent sends Telegram message with timestamp and message ID
2. **Daily Note Updated**: Entry created with placeholder for response
3. **User Replies**: User replies directly to the check-in message
4. **Polling Detects**: Polling service detects the reply
5. **Response Logged**: Response is automatically logged in daily notes
6. **Acknowledgment Sent**: User receives confirmation message

## Benefits

1. **Separation of Concerns**: Check-ins handled by dedicated system
2. **Better UX**: Users reply directly to check-in messages
3. **Automatic Logging**: No manual updates needed
4. **Reliable**: State persistence ensures no lost data
5. **Scalable**: Can handle multiple users/chats

## Monitoring

```bash
# View agent logs
tail -f /root/.nanobot/workspace/subagents/checkin_agent.log

# View polling logs
tail -f /root/.nanobot/workspace/subagents/checkin_polling.log

# View systemd service logs
journalctl -u checkin-bot -f

# Check state
cat /root/.nanobot/workspace/subagents/checkin_state.json | jq .
```

## Troubleshooting

### Bot not responding
- Check if bot token is correct
- Verify chat ID matches your Telegram account
- Ensure bot is started and has access to messages

### Responses not logged
- Check polling service is running
- Verify message IDs match in state file
- Check daily note file permissions

### Cron jobs not running
- Check cron syntax and user permissions
- Verify Python path is correct
- Check cron logs: `grep CRON /var/log/syslog`

## Integration with Main Agent

The main agent (nanobot) can:
1. Query check-in status via state file
2. Send manual check-ins via the subagent
3. Read logged responses from daily notes
4. Generate reports based on check-in history

## Future Enhancements

1. **Webhook Support**: Replace polling with webhooks
2. **Multiple Users**: Support multiple chat IDs
3. **Analytics**: Generate check-in statistics
4. **Custom Schedules**: User-defined check-in times
5. **Reminders**: Follow-up reminders for missed check-ins