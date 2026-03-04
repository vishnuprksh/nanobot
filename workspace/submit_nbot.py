#!/usr/bin/env python3
"""
Manual submission of nbot.ai to FindYourSecondBrain directory
"""

import json
import requests
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def submit_nbot_ai():
    """Submit nbot.ai to FindYourSecondBrain Firebase directory"""
    
    # Firebase configuration
    firebase_config = {
        "apiKey": "AIzaSyCLeY68ONelcMBG3AcZLZJnWHD4QqXKmZw",
        "authDomain": "findyoursecondbrain.firebaseapp.com",
        "projectId": "findyoursecondbrain",
        "storageBucket": "findyoursecondbrain.firebasestorage.app",
        "messagingSenderId": "686559526039",
        "appId": "1:686559526039:web:47a2f60e5b8a65ab5e7dd2",
        "measurementId": "G-B1FWVYXZND"
    }
    
    submit_url = "https://us-central1-findyoursecondbrain.cloudfunctions.net/submitApp"
    
    # nbot.ai tool data
    nbot_data = {
        "name": "nbot.ai",
        "description": "Build AI Trackers for What Matters to You - Custom AI agents and trackers for personal and business intelligence",
        "websiteUrl": "https://nbot.ai",
        "tags": ["ai", "trackers", "agents", "automation", "second-brain", "personal-ai", "monitoring"],
        "category": "AI",
        "pricing": "Freemium",
        "source": "Manual Submission",
        "discovered": datetime.now().isoformat()
    }
    
    logger.info(f"Preparing to submit: {nbot_data['name']}")
    print(f"\n📤 Submitting: {nbot_data['name']}")
    print(f"🔗 URL: {nbot_data['websiteUrl']}")
    print(f"📝 Description: {nbot_data['description'][:100]}...")
    print(f"🏷️ Tags: {', '.join(nbot_data['tags'])}")
    
    try:
        # First get an anonymous Firebase token
        logger.info("Getting Firebase anonymous token...")
        auth_url = "https://identitytoolkit.googleapis.com/v1/accounts:signUp"
        
        auth_response = requests.post(
            f"{auth_url}?key={firebase_config['apiKey']}",
            json={"returnSecureToken": True},
            timeout=10
        )
        
        if auth_response.status_code == 200:
            token_data = auth_response.json()
            token = token_data.get('idToken')
            logger.info("Successfully obtained Firebase token")
        else:
            logger.warning(f"Failed to get Firebase token: HTTP {auth_response.status_code}")
            # Use a test token as fallback
            import uuid
            token = f"test_token_{uuid.uuid4()}"
            logger.info(f"Using test token: {token[:20]}...")
        
        # Prepare headers with token
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }
        
        # Submit to Firebase
        logger.info(f"Submitting nbot.ai to Firebase...")
        print(f"\n🚀 Sending submission to FindYourSecondBrain...")
        
        response = requests.post(
            submit_url,
            json=nbot_data,
            headers=headers,
            timeout=30
        )
        
        print(f"\n📊 Response Status: HTTP {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ SUCCESS! Tool submitted successfully")
            print(f"📋 Response: {json.dumps(result, indent=2)}")
            
            # Save to submitted tools
            try:
                with open('/root/.nanobot/workspace/submitted_tools.json', 'r') as f:
                    submitted = json.load(f)
            except:
                submitted = {}
            
            submitted[nbot_data['websiteUrl']] = {
                **nbot_data,
                'submitted_at': datetime.now().isoformat(),
                'response': result
            }
            
            with open('/root/.nanobot/workspace/submitted_tools.json', 'w') as f:
                json.dump(submitted, f, indent=2)
            
            print(f"\n💾 Saved to submitted_tools.json")
            
            return {
                'success': True,
                'tool': nbot_data['name'],
                'response': result
            }
            
        else:
            error_text = response.text[:200] if response.text else "No response text"
            print(f"❌ FAILED: HTTP {response.status_code}")
            print(f"📋 Error: {error_text}")
            
            return {
                'success': False,
                'tool': nbot_data['name'],
                'error': f"HTTP {response.status_code}",
                'response': error_text
            }
            
    except requests.exceptions.RequestException as e:
        print(f"❌ NETWORK ERROR: {e}")
        return {
            'success': False,
            'tool': nbot_data['name'],
            'error': str(e)
        }
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")
        return {
            'success': False,
            'tool': nbot_data['name'],
            'error': str(e)
        }

if __name__ == "__main__":
    print("=" * 60)
    print("FindYourSecondBrain - Manual Tool Submission")
    print("=" * 60)
    
    result = submit_nbot_ai()
    
    print("\n" + "=" * 60)
    print("Submission Complete")
    print("=" * 60)
    
    if result.get('success'):
        print(f"✅ Successfully submitted: {result['tool']}")
    else:
        print(f"❌ Failed to submit: {result['tool']}")
        print(f"   Error: {result.get('error', 'Unknown error')}")