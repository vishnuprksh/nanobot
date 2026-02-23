#!/usr/bin/env python3
"""
Test script for Firebase submission with 3-4 sample apps
"""

import json
import time
from datetime import datetime
import sys
import os

# Add the current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the submitter
from firebase_submitter import FirebaseSubmitter

def create_test_apps():
    """Create 3-4 test apps for trial submission"""
    test_apps = [
        {
            "name": "ThinkNotes",
            "description": "Your personal second brain application for note-taking and task management",
            "url": "https://thinknotes.app",
            "tags": ["note-taking", "task-management", "second-brain"],
            "source": "Reddit - r/secondbrain"
        },
        {
            "name": "Obsidian",
            "description": "A powerful knowledge base that works on local Markdown files",
            "url": "https://obsidian.md",
            "tags": ["markdown", "knowledge-base", "graph-view", "plugins"],
            "source": "Reddit - r/PKMS"
        },
        {
            "name": "Logseq",
            "description": "A privacy-first, open-source platform for knowledge management and collaboration",
            "url": "https://logseq.com",
            "tags": ["open-source", "outliner", "backlinks", "privacy"],
            "source": "Reddit - r/logseq"
        },
        {
            "name": "Heptabase",
            "description": "Visual knowledge mapping tool with whiteboards and card-based notes",
            "url": "https://heptabase.com",
            "tags": ["visual", "whiteboard", "knowledge-mapping", "cards"],
            "source": "Reddit - r/secondbrain"
        }
    ]
    return test_apps

def run_trial():
    """Run trial submission with 3-4 apps"""
    print("=" * 60)
    print("Firebase Submission Trial Run")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Initialize submitter
    submitter = FirebaseSubmitter()
    
    # Create test apps
    test_apps = create_test_apps()
    print(f"Created {len(test_apps)} test apps for submission")
    
    # Submit each app
    results = []
    for i, app in enumerate(test_apps, 1):
        print(f"\n[{i}/{len(test_apps)}] Processing: {app['name']}")
        
        # Format the app data
        formatted_app = submitter.format_tool_data(app)
        
        # Check for duplicates
        if submitter.is_duplicate(formatted_app):
            print(f"  ⚠️  Duplicate detected, skipping: {app['name']}")
            continue
        
        # Submit to Firebase
        print(f"  📤 Submitting to Firebase...")
        result = submitter.submit_to_firebase(formatted_app)
        
        if result.get('success'):
            print(f"  ✅ Successfully submitted: {app['name']}")
        else:
            print(f"  ❌ Failed to submit: {app['name']}")
            print(f"     Error: {result.get('error', 'Unknown error')}")
        
        results.append(result)
        
        # Small delay between submissions
        time.sleep(2)
    
    # Print summary
    print("\n" + "=" * 60)
    print("TRIAL RUN SUMMARY")
    print("=" * 60)
    
    successful = sum(1 for r in results if r.get('success'))
    failed = len(results) - successful
    
    print(f"Total apps processed: {len(results)}")
    print(f"Successfully submitted: {successful}")
    print(f"Failed submissions: {failed}")
    
    if successful > 0:
        print("\n✅ Successfully submitted:")
        for r in results:
            if r.get('success'):
                print(f"  • {r['tool']}")
    
    if failed > 0:
        print("\n❌ Failed submissions:")
        for r in results:
            if not r.get('success'):
                print(f"  • {r['tool']}: {r.get('error', 'Unknown error')}")
    
    print("\n" + "=" * 60)
    print("Trial run completed")
    print("=" * 60)
    
    # Save results to file
    trial_file = f"/root/.nanobot/workspace/trial_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(trial_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'apps_tested': len(test_apps),
            'successful': successful,
            'failed': failed,
            'results': results,
            'test_apps': test_apps
        }, f, indent=2)
    
    print(f"\nResults saved to: {trial_file}")
    
    return results

if __name__ == "__main__":
    run_trial()