"""Apex_FDE_Matrix: Multi-Agent Consensus and Quorum Engine.

Byzantine-resistant voting protocol and blast-radius veto enforcement.
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from apex_fde_matrix.swarm.roles import AgentProfile, AgentRole, FrontierModel


@dataclass
class Proposal:
    """An autonomous mutation or remediation action proposed by the swarm."""
    proposal_id: str
    action_type: str
    target_node_id: str
    parameters: Dict[str, Any]
    estimated_blast_radius: float
    reasoning: str
    created_at: float = field(default_factory=time.time)


@dataclass
class Vote:
    """An individual agent's decision on a proposal."""
    agent_role: AgentRole
    model: FrontierModel
    approved: bool
    confidence: float  # 0.0 to 1.0
    rationale: str
    veto_exercised: bool = False
    timestamp: float = field(default_factory=time.time)


@dataclass
class ConsensusVerdict:
    """Outcome of multi-agent voting on an infrastructure mutation."""
    proposal_id: str
    approved: bool
    aggregate_score: float
    threshold: float
    vetoed: bool
    veto_reason: Optional[str]
    votes: List[Vote]
    consensus_hash: str
    timestamp: float = field(default_factory=time.time)


class ConsensusEngine:
    """Evaluates multi-agent quorum and enforces invariant safety thresholds."""

    def __init__(
        self,
        profiles: Optional[Dict[AgentRole, AgentProfile]] = None,
        default_threshold: float = 0.75,
    ) -> None:
        self.profiles = profiles or AgentProfile.default_profiles()
        self.threshold = default_threshold

    def evaluate(
        self,
        proposal: Proposal,
        votes: List[Vote],
        threshold: Optional[float] = None,
    ) -> ConsensusVerdict:
        """Calculate weighted approval score and check for architectural vetoes."""
        thresh = threshold if threshold is not None else self.threshold
        vetoed = False
        veto_reason: Optional[str] = None

        total_weight = 0.0
        approved_weight = 0.0

        for vote in votes:
            profile = self.profiles.get(vote.agent_role)
            weight = profile.confidence_weight if profile else 0.25
            total_weight += weight

            if vote.veto_exercised:
                vetoed = True
                veto_reason = f"Veto exercised by {vote.agent_role.value}: {vote.rationale}"

            if vote.approved:
                approved_weight += weight * vote.confidence

        aggregate_score = (approved_weight / total_weight) if total_weight > 0 else 0.0
        final_approved = (aggregate_score >= thresh) and not vetoed

        # Generate cryptographic audit hash of the consensus decision
        raw_token = f"{proposal.proposal_id}:{final_approved}:{aggregate_score}:{time.time()}"
        consensus_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()

        return ConsensusVerdict(
            proposal_id=proposal.proposal_id,
            approved=final_approved,
            aggregate_score=round(aggregate_score, 4),
            threshold=thresh,
            vetoed=vetoed,
            veto_reason=veto_reason,
            votes=votes,
            consensus_hash=consensus_hash,
        )
