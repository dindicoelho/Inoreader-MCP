#!/usr/bin/env python3
"""
Simple MCP Server implementation for Inoreader integration
"""
import asyncio
import json
import sys
import logging
from typing import Dict, List, Any, Optional
from jsonrpc_base import Dispatcher, ProtocolError, JSONRPCResponseManager
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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPServer:
    def __init__(self):
        self.dispatcher = Dispatcher()
        self._setup_handlers()
        
    def _setup_handlers(self):
        """Setup JSON-RPC handlers"""
        self.dispatcher.add_method(self.initialize, name="initialize")
        self.dispatcher.add_method(self.list_tools, name="tools/list")
        self.dispatcher.add_method(self.call_tool, name="tools/call")
        
    async def initialize(self, **kwargs):
        """Initialize the MCP server"""
        return {
            "protocolVersion": "0.1.0",
            "serverInfo": {
                "name": "inoreader-mcp",
                "version": "1.0.0"
            },
            "capabilities": {
                "tools": {}
            }
        }
        
    async def list_tools(self):
        """List available tools"""
        return {
            "tools": [
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
        }
        
    async def call_tool(self, name: str, arguments: Optional[Dict] = None):
        """Call a tool"""
        if arguments is None:
            arguments = {}
            
        try:
            logger.info(f"Calling tool: {name} with arguments: {arguments}")
            
            # Route to appropriate tool
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
                
            return {
                "content": [
                    {
                        "type": "text",
                        "text": result
                    }
                ]
            }
            
        except Exception as e:
            logger.error(f"Error in tool {name}: {str(e)}", exc_info=True)
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error: {str(e)}"
                    }
                ],
                "isError": True
            }
            
    async def handle_request(self, request_str: str) -> str:
        """Handle a JSON-RPC request"""
        try:
            response = JSONRPCResponseManager.handle(request_str, self.dispatcher)
            return response.json
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            return json.dumps({
                "jsonrpc": "2.0",
                "error": {
                    "code": -32603,
                    "message": str(e)
                },
                "id": None
            })
            
    async def run(self):
        """Run the MCP server on stdin/stdout"""
        logger.info("Starting Inoreader MCP server...")
        
        reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(reader)
        
        await asyncio.get_event_loop().connect_read_pipe(
            lambda: protocol, sys.stdin
        )
        
        while True:
            try:
                # Read a line from stdin
                line = await reader.readline()
                if not line:
                    break
                    
                request = line.decode().strip()
                if not request:
                    continue
                    
                logger.debug(f"Received request: {request}")
                
                # Handle the request
                response = await self.handle_request(request)
                
                # Write response to stdout
                print(response)
                sys.stdout.flush()
                
            except KeyboardInterrupt:
                logger.info("Server stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}", exc_info=True)
                
async def main():
    """Main entry point"""
    server = MCPServer()
    await server.run()
    
if __name__ == "__main__":
    asyncio.run(main())