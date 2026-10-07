"""Unit tests for the Model Context Protocol (MCP) server."""

import json
import unittest

from apex_fde_matrix.actuation.executor import BoundedExecutor
from apex_fde_matrix.graph.model import InfraNode, ResourceType
from apex_fde_matrix.graph.topology import InfrastructureTopology
from apex_fde_matrix.mcp.server import MCPServer
from apex_fde_matrix.mcp.tools import MCPToolRegistry
from apex_fde_matrix.swarm.orchestrator import SRESwarmOrchestrator


class TestMCPServer(unittest.TestCase):
    def setUp(self) -> None:
        self.topo = InfrastructureTopology()
        self.topo.add_node(
            InfraNode(
                id="test_node_01",
                name="Test Compute Node",
                resource_type=ResourceType.BARE_METAL_NODE,
                criticality_weight=3.0,
            )
        )
        self.executor = BoundedExecutor(self.topo)
        self.orchestrator = SRESwarmOrchestrator(self.topo)
        self.registry = MCPToolRegistry(self.topo, self.orchestrator, self.executor)
        self.server = MCPServer(self.registry)

    def test_initialize(self) -> None:
        req = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}
        resp = self.server.handle_request(req)
        self.assertEqual(resp["id"], 1)
        self.assertIn("serverInfo", resp["result"])
        self.assertEqual(resp["result"]["serverInfo"]["name"], "Apex_FDE_Matrix")

    def test_tools_list(self) -> None:
        req = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
        resp = self.server.handle_request(req)
        tools = resp["result"]["tools"]
        tool_names = [t["name"] for t in tools]
        self.assertIn("matrix_query_topology", tool_names)
        self.assertIn("matrix_simulate_blast_radius", tool_names)
        self.assertIn("matrix_diagnose_incident", tool_names)

    def test_tools_call_query_topology(self) -> None:
        req = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "matrix_query_topology",
                "arguments": {"resource_type": "bare_metal_node"},
            },
        }
        resp = self.server.handle_request(req)
        self.assertEqual(resp["id"], 3)
        content_text = resp["result"]["content"][0]["text"]
        data = json.loads(content_text)
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["nodes"][0]["id"], "test_node_01")


if __name__ == "__main__":
    unittest.main()
