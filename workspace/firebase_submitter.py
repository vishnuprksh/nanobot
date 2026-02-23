#!/usr/bin/env python3
"""
Firebase app submitter for FindYourSecondBrain directory
Enhances the Reddit monitor to automatically submit new tools
"""

import json
import os
import sys
import time
import logging
from datetime import datetime
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/root/.nanobot/workspace/firebase_submitter.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class FirebaseSubmitter:
    def __init__(self):
        """Initialize Firebase submitter"""
        self.firebase_config = {
            "apiKey": "AIzaSyCLeY68ONelcMBG3AcZLZJnWHD4QqXKmZw",
            "authDomain": "findyoursecondbrain.firebaseapp.com",
            "projectId": "findyoursecondbrain",
            "storageBucket": "findyoursecondbrain.firebasestorage.app",
            "messagingSenderId": "686559526039",
            "appId": "1:686559526039:web:47a2f60e5b8a65ab5e7dd2",
            "measurementId": "G-B1FWVYXZND"
        }
        
        self.submit_url = "https://us-central1-findyoursecondbrain.cloudfunctions.net/submitApp"
        self.data_file = "/root/.nanobot/workspace/reddit_tools.json"
        self.submitted_file = "/root/.nanobot/workspace/submitted_tools.json"
        self.token = None
        self.token_expiry = None
        
        # Initialize submitted tools tracking
        self.load_submitted_tools()
        
    def load_submitted_tools(self):
        """Load previously submitted tools to avoid duplicates"""
        if os.path.exists(self.submitted_file):
            try:
                with open(self.submitted_file, 'r') as f:
                    self.submitted_tools = json.load(f)
                logger.info(f"Loaded {len(self.submitted_tools)} previously submitted tools")
            except Exception as e:
                logger.error(f"Error loading submitted tools: {e}")
                self.submitted_tools = {}
        else:
            self.submitted_tools = {}
            logger.info("No previously submitted tools found, starting fresh")
    
    def save_submitted_tools(self):
        """Save submitted tools to file"""
        try:
            with open(self.submitted_file, 'w') as f:
                json.dump(self.submitted_tools, f, indent=2)
            logger.info(f"Saved {len(self.submitted_tools)} submitted tools to file")
        except Exception as e:
            logger.error(f"Error saving submitted tools: {e}")
    
    def get_firebase_token(self):
        """Get Firebase anonymous authentication token using REST API"""
        try:
            # Firebase anonymous auth REST API endpoint
            auth_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp"
            
            # Request body with API key
            data = {
                "returnSecureToken": True
            }
            
            # Make request to get anonymous token
            response = requests.post(
                f"{auth_url}?key={self.firebase_config['apiKey']}",
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                self.token = result.get('idToken')
                self.token_expiry = time.time() + int(result.get('expiresIn', 3600))
                logger.info("Successfully obtained Firebase anonymous token")
                return self.token
            else:
                logger.error(f"Failed to get Firebase token: HTTP {response.status_code}")
                # Fallback to simple token for testing
                import uuid
                self.token = f"test_token_{uuid.uuid4()}"
                self.token_expiry = time.time() + 3600
                logger.info(f"Using test token: {self.token[:20]}...")
                return self.token
                
        except Exception as e:
            logger.error(f"Error getting Firebase token: {e}")
            # Fallback
            import uuid
            self.token = f"fallback_token_{uuid.uuid4()}"
            self.token_expiry = time.time() + 3600
            return self.token
    
    def is_duplicate(self, tool_data):
        """Check if tool has already been submitted"""
        # Check by URL (most reliable)
        url = tool_data.get('websiteUrl', '').lower().strip()
        if url in self.submitted_tools:
            logger.info(f"Tool with URL {url} already submitted")
            return True
        
        # Check by name (case-insensitive)
        name = tool_data.get('name', '').lower().strip()
        for submitted in self.submitted_tools.values():
            if submitted.get('name', '').lower().strip() == name:
                logger.info(f"Tool with name {name} already submitted")
                return True
        
        return False
    
    def format_tool_data(self, raw_tool):
        """Format raw tool data for Firebase submission"""
        # Extract or generate required fields
        name = raw_tool.get('name', 'Unknown Tool')
        description = raw_tool.get('description', '')
        url = raw_tool.get('url', '')
        
        # If no description, create one
        if not description:
            description = f"A second brain/PKMS tool mentioned in Reddit community"
        
        # Determine category based on description/tags
        category = "Other"
        if any(word in description.lower() for word in ['ai', 'artificial', 'intelligence', 'gpt', 'llm']):
            category = "AI"
        elif any(word in description.lower() for word in ['visual', 'graph', 'canvas', 'whiteboard']):
            category = "Visual"
        elif any(word in description.lower() for word in ['note', 'notes', 'writing']):
            category = "Note-taking"
        elif any(word in description.lower() for word in ['task', 'todo', 'project', 'management']):
            category = "Task Management"
        
        # Determine pricing
        pricing = "Free"
        if any(word in description.lower() for word in ['paid', 'premium', 'subscription', 'monthly', 'yearly']):
            pricing = "Paid"
        elif any(word in description.lower() for word in ['freemium', 'tier', 'plan']):
            pricing = "Freemium"
        
        # Extract tags from description or use defaults
        tags = raw_tool.get('tags', [])
        if not tags:
            tags = ["second-brain", "pkms", "productivity"]
            if category != "Other":
                tags.append(category.lower().replace('-', ''))
        
        # Ensure website URL is valid
        if not url.startswith(('http://', 'https://')):
            url = f"https://{url}" if url else "https://example.com"
        
        return {
            "name": name[:100],  # Limit name length
            "description": description[:500],  # Limit description length
            "websiteUrl": url,
            "tags": tags[:10],  # Limit to 10 tags
            "category": category,
            "pricing": pricing,
            "source": raw_tool.get('source', 'Reddit'),
            "discovered": datetime.now().isoformat()
        }
    
    def submit_to_firebase(self, tool_data):
        """Submit formatted tool data to Firebase"""
        try:
            # Get token if needed
            if not self.token or (self.token_expiry and time.time() > self.token_expiry):
                self.get_firebase_token()
            
            # Prepare headers
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.token}'
            }
            
            # Submit to Firebase
            logger.info(f"Submitting tool: {tool_data['name']}")
            response = requests.post(
                self.submit_url,
                json=tool_data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info(f"Successfully submitted {tool_data['name']}")
                
                # Mark as submitted
                url_key = tool_data['websiteUrl'].lower().strip()
                self.submitted_tools[url_key] = {
                    **tool_data,
                    'submitted_at': datetime.now().isoformat(),
                    'response': response.json() if response.text else {}
                }
                self.save_submitted_tools()
                
                return {
                    'success': True,
                    'tool': tool_data['name'],
                    'response': response.json() if response.text else {}
                }
            else:
                logger.error(f"Failed to submit {tool_data['name']}: HTTP {response.status_code}")
                return {
                    'success': False,
                    'tool': tool_data['name'],
                    'error': f"HTTP {response.status_code}",
                    'response': response.text[:200] if response.text else ""
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error submitting {tool_data['name']}: {e}")
            return {
                'success': False,
                'tool': tool_data['name'],
                'error': str(e)
            }
        except Exception as e:
            logger.error(f"Unexpected error submitting {tool_data['name']}: {e}")
            return {
                'success': False,
                'tool': tool_data['name'],
                'error': str(e)
            }
    
    def process_new_tools(self):
        """Process new tools from Reddit scraper and submit to Firebase"""
        if not os.path.exists(self.data_file):
            logger.error(f"Data file not found: {self.data_file}")
            return []
        
        try:
            # Load Reddit tools data
            with open(self.data_file, 'r') as f:
                reddit_data = json.load(f)
            
            # Get tools list
            tools = reddit_data.get('tools', [])
            if not tools:
                logger.info("No tools found in Reddit data")
                return []
            
            logger.info(f"Found {len(tools)} tools in Reddit data")
            
            # Process and submit new tools
            results = []
            new_tools_submitted = 0
            
            for tool in tools:
                # Format tool data
                formatted_tool = self.format_tool_data(tool)
                
                # Check for duplicates
                if self.is_duplicate(formatted_tool):
                    continue
                
                # Submit to Firebase
                result = self.submit_to_firebase(formatted_tool)
                results.append(result)
                
                if result.get('success'):
                    new_tools_submitted += 1
                
                # Small delay between submissions
                time.sleep(1)
            
            logger.info(f"Submitted {new_tools_submitted} new tools to Firebase")
            return results
            
        except Exception as e:
            logger.error(f"Error processing tools: {e}")
            return []
    
    def run_daily_submission(self):
        """Main function to run daily submission process"""
        logger.info("=" * 60)
        logger.info(f"Starting Firebase submission - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 60)
        
        # Process new tools
        results = self.process_new_tools()
        
        # Generate summary
        successful = sum(1 for r in results if r.get('success'))
        failed = len(results) - successful
        
        summary = {
            'timestamp': datetime.now().isoformat(),
            'total_processed': len(results),
            'successful': successful,
            'failed': failed,
            'results': results
        }
        
        # Save summary
        summary_file = f"/root/.nanobot/workspace/submission_summary_{datetime.now().strftime('%Y%m%d')}.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info("=" * 60)
        logger.info(f"Submission complete: {successful} successful, {failed} failed")
        logger.info("=" * 60)
        
        return summary

def main():
    """Main execution function"""
    try:
        submitter = FirebaseSubmitter()
        summary = submitter.run_daily_submission()
        
        # Print summary for cron logs
        print(f"Firebase submission complete: {summary['successful']} successful, {summary['failed']} failed")
        
        if summary['successful'] > 0:
            print(f"Successfully submitted: {[r['tool'] for r in summary['results'] if r.get('success')]}")
        
        if summary['failed'] > 0:
            print(f"Failed submissions: {[r['tool'] for r in summary['results'] if not r.get('success')]}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Fatal error in main: {e}")
        print(f"Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())