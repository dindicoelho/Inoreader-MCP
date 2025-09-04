#!/usr/bin/env python3
import asyncio
import logging
from config import Config
from inoreader_client import InoreaderClient

# Enable debug logging
logging.basicConfig(level=logging.DEBUG, stream=sys.stderr if 'sys' in globals() else None)

async def test_articles():
    try:
        Config.validate()
        
        async with InoreaderClient() as client:
            print("✓ Authentication successful")
            
            # Test getting stream contents (all unread articles)
            print("\nTesting stream contents...")
            result = await client.get_stream_contents(count=10, exclude_read=True)
            
            print(f"Response type: {type(result)}")
            
            if isinstance(result, dict):
                print(f"Keys in response: {list(result.keys())}")
                items = result.get('items', [])
                print(f"Number of items: {len(items)}")
                
                if items:
                    first_item = items[0]
                    print(f"First item keys: {list(first_item.keys())}")
                    print(f"First item title: {first_item.get('title', 'No title')}")
                else:
                    print("No items found")
            else:
                print(f"Unexpected response format: {result[:500] if isinstance(result, str) else result}")
                
            # Test search
            print("\nTesting search...")
            search_result = await client.search("technology", count=5)
            print(f"Search response type: {type(search_result)}")
            
            if isinstance(search_result, dict):
                search_items = search_result.get('items', [])
                print(f"Search items found: {len(search_items)}")
            else:
                print(f"Search unexpected response: {search_result[:200] if isinstance(search_result, str) else search_result}")
                
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import sys
    asyncio.run(test_articles())