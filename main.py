#!/usr/bin/env python3
import asyncio
import logging
from mcp.server import Server
from mcp.types import Tool, TextContent
from config import Config
from tools import (
    list_feeds_tool,
    list_articles_tool,
    get_content_tool,
    mark_as_read_tool,
    search_articles_tool,
    summarize_article_tool,
    analyze_articles_tool,
    get_stats_tool
)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create the MCP server
server = Server("inoreader-mcp")

# Tool definitions
TOOLS = [
    Tool(
        name="inoreader_list_feeds",
        description="List all subscribed feeds in Inoreader",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": []
        }
    ),
    Tool(
        name="inoreader_list_articles",
        description="List articles from feeds with optional filters",
        inputSchema={
            "type": "object",
            "properties": {
                "feed_id": {
                    "type": "string",
                    "description": "Optional feed ID to filter articles"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of articles to return (default: 50)"
                },
                "unread_only": {
                    "type": "boolean",
                    "description": "Only show unread articles (default: true)"
                },
                "days": {
                    "type": "integer",
                    "description": "Only show articles from the last N days"
                }
            },
            "required": []
        }
    ),
    Tool(
        name="inoreader_get_content",
        description="Get the full content of a specific article",
        inputSchema={
            "type": "object",
            "properties": {
                "article_id": {
                    "type": "string",
                    "description": "The ID of the article to retrieve"
                }
            },
            "required": ["article_id"]
        }
    ),
    Tool(
        name="inoreader_mark_as_read",
        description="Mark articles as read",
        inputSchema={
            "type": "object",
            "properties": {
                "article_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of article IDs to mark as read"
                }
            },
            "required": ["article_ids"]
        }
    ),
    Tool(
        name="inoreader_search",
        description="Search for articles by keyword",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results (default: 50)"
                },
                "days": {
                    "type": "integer",
                    "description": "Search within the last N days"
                }
            },
            "required": ["query"]
        }
    ),
    Tool(
        name="inoreader_summarize",
        description="Generate a summary of an article",
        inputSchema={
            "type": "object",
            "properties": {
                "article_id": {
                    "type": "string",
                    "description": "The ID of the article to summarize"
                }
            },
            "required": ["article_id"]
        }
    ),
    Tool(
        name="inoreader_analyze",
        description="Analyze multiple articles for trends, sentiment, or keywords",
        inputSchema={
            "type": "object",
            "properties": {
                "article_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of article IDs to analyze"
                },
                "analysis_type": {
                    "type": "string",
                    "enum": ["summary", "trends", "sentiment", "keywords"],
                    "description": "Type of analysis to perform"
                }
            },
            "required": ["article_ids", "analysis_type"]
        }
    ),
    Tool(
        name="inoreader_get_stats",
        description="Get statistics about unread articles",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": []
        }
    )
]

@server.list_tools()
async def list_tools():
    """List available tools"""
    return TOOLS

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    """Handle tool calls"""
    try:
        logger.info(f"Tool called: {name} with arguments: {arguments}")
        
        # Validate configuration
        Config.validate()
        
        # Route to appropriate tool handler
        if name == "inoreader_list_feeds":
            result = await list_feeds_tool()
        elif name == "inoreader_list_articles":
            result = await list_articles_tool(**arguments)
        elif name == "inoreader_get_content":
            result = await get_content_tool(**arguments)
        elif name == "inoreader_mark_as_read":
            result = await mark_as_read_tool(**arguments)
        elif name == "inoreader_search":
            result = await search_articles_tool(**arguments)
        elif name == "inoreader_summarize":
            result = await summarize_article_tool(**arguments)
        elif name == "inoreader_analyze":
            result = await analyze_articles_tool(**arguments)
        elif name == "inoreader_get_stats":
            result = await get_stats_tool()
        else:
            raise ValueError(f"Unknown tool: {name}")
            
        return [TextContent(type="text", text=result)]
        
    except Exception as e:
        logger.error(f"Error in tool {name}: {str(e)}", exc_info=True)
        return [TextContent(type="text", text=f"Error: {str(e)}")]

async def main():
    """Main entry point"""
    try:
        logger.info("Starting Inoreader MCP server...")
        
        # Run the server using stdin/stdout
        async with server:
            await server.run()
            
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    asyncio.run(main())