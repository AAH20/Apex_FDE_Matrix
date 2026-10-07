"""Apex_FDE_Matrix: Quickstart Example.

Demonstrates creating a digital twin, adding nodes/edges, and calculating blast radius.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from apex_fde_matrix import (
    EdgeType,
    InfraEdge,
    InfraNode,
    InfrastructureTopology,
    ResourceType,
    compute_blast_radius,
)

# 1. Initialize digital twin
topo = InfrastructureTopology()

# 2. Add infrastructure nodes
db = InfraNode(id="db_core", name="Core Postgres DB", resource_type=ResourceType.DATABASE, criticality_weight=8.5)
api = InfraNode(id="api_mesh", name="Kong Gateway", resource_type=ResourceType.K8S_SERVICE, criticality_weight=5.0)
worker = InfraNode(id="worker_fleet", name="Inference Workers", resource_type=ResourceType.K8S_POD, criticality_weight=2.0)

topo.add_node(db)
topo.add_node(api)
topo.add_node(worker)

# 3. Define dependency edges: worker -> api -> db
topo.add_edge(InfraEdge(source_id="worker_fleet", target_id="api_mesh", edge_type=EdgeType.DEPENDS_ON))
topo.add_edge(InfraEdge(source_id="api_mesh", target_id="db_core", edge_type=EdgeType.DEPENDS_ON))

# 4. Compute deterministic blast radius of database failure
result = compute_blast_radius(topo, "db_core")

print(f"Target: {result.target_node_id}")
print(f"Impact Score: {result.impact_score}")
print(f"Affected Nodes: {result.affected_nodes_count}")
print(f"Direct Dependents: {result.direct_dependents}")
print(f"Transitive Dependents: {result.transitive_dependents}")
print(f"Execution Latency: {result.calculation_time_ms} ms")
