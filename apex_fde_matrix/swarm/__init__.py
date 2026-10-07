"""Apex_FDE_Matrix: Swarm Orchestration Package."""

from apex_fde_matrix.swarm.consensus import (
    ConsensusEngine,
    ConsensusVerdict,
    Proposal,
    Vote,
)
from apex_fde_matrix.swarm.orchestrator import SRESwarmOrchestrator
from apex_fde_matrix.swarm.roles import AgentProfile, AgentRole, FrontierModel

__all__ = [
    "AgentProfile",
    "AgentRole",
    "FrontierModel",
    "Proposal",
    "Vote",
    "ConsensusVerdict",
    "ConsensusEngine",
    "SRESwarmOrchestrator",
]
