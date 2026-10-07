"""Apex_FDE_Matrix: The Autonomous Infrastructure Knowledge Graph & Multi-Agent SRE Control Plane.

Pure Python 3.10+ standard library. Zero external dependencies.
Incubated under Apex Growth Systems LLC - Sole Managing Member: Ahmed Hassan.
"""

from apex_fde_matrix.actuation import (
    ActionType,
    BoundedExecutor,
    ExecutionResult,
    MutationAction,
    MutationPlan,
    RollbackDAGGenerator,
)
from apex_fde_matrix.graph import (
    BlastRadiusResult,
    EdgeType,
    GraphQueryEngine,
    InfraEdge,
    InfraNode,
    InfrastructureTopology,
    NodeStatus,
    ResourceType,
    compute_betweenness_centrality,
    compute_blast_radius,
    compute_pagerank,
    identify_single_points_of_failure,
)
from apex_fde_matrix.mcp import MCPServer, MCPToolRegistry
from apex_fde_matrix.swarm import (
    AgentProfile,
    AgentRole,
    ConsensusEngine,
    ConsensusVerdict,
    FrontierModel,
    Proposal,
    SRESwarmOrchestrator,
    Vote,
)

__version__ = "1.0.0"
__author__ = "Ahmed Hassan"
__company__ = "Apex Growth Systems LLC"

__all__ = [
    "__version__",
    "__author__",
    "__company__",
    # Graph Engine
    "InfrastructureTopology",
    "InfraNode",
    "InfraEdge",
    "ResourceType",
    "EdgeType",
    "NodeStatus",
    "BlastRadiusResult",
    "GraphQueryEngine",
    "compute_blast_radius",
    "compute_pagerank",
    "compute_betweenness_centrality",
    "identify_single_points_of_failure",
    # Swarm Orchestration
    "SRESwarmOrchestrator",
    "AgentProfile",
    "AgentRole",
    "FrontierModel",
    "ConsensusEngine",
    "ConsensusVerdict",
    "Proposal",
    "Vote",
    # Actuation & Rollback
    "BoundedExecutor",
    "ExecutionResult",
    "MutationPlan",
    "MutationAction",
    "ActionType",
    "RollbackDAGGenerator",
    # Model Context Protocol
    "MCPServer",
    "MCPToolRegistry",
]
