"""Apex_FDE_Matrix: Zero-Dependency JSON-RPC 2.0 MCP Server.

Provides Model Context Protocol (MCP) server endpoints over stdio and memory.
"""

from __future__ import annotations

import json
import sys
from typing import Any, Dict, Optional, TextIO

from apex_fde_matrix.mcp.tools import MCPToolRegistry


class MCPServer:
    """Standard Model Context Protocol server."""

    PROTOCOL_VERSION = "2024-11-05"
    SERVER_NAME = "Apex_FDE_Matrix"
    SERVER_VERSION = "1.0.0"

    def __init__(self, registry: MCPToolRegistry) -> None:
        self.registry = registry

    def handle_request(self, req: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single JSON-RPC 2.0 request."""
        req_id = req.get("id")
        method = req.get("method")
        params = req.get("params", {})

        if not method:
            return self._error_response(req_id, -32600, "Invalid Request: missing method")

        try:
            if method == "initialize":
                return self._success_response(
                    req_id,
                    {
                        "protocolVersion": self.PROTOCOL_VERSION,
                        "capabilities": {"tools": {}},
                        "serverInfo": {
                            "name": self.SERVER_NAME,
                            "version": self.SERVER_VERSION,
                        },
                    },
                )

            elif method == "ping":
                return self._success_response(req_id, {})

            elif method == "tools/list":
                tools = self.registry.get_tool_definitions()
                return self._success_response(req_id, {"tools": tools})

            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                if not tool_name:
                    return self._error_response(req_id, -32602, "Missing tool name in tools/call")

                result = self.registry.call_tool(tool_name, arguments)
                return self._success_response(
                    req_id,
                    {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(result, indent=2),
                            }
                        ]
                    },
                )

            else:
                return self._error_response(req_id, -32601, f"Method not found: {method}")

        except Exception as exc:
            return self._error_response(req_id, -32603, f"Internal tool execution error: {str(exc)}")

    def run_stdio(self, input_stream: Optional[TextIO] = None, output_stream: Optional[TextIO] = None) -> None:
        """Run standard I/O event loop for MCP clients (Claude Desktop, IDEs, etc.)."""
        inp = input_stream or sys.stdin
        out = output_stream or sys.stdout

        for line in inp:
            line = line.strip()
            if not line:
                continue
            try:
                req = json.loads(line)
                resp = self.handle_request(req)
                out.write(json.dumps(resp) + "\n")
                out.flush()
            except json.JSONDecodeError:
                err = self._error_response(None, -32700, "Parse error")
                out.write(json.dumps(err) + "\n")
                out.flush()

    def _success_response(self, req_id: Any, result: Any) -> Dict[str, Any]:
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": result,
        }

    def _error_response(self, req_id: Any, code: int, message: str) -> Dict[str, Any]:
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {
                "code": code,
                "message": message,
            },
        }
