#!/usr/bin/env python3
"""
Reddit Monitor for SecondBrain Tools Directory
Monitors r/secondbrain and r/PKMS for new AI/PKMS tools
Sends daily morning updates with new tools found
"""

import os
import json
import time
import requests
from datetime import datetime
from pathlib import Path
import logging

# Configuration
REDDIT_SUBREDDITS = ["secondbrain", "PKMS"]
CHECK_INTERVAL_HOURS = 24  # Run daily
DATA_FILE = "/root/.nanobot/workspace/reddit_tools.json"
LOG_FILE = "/root/.nanobot/workspace/reddit_monitor.log"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

class RedditMonitor:
    def __init__(self):
        self.tools_data = self.load_data()
        self.user_agent = "SecondBrainToolsMonitor/1.0"
        
    def load_data(self):
        """Load existing tools data from file"""
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logging.error(f"Error loading data: {e}")
                return {"tools": [], "last_check": None, "stats": {}}
        return {"tools": [], "last_check": None, "stats": {}}
    
    def save_data(self):
        """Save tools data to file"""
        try:
            with open(DATA_FILE, 'w') as f:
                json.dump(self.tools_data, f, indent=2)
            logging.info(f"Data saved to {DATA_FILE}")
        except Exception as e:
            logging.error(f"Error saving data: {e}")
    
    def fetch_reddit_posts(self, subreddit, limit=50):
        """Fetch recent posts from a subreddit"""
        url = f"https://www.reddit.com/r/{subreddit}/new.json?limit={limit}"
        headers = {"User-Agent": self.user_agent}
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logging.error(f"Error fetching from r/{subreddit}: {e}")
            return None
    
    def extract_tools_from_post(self, post):
        """Extract tool mentions from a post"""
        tools = []
        
        # Check title and text for tool mentions
        text = f"{post.get('title', '')} {post.get('selftext', '')}".lower()
        
        # Common tool patterns
        tool_patterns = [
            r'obsidian', r'notion', r'roam', r'logseq', r'tana', r'mem\.ai',
            r'heptabase', r'anytype', r'capacities', r'reflect\.app', r'evernote',
            r'onenote', r'bear', r'craft', r'remnote', r'scrintal', r'capacities',
            r'app\.', r'https?://', r'www\.', r'\.com', r'\.io', r'\.ai'
        ]
        
        # Extract URLs
        import re
        urls = re.findall(r'https?://[^\s\)\]\}]+', text)
        
        # Simple extraction - look for tool mentions
        for url in urls:
            # Clean URL
            url = url.rstrip('.,;!?)')
            tools.append({
                "url": url,
                "source_post": post.get('title', '')[:100],
                "subreddit": post.get('subreddit', ''),
                "post_id": post.get('id', ''),
                "found_at": datetime.now().isoformat()
            })
        
        return tools
    
    def process_subreddit(self, subreddit):
        """Process a subreddit for new tools"""
        logging.info(f"Processing r/{subreddit}")
        
        data = self.fetch_reddit_posts(subreddit)
        if not data:
            return []
        
        new_tools = []
        posts = data.get('data', {}).get('children', [])
        
        for post_data in posts:
            post = post_data.get('data', {})
            tools = self.extract_tools_from_post(post)
            
            for tool in tools:
                # Check if tool already exists
                if not self.tool_exists(tool):
                    new_tools.append(tool)
                    self.tools_data["tools"].append(tool)
        
        logging.info(f"Found {len(new_tools)} new tools in r/{subreddit}")
        return new_tools
    
    def tool_exists(self, tool):
        """Check if tool already exists in database"""
        for existing in self.tools_data["tools"]:
            if existing.get("url") == tool.get("url"):
                return True
        return False
    
    def generate_daily_report(self, new_tools):
        """Generate daily report message"""
        if not new_tools:
            return "No new tools found today."
        
        report = f"📋 **Daily PKMS Tools Update** ({datetime.now().strftime('%Y-%m-%d')})\n\n"
        report += f"Found {len(new_tools)} new tools:\n\n"
        
        for i, tool in enumerate(new_tools[:10], 1):  # Limit to 10
            report += f"{i}. **{tool.get('source_post', 'Tool')}**\n"
            report += f"   🔗 {tool.get('url', 'No URL')}\n"
            report += f"   📍 r/{tool.get('subreddit', 'unknown')}\n\n"
        
        if len(new_tools) > 10:
            report += f"... and {len(new_tools) - 10} more tools.\n"
        
        report += f"\n**Total tools in directory:** {len(self.tools_data['tools'])}"
        return report
    
    def run_daily_check(self):
        """Run daily check and return report"""
        logging.info("Starting daily Reddit check")
        
        all_new_tools = []
        for subreddit in REDDIT_SUBREDDITS:
            new_tools = self.process_subreddit(subreddit)
            all_new_tools.extend(new_tools)
        
        # Update stats
        self.tools_data["last_check"] = datetime.now().isoformat()
        self.tools_data["stats"][datetime.now().strftime("%Y-%m-%d")] = {
            "new_tools": len(all_new_tools),
            "subreddits_checked": REDDIT_SUBREDDITS
        }
        
        self.save_data()
        
        report = self.generate_daily_report(all_new_tools)
        logging.info(f"Daily check complete. New tools: {len(all_new_tools)}")
        
        return report

def main():
    """Main function for manual testing"""
    monitor = RedditMonitor()
    report = monitor.run_daily_check()
    print(report)

if __name__ == "__main__":
    main()