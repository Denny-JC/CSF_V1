import requests
import json
from datetime import datetime

# Load config
with open('config.json', 'r') as f:
    config = json.load(f)

webhook_url = config.get('discord', {}).get('webhook_url')

if not webhook_url or 'YOUR_WEBHOOK_URL' in webhook_url:
    print("❌ Discord webhook URL not configured!")
    print("Please add your webhook URL to config.json")
    exit(1)

# Create test embed
embed = {
    "title": "🎯 CSFloat Snipe Found! (TEST)",
    "description": "**AK-47 | Redline (Field-Tested)**",
    "color": 3066993,  # Green color
    "fields": [
        {
            "name": "💰 Price",
            "value": "$12.50",
            "inline": True
        },
        {
            "name": "📊 Discount",
            "value": "25.00%",
            "inline": True
        },
        {
            "name": "🎲 Float",
            "value": "0.150000",
            "inline": True
        }
    ],
    "url": "https://csfloat.com",
    "timestamp": datetime.now().isoformat(),
    "footer": {
        "text": "This is a test notification! 🧪"
    }
}

payload = {
    "content": "🧪 Testing Discord notifications...",
    "embeds": [embed]
}

try:
    print("Sending test notification to Discord...")
    response = requests.post(webhook_url, json=payload)
    response.raise_for_status()
    print("✅ Discord notification sent successfully!")
    print("Check your Discord channel for the test message.")
except requests.exceptions.HTTPError as e:
    print(f"❌ Failed to send Discord notification!")
    print(f"Error: {e}")
    if e.response is not None:
        print(f"Response: {e.response.text}")
except Exception as e:
    print(f"❌ Error: {e}")
