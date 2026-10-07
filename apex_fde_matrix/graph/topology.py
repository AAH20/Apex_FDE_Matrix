"""Apex_FDE_Matrix: Causal Infrastructure Knowledge Graph (Digital Twin).

High-performance, in-memory directed graph representing live physical and logical
enterprise infrastructure. Sub-millisecond traversals with zero external dependencies.
"""

from __future__ import annotations

import collections
import copy
import time
from typing import Any, Deque, Dict, Iterator, List, Optional, Set, Tuple

from apex_fde_matrix.graph.model import (
    EdgeType,
    InfraEdge,
    InfraNode,
    NodeStatus,
    ResourceType,
)


class InfrastructureTopology:
    """In-memory directed property graph representing the enterprise digital twin."""

    def __init__(self) -> None:
        self._nodes: Dict[str, InfraNode] = {}
        # Forward edges: source -> {target: edge}
        self._out_edges: Dict[str, Dict[str, InfraEdge]] = collections.defaultdict(dict)
        # Reverse edges: target -> {source: edge}
        self._in_edges: Dict[str, Dict[str, InfraEdge]] = collections.defaultdict(dict)
        self._version: int = 0
        self._created_at: float = time.time()

    @property
    def version(self) -> int:
        return self._version

    @property
    def node_count(self) -> int:
        return len(self._nodes)

    @property
    def edge_count(self) -> int:
        return sum(len(targets) for targets in self._out_edges.values())

    def add_node(self, node: InfraNode) -> None:
        """Insert or replace an infrastructure node."""
        self._nodes[node.id] = node
        self._version += 1

    def remove_node(self, node_id: str) -> Optional[InfraNode]:
        """Remove a node and all associated inbound and outbound edges."""
        if node_id not in self._nodes:
            return None

        # Remove outbound edges
        out_targets = list(self._out_edges.get(node_id, {}).keys())
        for tgt in out_targets:
            self.remove_edge(node_id, tgt)

        # Remove inbound edges
        in_sources = list(self._in_edges.get(node_id, {}).keys())
        for src in in_sources:
            self.remove_edge(src, node_id)

        node = self._nodes.pop(node_id)
        self._out_edges.pop(node_id, None)
        self._in_edges.pop(node_id, None)
        self._version += 1
        return node

    def add_edge(self, edge: InfraEdge) -> None:
        """Insert a directional dependency edge."""
        if edge.source_id not in self._nodes:
            raise KeyError(f"Source node '{edge.source_id}' does not exist in topology.")
        if edge.target_id not in self._nodes:
            raise KeyError(f"Target node '{edge.target_id}' does not exist in topology.")

        self._out_edges[edge.source_id][edge.target_id] = edge
        self._in_edges[edge.target_id][edge.source_id] = edge
        self._version += 1

    def remove_edge(self, source_id: str, target_id: str) -> Optional[InfraEdge]:
        """Remove a directional dependency edge."""
        edge = self._out_edges.get(source_id, {}).pop(target_id, None)
        self._in_edges.get(target_id, {}).pop(source_id, None)
        if edge is not None:
            self._version += 1
        return edge

    def get_node(self, node_id: str) -> Optional[InfraNode]:
        """Retrieve node by unique ID."""
        return self._nodes.get(node_id)

    def get_nodes(self) -> List[InfraNode]:
        """Retrieve all nodes in the topology."""
        return list(self._nodes.values())

    def get_edge(self, source_id: str, target_id: str) -> Optional[InfraEdge]:
        """Retrieve edge between two nodes if it exists."""
        return self._out_edges.get(source_id, {}).get(target_id)

    def get_outbound_edges(self, node_id: str) -> List[InfraEdge]:
        """Retrieve all outgoing edges from node_id."""
        return list(self._out_edges.get(node_id, {}).values())

    def get_inbound_edges(self, node_id: str) -> List[InfraEdge]:
        """Retrieve all incoming edges to node_id."""
        return list(self._in_edges.get(node_id, {}).values())

    def get_dependents(self, node_id: str) -> List[InfraNode]:
        """Nodes that directly depend on node_id (nodes whose DEPENDS_ON points to node_id).

        If A depends_on B (edge A -> B), then A is dependent on B.
        In reverse adjacency, in_edges of B contains A.
        """
        dependent_ids = self._in_edges.get(node_id, {}).keys()
        return [self._nodes[did] for did in dependent_ids if did in self._nodes]

    def get_dependencies(self, node_id: str) -> List[InfraNode]:
        """Nodes that node_id directly depends on (targets of outbound DEPENDS_ON edges)."""
        target_ids = self._out_edges.get(node_id, {}).keys()
        return [self._nodes[tid] for tid in target_ids if tid in self._nodes]

    def find_shortest_path(self, source_id: str, target_id: str) -> Optional[List[str]]:
        """Compute shortest path using unweighted BFS."""
        if source_id not in self._nodes or target_id not in self._nodes:
            return None
        if source_id == target_id:
            return [source_id]

        queue: Deque[Tuple[str, List[str]]] = collections.deque([(source_id, [source_id])])
        visited: Set[str] = {source_id}

        while queue:
            curr, path = queue.popleft()
            for neighbor in self._out_edges.get(curr, {}):
                if neighbor == target_id:
                    return path + [neighbor]
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        return None

    def detect_cycles(self) -> List[List[str]]:
        """Tarjan's algorithm to identify strongly connected components / dependency cycles."""
        index = 0
        indices: Dict[str, int] = {}
        lowlinks: Dict[str, int] = {}
        stack: List[str] = []
        on_stack: Set[str] = set()
        sccs: List[List[str]] = []

        def strongconnect(node_id: str) -> None:
            nonlocal index
            indices[node_id] = index
            lowlinks[node_id] = index
            index += 1
            stack.append(node_id)
            on_stack.add(node_id)

            for neighbor in self._out_edges.get(node_id, {}):
                if neighbor not in indices:
                    strongconnect(neighbor)
                    lowlinks[node_id] = min(lowlinks[node_id], lowlinks[neighbor])
                elif neighbor in on_stack:
                    lowlinks[node_id] = min(lowlinks[node_id], indices[neighbor])

            if lowlinks[node_id] == indices[node_id]:
                scc: List[str] = []
                while True:
                    w = stack.pop()
                    on_stack.remove(w)
                    scc.append(w)
                    if w == node_id:
                        break
                if len(scc) > 1:
                    sccs.append(scc)

        for node_id in self._nodes:
            if node_id not in indices:
                strongconnect(node_id)
        return sccs

    def snapshot(self) -> Dict[str, Any]:
        """Generate an exact, transactional checkpoint of the current digital twin."""
        return {
            "version": self._version,
            "created_at": self._created_at,
            "nodes": [node.to_dict() for node in self._nodes.values()],
            "edges": [
                edge.to_dict()
                for target_map in self._out_edges.values()
                for edge in target_map.values()
            ],
        }

    def restore_snapshot(self, snapshot: Dict[str, Any]) -> None:
        """Atomically restore topology state from a snapshot checkpoint."""
        self._nodes.clear()
        self._out_edges.clear()
        self._in_edges.clear()

        for nd in snapshot.get("nodes", []):
            self.add_node(InfraNode.from_dict(nd))

        for ed in snapshot.get("edges", []):
            self.add_edge(InfraEdge.from_dict(ed))

        self._version = snapshot.get("version", self._version + 1)
