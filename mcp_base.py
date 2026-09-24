#!/usr/bin/env python3
"""
Base Model Context Protocol (MCP) Server Implementation over JSON-RPC 2.0 stdio.
Compatible with Claude Desktop, Cursor, Antigravity, and Gemini CLI.
"""
from __future__ import annotations
import sys
import json
import traceback
import inspect
from typing import Callable, Any, Dict, List

class MCPServer:
    def __init__(self, name: str, version: str = "1.0.0"):
        self.name = name
        self.version = version
        self.tools: Dict[str, Dict[str, Any]] = {}
        self.handlers: Dict[str, Callable] = {}

    def tool(self, name: str, description: str, input_schema: Dict[str, Any]):
        """Decorator to register a tool with its schema."""
        def decorator(func: Callable):
            self.tools[name] = {
                "name": name,
                "description": description,
                "inputSchema": input_schema
            }
            self.handlers[name] = func
            return func
        return decorator

    def _invoke_handler(self, func: Callable, arguments: Dict[str, Any]) -> Any:
        sig = inspect.signature(func)
        has_var_keyword = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values())
        if has_var_keyword:
            return func(**arguments)
        else:
            filtered_args = {k: v for k, v in arguments.items() if k in sig.parameters}
            return func(**filtered_args)

    def call_tool_direct(self, name: str, arguments: Dict[str, Any]) -> Any:
        """Call a tool directly in Python for testing and verification."""
        if name not in self.handlers:
            raise ValueError(f"Tool {name} not found on server {self.name}")
        return self._invoke_handler(self.handlers[name], arguments)

    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any] | None:
        """Handle incoming JSON-RPC request."""
        req_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": self.name,
                        "version": self.version
                    }
                }
            }

        elif method == "notifications/initialized":
            return None

        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "tools": list(self.tools.values())
                }
            }

        elif method == "tools/call":
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})
            if tool_name not in self.handlers:
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method/Tool '{tool_name}' not found"
                    }
                }
            try:
                res = self._invoke_handler(self.handlers[tool_name], tool_args)
                text_output = json.dumps(res, indent=2, ensure_ascii=False, default=str)
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": text_output
                            }
                        ],
                        "isError": False
                    }
                }
            except Exception as e:
                err_msg = f"Error executing tool '{tool_name}': {str(e)}\n{traceback.format_exc()}"
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": err_msg
                            }
                        ],
                        "isError": True
                    }
                }

        elif method == "ping":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {}
            }

        else:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": -32601,
                    "message": f"Method '{method}' not supported"
                }
            }

    def run(self):
        """Run standard stdio JSON-RPC loop."""
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                req = json.loads(line)
                resp = self.handle_request(req)
                if resp is not None:
                    sys.stdout.write(json.dumps(resp) + "\n")
                    sys.stdout.flush()
            except json.JSONDecodeError:
                err_resp = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32700,
                        "message": "Parse error: Invalid JSON"
                    }
                }
                sys.stdout.write(json.dumps(err_resp) + "\n")
                sys.stdout.flush()
            except Exception as e:
                err_resp = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    }
                }
                sys.stdout.write(json.dumps(err_resp) + "\n")
                sys.stdout.flush()
