"""Apex_FDE_Matrix: Graph Query & GraphRAG Context Extraction Engine.

Fast pattern matching, subgraph isolation, and LLM-ready structural context synthesis.
"""

from __future__ import annotations

import re
from typing import Any, Callable, Dict, List, Optional, Set

from apex_fde_matrix.graph.model import InfraEdge, InfraNode, NodeStatus, ResourceType
from apex_fde_matrix.graph.topology import InfrastructureTopology


class GraphQueryEngine:
    """Provides high-performance query primitives and GraphRAG context formatting."""

    def __init__(self, topology: InfrastructureTopology) -> None:
        self.topology = topology

    def find_nodes(
        self,
        resource_type: Optional[ResourceType] = None,
        status: Optional[NodeStatus] = None,
        min_criticality: Optional[float] = None,
        name_pattern: Optional[str] = None,
        metadata_match: Optional[Dict[str, Any]] = None,
    ) -> List[InfraNode]:
        """Filter topology nodes based on structural and operational attributes."""
        pattern = re.compile(name_pattern) if name_pattern else None
        results: List[InfraNode] = []

        for node in self.topology.get_nodes():
            if resource_type and node.resource_type != resource_type:
                continue
            if status and node.status != status:
                continue
            if min_criticality is not None and node.criticality_weight < min_criticality:
                continue
            if pattern and not pattern.search(node.name):
                continue
            if metadata_match:
                matches = all(
                    node.metadata.get(k) == v for k, v in metadata_match.items()
                )
                if not matches:
                    continue
            results.append(node)

        return results

    def extract_subgraph_context(
        self,
        focus_node_ids: List[str],
        hops: int = 1,
    ) -> Dict[str, Any]:
        """Extract a bounded subgraph around focus nodes, formatted for LLM context windows."""
        included_node_ids: Set[str] = set(focus_node_ids)
        frontier: Set[str] = set(focus_node_ids)

        for _ in range(hops):
            next_frontier: Set[str] = set()
            for nid in frontier:
                for edge in self.topology.get_outbound_edges(nid):
                    next_frontier.add(edge.target_id)
                for edge in self.topology.get_inbound_edges(nid):
                    next_frontier.add(edge.source_id)
            new_nodes = next_frontier - included_node_ids
            included_node_ids.update(new_nodes)
            frontier = new_nodes

        nodes_data: List[Dict[str, Any]] = []
        for nid in included_node_ids:
            node = self.topology.get_node(nid)
            if node:
                nodes_data.append(node.to_dict())

        edges_data: List[Dict[str, Any]] = []
        for nid in included_node_ids:
            for edge in self.topology.get_outbound_edges(nid):
                if edge.target_id in included_node_ids:
                    edges_data.append(edge.to_dict())

        return {
            "focus_nodes": focus_node_ids,
            "hops": hops,
            "total_nodes": len(nodes_data),
            "total_edges": len(edges_data),
            "nodes": nodes_data,
            "edges": edges_data,
        }

    def synthesize_graphrag_markdown(self, context: Dict[str, Any]) -> str:
        """Render extracted subgraph context into concise, structured Markdown for agent prompts."""
        lines: List[str] = [
            f"### Infrastructure Digital Twin Context (Nodes: {context['total_nodes']}, Edges: {context['total_edges']})",
            "",
            "#### Nodes:",
        ]

        for n in context["nodes"]:
            lines.append(
                f"- **{n['id']}** ({n['name']}) | Type: `{n['resource_type']}` | Status: `{n['status']}` | Weight: {n['criticality_weight']}"
            )
            if n.get("metrics"):
                metric_str = ", ".join(f"{k}={v}" for k, v in n["metrics"].items())
                lines.append(f"  - Metrics: {metric_str}")

        lines.append("")
        lines.append("#### Dependency Paths & Routes:")
        for e in context["edges"]:
            lines.append(
                f"- `{e['source_id']}` --[{e['edge_type']}]--> `{e['target_id']}`"
            )

        return "\n".join(lines)
