#!/usr/bin/env python3
"""
Simple MCP Server for Inoreader - Compatible with Claude Desktop
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

# Configure logging to stderr so it appears in Claude logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

class SimpleMCPServer:
    def __init__(self):
        self.tools = self._get_tools_definition()
        
    def _get_tools_definition(self):
        """Define available tools"""
        return [
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
        
    async def handle_initialize(self, request_id: Any, params: Dict) -> Dict:
        """Handle initialize request"""
        logger.info("Handling initialize request")
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "0.1.0",
                "serverInfo": {
                    "name": "inoreader-mcp",
                    "version": "1.0.0"
                },
                "capabilities": {
                    "tools": {}
                }
            }
        }
        
    async def handle_list_tools(self, request_id: Any) -> Dict:
        """Handle tools/list request"""
        logger.info("Handling list tools request")
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": self.tools
            }
        }
        
    async def handle_call_tool(self, request_id: Any, tool_name: str, arguments: Dict) -> Dict:
        """Handle tools/call request"""
        logger.info(f"Handling tool call: {tool_name} with args: {arguments}")
        
        try:
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
                
            return {
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
            return {
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
            
    async def handle_request(self, request: Dict) -> Dict:
        """Handle a JSON-RPC request"""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        logger.info(f"Received request: {method}")
        
        if method == "initialize":
            return await self.handle_initialize(request_id, params)
        elif method == "tools/list":
            return await self.handle_list_tools(request_id)
        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            return await self.handle_call_tool(request_id, tool_name, arguments)
        else:
            logger.error(f"Unknown method: {method}")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }
            
    async def run(self):
        """Run the MCP server on stdin/stdout"""
        logger.info("Starting Inoreader MCP server...")
        
        reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(reader)
        
        try:
            await asyncio.get_event_loop().connect_read_pipe(
                lambda: protocol, sys.stdin
            )
            
            while True:
                try:
                    # Read a line from stdin
                    line = await reader.readline()
                    if not line:
                        logger.info("No more input, shutting down")
                        break
                        
                    # Decode and parse JSON-RPC request
                    request_str = line.decode().strip()
                    if not request_str:
                        continue
                        
                    logger.debug(f"Raw request: {request_str}")
                    
                    try:
                        request = json.loads(request_str)
                    except json.JSONDecodeError as e:
                        logger.error(f"Invalid JSON: {e}")
                        continue
                        
                    # Handle the request
                    response = await self.handle_request(request)
                    
                    # Send response
                    response_str = json.dumps(response)
                    logger.debug(f"Sending response: {response_str}")
                    print(response_str, flush=True)
                    
                except KeyboardInterrupt:
                    logger.info("Server stopped by user")
                    break
                except Exception as e:
                    logger.error(f"Error in main loop: {e}", exc_info=True)
                    
        except Exception as e:
            logger.error(f"Failed to setup server: {e}", exc_info=True)
            raise
            
async def main():
    """Main entry point"""
    try:
        server = SimpleMCPServer()
        await server.run()
    except Exception as e:
        logger.error(f"Server crashed: {e}", exc_info=True)
        sys.exit(1)
        
if __name__ == "__main__":
    logger.info("Starting Inoreader MCP server process...")
    asyncio.run(main())