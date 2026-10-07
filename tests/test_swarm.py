"""Unit tests for the Multi-Agent SRE Swarm Orchestrator and Consensus."""

import unittest

from apex_fde_matrix.graph.model import InfraEdge, InfraNode, ResourceType
from apex_fde_matrix.graph.topology import InfrastructureTopology
from apex_fde_matrix.swarm.consensus import (
    ConsensusEngine,
    Proposal,
    Vote,
)
from apex_fde_matrix.swarm.orchestrator import SRESwarmOrchestrator
from apex_fde_matrix.swarm.roles import AgentProfile, AgentRole, FrontierModel


class TestSwarmOrchestration(unittest.TestCase):
    def setUp(self) -> None:
        self.topo = InfrastructureTopology()
        self.topo.add_node(
            InfraNode(
                id="gpu_node_01",
                name="NVIDIA H100 Node",
                resource_type=ResourceType.BARE_METAL_NODE,
                criticality_weight=5.0,
            )
        )
        self.orchestrator = SRESwarmOrchestrator(self.topo)
        self.consensus_engine = ConsensusEngine()

    def test_consensus_approval(self) -> None:
        prop = Proposal(
            proposal_id="p1",
            action_type="drain_node",
            target_node_id="gpu_node_01",
            parameters={},
            estimated_blast_radius=5.0,
            reasoning="Prevent GPU thermal throttle",
        )
        votes = [
            Vote(agent_role=AgentRole.STRATEGIC_ARCHITECT, model=FrontierModel.CLAUDE_OPUS_5_5, approved=True, confidence=1.0, rationale="OK"),
            Vote(agent_role=AgentRole.RAPID_REMEDIATOR, model=FrontierModel.GPT_6_ASTRA, approved=True, confidence=1.0, rationale="OK"),
            Vote(agent_role=AgentRole.TELEMETRY_SYNTHESIZER, model=FrontierModel.GEMINI_4_ARGON, approved=True, confidence=1.0, rationale="OK"),
        ]
        verdict = self.consensus_engine.evaluate(prop, votes, threshold=0.75)
        self.assertTrue(verdict.approved)
        self.assertFalse(verdict.vetoed)
        self.assertGreaterEqual(verdict.aggregate_score, 0.75)
        self.assertTrue(len(verdict.consensus_hash) == 64)

    def test_strategic_architect_veto(self) -> None:
        prop = Proposal(
            proposal_id="p2",
            action_type="drain_node",
            target_node_id="gpu_node_01",
            parameters={},
            estimated_blast_radius=60.0,
            reasoning="Unbounded drain",
        )
        votes = [
            Vote(agent_role=AgentRole.STRATEGIC_ARCHITECT, model=FrontierModel.CLAUDE_OPUS_5_5, approved=False, confidence=0.0, rationale="Blast radius too high", veto_exercised=True),
            Vote(agent_role=AgentRole.RAPID_REMEDIATOR, model=FrontierModel.GPT_6_ASTRA, approved=True, confidence=1.0, rationale="OK"),
            Vote(agent_role=AgentRole.TELEMETRY_SYNTHESIZER, model=FrontierModel.GEMINI_4_ARGON, approved=True, confidence=1.0, rationale="OK"),
        ]
        verdict = self.consensus_engine.evaluate(prop, votes, threshold=0.75)
        self.assertFalse(verdict.approved)
        self.assertTrue(verdict.vetoed)
        self.assertIn("Blast radius too high", verdict.veto_reason or "")

    def test_orchestrator_incident_handling(self) -> None:
        res = self.orchestrator.handle_incident(
            incident_id="INC-100",
            impacted_node_id="gpu_node_01",
            symptom_description="High PCIe replay errors",
            max_acceptable_blast_radius=20.0,
        )
        self.assertEqual(res["incident_id"], "INC-100")
        self.assertTrue(res["consensus"]["approved"])
        self.assertEqual(res["proposal"]["target"], "gpu_node_01")


if __name__ == "__main__":
    unittest.main()
