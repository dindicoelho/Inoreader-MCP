#!/usr/bin/env python3
import asyncio
from config import Config
from inoreader_client import InoreaderClient

async def test_connection():
    try:
        # Validate config
        Config.validate()
        print("✓ Configuration loaded successfully")
        
        # Test connection
        async with InoreaderClient() as client:
            print("✓ Authentication successful")
            
            # Try to get feeds
            feeds = await client.get_subscription_list()
            print(f"✓ Connection working! You have {len(feeds)} feeds")
            
            # Show first 3 feeds
            for i, feed in enumerate(feeds[:3]):
                print(f"  - {feed.get('title', 'No title')}")
            
            if len(feeds) > 3:
                print(f"  ... and {len(feeds) - 3} more feeds")
                
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        print("\nCheck:")
        print("1. If you created the .env file")
        print("2. If credentials are correct")
        print("3. If your Inoreader account is active")

if __name__ == "__main__":
    asyncio.run(test_connection())