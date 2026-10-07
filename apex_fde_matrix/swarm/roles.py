"""Apex_FDE_Matrix: Frontier Agent Roles and Profiles.

Late-2026 frontier model definitions and SRE swarm role archetypes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Set


class AgentRole(str, Enum):
    """Specialized SRE swarm roles."""
    STRATEGIC_ARCHITECT = "strategic_architect"
    RAPID_REMEDIATOR = "rapid_remediator"
    TELEMETRY_SYNTHESIZER = "telemetry_synthesizer"
    AUDIT_VERIFIER = "audit_verifier"


class FrontierModel(str, Enum):
    """Late-2026 frontier models and enterprise open-weight standards."""
    # Frontier Proprietary
    CLAUDE_OPUS_5_5 = "claude-opus-5.5"
    CLAUDE_MYTHOS_5_1 = "claude-mythos-5.1"
    GPT_6_ASTRA = "gpt-6-astra"
    GPT_6_LUNA = "gpt-6-luna"
    GEMINI_4_ARGON = "gemini-4-argon"
    GEMINI_3_8_FLASH = "gemini-3.8-flash"

    # Enterprise Open-Weight (NVIDIA NIM / Self-Hosted)
    NEMOTRON_70B = "nvidia/llama-3.1-nemotron-70b"
    HERMES_3 = "nousresearch/hermes-3-llama-3.1-70b"
    DEEPSEEK_R1 = "deepseek-ai/deepseek-r1"
    QWEN_2_5_CODER = "qwen/qwen-2.5-coder-32b"


@dataclass
class AgentProfile:
    """Defines capabilities, authority, and voting weights for an SRE agent."""
    role: AgentRole
    model: FrontierModel
    confidence_weight: float  # e.g., 0.40 for Claude Opus, 0.35 for GPT-6, 0.25 for Gemini
    system_prompt: str
    capabilities: Set[str] = field(default_factory=set)

    @classmethod
    def default_profiles(cls) -> Dict[AgentRole, AgentProfile]:
        return {
            AgentRole.STRATEGIC_ARCHITECT: cls(
                role=AgentRole.STRATEGIC_ARCHITECT,
                model=FrontierModel.CLAUDE_OPUS_5_5,
                confidence_weight=0.40,
                system_prompt=(
                    "You are the Strategic Infrastructure Architect. Your mandate is to analyze "
                    "complex cross-cluster causal dependencies, generate root-cause hypotheses, "
                    "and reject any mutation plan whose blast radius threatens core data or spine routing."
                ),
                capabilities={"hypothesis_generation", "architectural_review", "blast_radius_veto"},
            ),
            AgentRole.RAPID_REMEDIATOR: cls(
                role=AgentRole.RAPID_REMEDIATOR,
                model=FrontierModel.GPT_6_ASTRA,
                confidence_weight=0.35,
                system_prompt=(
                    "You are the Rapid SRE Remediator. Your mandate is to synthesize surgical, "
                    "bounded configuration patches, generate inverse compensatory rollback sequences, "
                    "and calculate step-by-step actuation DAGs for immediate incident resolution."
                ),
                capabilities={"patch_synthesis", "rollback_generation", "dag_scheduling"},
            ),
            AgentRole.TELEMETRY_SYNTHESIZER: cls(
                role=AgentRole.TELEMETRY_SYNTHESIZER,
                model=FrontierModel.GEMINI_4_ARGON,
                confidence_weight=0.25,
                system_prompt=(
                    "You are the Distributed Telemetry Synthesizer. Your mandate is to digest "
                    "massive eBPF socket flows, OpenTelemetry spans, and kernel error logs to pinpoint "
                    "anomalous metric divergence and verify post-mutation invariant health."
                ),
                capabilities={"ebpf_stream_analysis", "metric_anomaly_detection", "health_verification"},
            ),
            AgentRole.AUDIT_VERIFIER: cls(
                role=AgentRole.AUDIT_VERIFIER,
                model=FrontierModel.HERMES_3,
                confidence_weight=0.20,
                system_prompt=(
                    "You are the Sovereign Audit & GRC Verifier. Your mandate is to enforce ISO/IEC 42001, "
                    "SOC2, and zero-loop invariants, logging immutable cryptographic proofs before execution."
                ),
                capabilities={"grc_verification", "audit_logging", "loop_detection"},
            ),
        }
