#!/usr/bin/env python3
"""
Minimal MCP server for Inoreader - Based on working examples
"""
import asyncio
import json
import sys
import logging
from typing import Dict, Any
from config import Config
from tools import list_feeds_tool, list_articles_tool, search_articles_tool

# Configure logging
logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger(__name__)

class MinimalMCPServer:
    def __init__(self):
        pass
        
    async def send_response(self, response: Dict[str, Any]):
        """Send JSON response to stdout"""
        json_str = json.dumps(response)
        print(json_str, flush=True)
        
    async def handle_message(self, message: Dict[str, Any]):
        """Handle incoming message"""
        method = message.get("method", "")
        params = message.get("params", {})
        msg_id = message.get("id", 0)
        
        logger.info(f"Received method: {method}")
        
        try:
            if method == "initialize":
                await self.handle_initialize(msg_id, params)
            elif method == "tools/list":
                await self.handle_list_tools(msg_id)
            elif method == "tools/call":
                await self.handle_call_tool(msg_id, params)
            else:
                await self.send_error(msg_id, -32601, f"Unknown method: {method}")
                
        except Exception as e:
            logger.error(f"Error handling {method}: {e}", exc_info=True)
            await self.send_error(msg_id, -32603, str(e))
            
    async def handle_initialize(self, msg_id: Any, params: Dict):
        """Handle initialize"""
        response = {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "inoreader-mcp",
                    "version": "1.0.0"
                }
            }
        }
        await self.send_response(response)
        
    async def handle_list_tools(self, msg_id: Any):
        """List available tools"""
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
                "description": "List recent articles with optional filters",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer", 
                            "description": "Number of articles to return (default: 20)"
                        },
                        "days": {
                            "type": "integer",
                            "description": "Articles from last N days (default: 7)"
                        }
                    },
                    "required": []
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
                        "days": {
                            "type": "integer",
                            "description": "Search within the last N days (default: 7)"
                        }
                    },
                    "required": ["query"]
                }
            }
        ]
        
        response = {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "tools": tools
            }
        }
        await self.send_response(response)
        
    async def handle_call_tool(self, msg_id: Any, params: Dict):
        """Handle tool call"""
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})
        
        logger.info(f"Calling tool: {tool_name}")
        
        try:
            if tool_name == "inoreader_list_feeds":
                result = await list_feeds_tool()
            elif tool_name == "inoreader_list_articles":
                # Use safer defaults
                limit = arguments.get("limit", 20)
                days = arguments.get("days", 7)
                result = await list_articles_tool(limit=limit, days=days)
            elif tool_name == "inoreader_search":
                query = arguments.get("query", "")
                days = arguments.get("days", 7)
                result = await search_articles_tool(query=query, days=days)
            else:
                raise ValueError(f"Unknown tool: {tool_name}")
                
            response = {
                "jsonrpc": "2.0", 
                "id": msg_id,
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
            logger.error(f"Tool error: {e}")
            response = {
                "jsonrpc": "2.0",
                "id": msg_id, 
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
            
        await self.send_response(response)
        
    async def send_error(self, msg_id: Any, code: int, message: str):
        """Send error response"""
        response = {
            "jsonrpc": "2.0",
            "id": msg_id,
            "error": {
                "code": code,
                "message": message
            }
        }
        await self.send_response(response)
        
    async def run(self):
        """Main server loop"""
        logger.info("Starting minimal MCP server...")
        
        # Read from stdin
        reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(reader)
        
        await asyncio.get_event_loop().connect_read_pipe(
            lambda: protocol, sys.stdin
        )
        
        while True:
            try:
                line = await reader.readline()
                if not line:
                    break
                    
                line_str = line.decode().strip()
                if not line_str:
                    continue
                    
                try:
                    message = json.loads(line_str)
                    await self.handle_message(message)
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON: {line_str}")
                    
            except Exception as e:
                logger.error(f"Server loop error: {e}")
                
async def main():
    server = MinimalMCPServer()
    await server.run()
    
if __name__ == "__main__":
    asyncio.run(main())
