# nanobot Features

## Core Capabilities

### File Operations
- Read files and directories
- Write and create files
- Edit files by replacing text

### System Operations
- Execute shell commands
- List directory contents
- Run scripts and programs

### Web Interaction
- Perform web searches
- Fetch and extract content from URLs
- Convert HTML to markdown/text

### Communication
- Send messages to users via Telegram
- Support for multiple channels (Telegram, Discord, etc.)

### Memory & Context
- Maintain long-term memory in workspace/memory/
- Track user preferences and history
- Store daily notes and persistent data

## Available Skills

### cron
- Schedule reminders and recurring tasks
- Add, list, and remove scheduled jobs
- Support for cron expressions and interval-based timing

### weather
- Get current weather conditions
- Retrieve weather forecasts
- No API key required

### skill-creator
- Create or update AgentSkills
- Package skills with scripts, references, and assets
- Design and structure new capabilities

### tmux
- Remote-control tmux sessions
- Send keystrokes to tmux panes
- Scrape and read output from interactive CLIs

## Tools

### read_file
Read the contents of any file in the system.

### write_file
Create or overwrite files at any path.

### edit_file
Modify files by replacing specific text.

### list_dir
List contents of directories.

### exec
Execute shell commands with full system access.

### web_search
Search the web and return results with titles, URLs, and snippets.

### web_fetch
Retrieve and extract readable content from web pages.

### message
Send messages to users on various channels.

### spawn
Create subagents to handle complex background tasks.

### cron
Schedule and manage timed tasks and reminders.

## Configuration

- **Platform**: Linux x86_64, Python 3.12.3
- **Workspace**: /root/.nanobot/workspace
- **Default Timezone**: Asia/Kolkata (IST, UTC+5:30)
- **Primary Language**: English
- **Communication Channel**: Telegram
- **Telegram Bot Token**: Configured and active

## Memory System

- **Long-term Memory**: `/root/.nanobot/workspace/memory/MEMORY.md`
- **Daily Notes**: `/root/.nanobot/workspace/memory/YYYY-MM-DD.md`
- **User Preferences**: Stored in USER.md
- **Agent Configuration**: Managed in AGENTS.md and SOUL.md

## Security & Privacy

- All operations are executed with user consent
- File system access is confined to workspace unless explicitly directed
- User data is stored locally and securely
- No data is shared externally without explicit instruction