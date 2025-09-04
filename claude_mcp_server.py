#!/usr/bin/env python3
"""
MCP Server for Inoreader - Fully compatible with Claude Desktop
"""
import asyncio
import json
import sys
import logging
from typing import Dict, List, Any, Optional
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

# Configure logging to stderr
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

class ClaudeMCPServer:
    def __init__(self):
        self.reader = None
        self.writer = None
        
    async def send_message(self, message: Dict):
        """Send a JSON-RPC message to stdout"""
        message_str = json.dumps(message)
        print(message_str, flush=True)
        logger.debug(f"Sent: {message_str}")
        
    async def handle_initialize(self, request_id: Any, params: Dict):
        """Handle the initialize request"""
        response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2024-11-05",  # Use standard MCP version
                "serverInfo": {
                    "name": "inoreader-mcp",
                    "version": "1.0.0"
                },
                "capabilities": {
                    "tools": {}
                }
            }
        }
        await self.send_message(response)
        
    async def handle_tools_list(self, request_id: Any):
        """Handle tools/list request"""
        tools = [
            {
                "name": "inoreader_list_feeds",
                "description": "List all subscribed feeds in Inoreader",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "inoreader_list_articles",
                "description": "List articles from feeds with optional filters",
                "inputSchema": {
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
            },
            {
                "name": "inoreader_get_content",
                "description": "Get the full content of a specific article",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "article_id": {
                            "type": "string",
                            "description": "The ID of the article to retrieve"
                        }
                    },
                    "required": ["article_id"]
                }
            },
            {
                "name": "inoreader_mark_as_read",
                "description": "Mark articles as read",
                "inputSchema": {
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
            },
            {
                "name": "inoreader_search",
                "description": "Search for articles by keyword",
                "inputSchema": {
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
            },
            {
                "name": "inoreader_summarize",
                "description": "Generate a summary of an article",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "article_id": {
                            "type": "string",
                            "description": "The ID of the article to summarize"
                        }
                    },
                    "required": ["article_id"]
                }
            },
            {
                "name": "inoreader_analyze",
                "description": "Analyze multiple articles for trends, sentiment, or keywords",
                "inputSchema": {
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
            },
            {
                "name": "inoreader_get_stats",
                "description": "Get statistics about unread articles",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        ]
        
        response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": tools
            }
        }
        await self.send_message(response)
        
    async def handle_tools_call(self, request_id: Any, tool_name: str, arguments: Dict):
        """Handle tools/call request"""
        try:
            logger.info(f"Calling tool: {tool_name} with args: {arguments}")
            
            # Validate configuration
            Config.validate()
            
            # Route to appropriate tool
            if tool_name == "inoreader_list_feeds":
                result = await list_feeds_tool()
            elif tool_name == "inoreader_list_articles":
                result = await list_articles_tool(**arguments)
            elif tool_name == "inoreader_get_content":
                result = await get_content_tool(**arguments)
            elif tool_name == "inoreader_mark_as_read":
                result = await mark_as_read_tool(**arguments)
            elif tool_name == "inoreader_search":
                result = await search_articles_tool(**arguments)
            elif tool_name == "inoreader_summarize":
                result = await summarize_article_tool(**arguments)
            elif tool_name == "inoreader_analyze":
                result = await analyze_articles_tool(**arguments)
            elif tool_name == "inoreader_get_stats":
                result = await get_stats_tool()
            else:
                raise ValueError(f"Unknown tool: {tool_name}")
                
            response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": result
                        }
                    ]
                }
            }
            
        except Exception as e:
            logger.error(f"Error in tool {tool_name}: {str(e)}", exc_info=True)
            response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Error: {str(e)}"
                        }
                    ],
                    "isError": True
                }
            }
            
        await self.send_message(response)
        
    async def handle_message(self, message: Dict):
        """Handle incoming JSON-RPC message"""
        method = message.get("method")
        params = message.get("params", {})
        request_id = message.get("id")
        
        logger.info(f"Handling method: {method}")
        
        if method == "initialize":
            await self.handle_initialize(request_id, params)
        elif method == "tools/list":
            await self.handle_tools_list(request_id)
        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            await self.handle_tools_call(request_id, tool_name, arguments)
        else:
            # Send error for unknown method
            error_response = {
                "jsonrpc": "2.0",
                "id": request_id if request_id is not None else 0,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }
            await self.send_message(error_response)
            
    async def run(self):
        """Main server loop"""
        logger.info("Starting Inoreader MCP server...")
        
        # Set up stdin reader
        reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(reader)
        await asyncio.get_event_loop().connect_read_pipe(
            lambda: protocol, sys.stdin
        )
        
        try:
            while True:
                # Read line from stdin
                line = await reader.readline()
                if not line:
                    logger.info("No more input, shutting down")
                    break
                    
                # Parse JSON-RPC message
                try:
                    message_str = line.decode().strip()
                    if not message_str:
                        continue
                        
                    logger.debug(f"Received: {message_str}")
                    message = json.loads(message_str)
                    
                    # Handle the message
                    await self.handle_message(message)
                    
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON: {e}")
                except Exception as e:
                    logger.error(f"Error handling message: {e}", exc_info=True)
                    
        except asyncio.CancelledError:
            logger.info("Server cancelled")
        except Exception as e:
            logger.error(f"Server error: {e}", exc_info=True)
            
async def main():
    """Entry point"""
    try:
        server = ClaudeMCPServer()
        await server.run()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
        
if __name__ == "__main__":
    asyncio.run(main())