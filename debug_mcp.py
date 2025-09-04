#!/usr/bin/env python3
"""
Debug script to test what's happening when Claude calls the tools
"""
import asyncio
import sys
import logging
from config import Config
from tools import list_articles_tool, search_articles_tool

# Enable debug logging
logging.basicConfig(level=logging.DEBUG, stream=sys.stderr)
logger = logging.getLogger(__name__)

async def debug_tools():
    try:
        Config.validate()
        print("✓ Configuration validated")
        
        # Test the exact same call that Claude is making
        print("\n=== Testing list_articles_tool(limit=20, days=7) ===")
        try:
            result = await list_articles_tool(limit=20, days=7)
            print(f"SUCCESS: {result[:200]}...")
        except Exception as e:
            print(f"ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            
        print("\n=== Testing search_articles_tool(query='tecnologia', days=7) ===")
        try:
            result = await search_articles_tool(query="tecnologia", days=7)
            print(f"SUCCESS: {result[:200]}...")
        except Exception as e:
            print(f"ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            
        print("\n=== Testing with no parameters ===")
        try:
            result = await list_articles_tool()
            print(f"SUCCESS: {result[:200]}...")
        except Exception as e:
            print(f"ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            
    except Exception as e:
        print(f"✗ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_tools())