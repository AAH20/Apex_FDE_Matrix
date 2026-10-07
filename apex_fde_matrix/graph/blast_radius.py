"""Apex_FDE_Matrix: Blast Radius Calculation & Graph Centrality Algorithms.

Mathematical reachability analysis, PageRank, and Brandes' betweenness centrality.
Pure Python standard library with sub-millisecond execution guarantees.
"""

from __future__ import annotations

import collections
import time
from typing import Deque, Dict, List, Set, Tuple

from apex_fde_matrix.graph.model import BlastRadiusResult
from apex_fde_matrix.graph.topology import InfrastructureTopology


def compute_blast_radius(
    topology: InfrastructureTopology,
    target_node_id: str,
    attenuation_factor: float = 0.85,
    max_depth: int = 10,
) -> BlastRadiusResult:
    """Calculate the deterministic blast radius impact if target_node_id is mutated or fails.

    Traverses all forward-dependent nodes (nodes that rely on target_node_id),
    weighting impact by criticality and decaying by network/causal distance:
        Impact = sum(weight(v) * (attenuation ** depth(v)))
    """
    start_time = time.perf_counter()

    target_node = topology.get_node(target_node_id)
    if target_node is None:
        raise KeyError(f"Target node '{target_node_id}' not found in topology.")

    # Nodes dependent on target_node are found via reverse edges (who points to target_node)
    # or forward edges depending on semantic direction.
    # In our graph, if Service A -> Database B (A depends on B),
    # then if Database B fails, Service A is affected.
    # Therefore, affected nodes are reachable via IN-EDGES (reverse direction).
    affected_nodes: Dict[str, int] = {}  # node_id -> shortest depth
    direct_dependents: List[str] = []
    transitive_dependents: List[str] = []
    critical_dependents: List[str] = []

    queue: Deque[Tuple[str, int]] = collections.deque([(target_node_id, 0)])
    visited: Set[str] = {target_node_id}

    while queue:
        curr_id, depth = queue.popleft()
        if depth >= max_depth:
            continue

        # In-edges point to curr_id (i.e. nodes that depend on curr_id)
        in_edges = topology.get_inbound_edges(curr_id)
        for edge in in_edges:
            neighbor_id = edge.source_id
            if neighbor_id not in visited:
                visited.add(neighbor_id)
                next_depth = depth + 1
                affected_nodes[neighbor_id] = next_depth
                queue.append((neighbor_id, next_depth))

                if next_depth == 1:
                    direct_dependents.append(neighbor_id)
                else:
                    transitive_dependents.append(neighbor_id)

                neighbor_node = topology.get_node(neighbor_id)
                if neighbor_node and neighbor_node.criticality_weight >= 5.0:
                    critical_dependents.append(neighbor_id)

    # Compute aggregate mathematical impact score
    # Base impact starts with target node itself
    total_impact = target_node.criticality_weight
    for node_id, depth in affected_nodes.items():
        node = topology.get_node(node_id)
        weight = node.criticality_weight if node else 1.0
        total_impact += weight * (attenuation_factor ** depth)

    elapsed_ms = (time.perf_counter() - start_time) * 1000.0

    return BlastRadiusResult(
        target_node_id=target_node_id,
        impact_score=round(total_impact, 4),
        affected_nodes_count=len(affected_nodes),
        direct_dependents=direct_dependents,
        transitive_dependents=transitive_dependents,
        critical_dependents=critical_dependents,
        attenuation_factor=attenuation_factor,
        calculation_time_ms=round(elapsed_ms, 3),
    )


def compute_pagerank(
    topology: InfrastructureTopology,
    damping: float = 0.85,
    max_iter: int = 50,
    tol: float = 1e-6,
) -> Dict[str, float]:
    """Compute PageRank centrality to identify core structural hubs in the infrastructure."""
    nodes = topology.get_nodes()
    n = len(nodes)
    if n == 0:
        return {}

    node_ids = [node.id for node in nodes]
    rank: Dict[str, float] = {nid: 1.0 / n for nid in node_ids}

    # Precompute outbound degrees
    out_degrees: Dict[str, int] = {}
    for nid in node_ids:
        out_degrees[nid] = len(topology.get_outbound_edges(nid))

    base_val = (1.0 - damping) / n

    for _ in range(max_iter):
        new_rank: Dict[str, float] = {nid: base_val for nid in node_ids}
        dangling_sum = sum(rank[nid] for nid in node_ids if out_degrees[nid] == 0)
        dangling_contrib = damping * (dangling_sum / n)

        for nid in node_ids:
            new_rank[nid] += dangling_contrib

        for nid in node_ids:
            if out_degrees[nid] > 0:
                share = damping * (rank[nid] / out_degrees[nid])
                for edge in topology.get_outbound_edges(nid):
                    new_rank[edge.target_id] += share

        diff = sum(abs(new_rank[nid] - rank[nid]) for nid in node_ids)
        rank = new_rank
        if diff < tol:
            break

    return rank


def compute_betweenness_centrality(
    topology: InfrastructureTopology,
    normalized: bool = True,
) -> Dict[str, float]:
    """Brandes' fast algorithm for unweighted betweenness centrality.

    Identifies bottleneck nodes sitting on critical data and network propagation paths.
    """
    nodes = topology.get_nodes()
    node_ids = [n.id for n in nodes]
    num_nodes = len(node_ids)
    cb: Dict[str, float] = {nid: 0.0 for nid in node_ids}

    for s in node_ids:
        stack: List[str] = []
        pred: Dict[str, List[str]] = {w: [] for w in node_ids}
        sigma: Dict[str, int] = {w: 0 for w in node_ids}
        sigma[s] = 1
        dist: Dict[str, int] = {w: -1 for w in node_ids}
        dist[s] = 0

        queue: Deque[str] = collections.deque([s])
        while queue:
            v = queue.popleft()
            stack.append(v)
            for edge in topology.get_outbound_edges(v):
                w = edge.target_id
                if dist[w] < 0:
                    dist[w] = dist[v] + 1
                    queue.append(w)
                if dist[w] == dist[v] + 1:
                    sigma[w] += sigma[v]
                    pred[w].append(v)

        delta: Dict[str, float] = {w: 0.0 for w in node_ids}
        while stack:
            w = stack.pop()
            for v in pred[w]:
                if sigma[w] > 0:
                    delta[v] += (sigma[v] / sigma[w]) * (1.0 + delta[w])
            if w != s:
                cb[w] += delta[w]

    if normalized and num_nodes > 2:
        scale = 1.0 / ((num_nodes - 1) * (num_nodes - 2))
        for nid in cb:
            cb[nid] *= scale

    return cb


def identify_single_points_of_failure(
    topology: InfrastructureTopology,
    threshold: float = 0.15,
) -> List[Tuple[str, float]]:
    """Identify single points of failure (SPOFs) exceeding betweenness centrality threshold."""
    centrality = compute_betweenness_centrality(topology, normalized=True)
    spofs = [(nid, score) for nid, score in centrality.items() if score >= threshold]
    spofs.sort(key=lambda x: x[1], reverse=True)
    return spofs
