"""Apex_FDE_Matrix: Sovereign FDE Portfolio Mesh Router.

Connects and unifies all 22 Forward Deployed Engineering repositories from Ahmed Hassan's
portfolio into a synchronized operational mesh.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class FDERepositoryNode:
    """Metadata and operational contract for an FDE portfolio repository."""
    name: str
    repo_url: str
    tier: str  # "Tier 1: Core Flagship", "Tier 2: Production Tooling & Graph", "Tier 3: Strategic Playbooks & Research"
    capability: str
    integration_type: str  # "native_control", "policy_contract", "telemetry_source", "hypergraph_bridge"


class FDEPortfolioMesh:
    """Unified mesh registry linking all 22 sovereign FDE repositories."""

    PORTFOLIO_NODES: List[FDERepositoryNode] = [
        # Tier 1: Core Flagships
        FDERepositoryNode(
            name="Apex_FDE_Matrix",
            repo_url="https://github.com/AAH20/Apex_FDE_Matrix",
            tier="Tier 1: Core Flagship",
            capability="Autonomous Infrastructure Digital Twin & Multi-Agent SRE Control Plane",
            integration_type="native_control",
        ),
        FDERepositoryNode(
            name="fde-bounty-snr",
            repo_url="https://github.com/AAH20/fde-bounty-snr",
            tier="Tier 1: Core Flagship",
            capability="Senior AI FDE L0-L4 Evaluation Rubric & ActionLedger Receipts",
            integration_type="policy_contract",
        ),
        FDERepositoryNode(
            name="autonomous-tactical-ontology",
            repo_url="https://github.com/AAH20/autonomous-tactical-ontology",
            tier="Tier 1: Core Flagship",
            capability="Palantir Foundry/Gotham Open-Ontology Hypergraph & Entity Resolver",
            integration_type="hypergraph_bridge",
        ),
        FDERepositoryNode(
            name="enterprise-ai-production-control-plane",
            repo_url="https://github.com/AAH20/enterprise-ai-production-control-plane",
            tier="Tier 1: Core Flagship",
            capability="Enterprise Kubernetes GPU FinOps & Last-Mile Control Plane",
            integration_type="native_control",
        ),

        # Tier 2: Production Tooling, Graph Engines & Runtime Gates
        FDERepositoryNode(
            name="agent-action-gate",
            repo_url="https://github.com/AAH20/agent-action-gate",
            tier="Tier 2: Production Tooling & Graph",
            capability="Unattended Destructive Tool Call Gate & Instant Audit Receipts",
            integration_type="policy_contract",
        ),
        FDERepositoryNode(
            name="agentic-ai-infrastructure-data-engine",
            repo_url="https://github.com/AAH20/agentic-ai-infrastructure-data-engine",
            tier="Tier 2: Production Tooling & Graph",
            capability="Production AI Infra, GraphRAG & NVIDIA NIM Data Engine",
            integration_type="telemetry_source",
        ),
        FDERepositoryNode(
            name="agentic-cloud-solution-engineering-factory",
            repo_url="https://github.com/AAH20/agentic-cloud-solution-engineering-factory",
            tier="Tier 2: Production Tooling & Graph",
            capability="Solution Architecture, RFP Automation & Migration Contracts",
            integration_type="policy_contract",
        ),
        FDERepositoryNode(
            name="ai-ran-profitability-autopilot",
            repo_url="https://github.com/AAH20/ai-ran-profitability-autopilot",
            tier="Tier 2: Production Tooling & Graph",
            capability="AI-RAN Telco Field Service & Controlled Remediation Receipts",
            integration_type="telemetry_source",
        ),
        FDERepositoryNode(
            name="autonomous-cloud-modernization-factory",
            repo_url="https://github.com/AAH20/autonomous-cloud-modernization-factory",
            tier="Tier 2: Production Tooling & Graph",
            capability="VMware Exit, Azure Migration & Disaster Recovery Factory",
            integration_type="native_control",
        ),
        FDERepositoryNode(
            name="temporal-hypergraph-synthesizer",
            repo_url="https://github.com/AAH20/temporal-hypergraph-synthesizer",
            tier="Tier 2: Production Tooling & Graph",
            capability="Tactical Insurgent C2 Dynamic Subgraph Isomorphism Engine",
            integration_type="hypergraph_bridge",
        ),
        FDERepositoryNode(
            name="belief-graph",
            repo_url="https://github.com/AAH20/belief-graph",
            tier="Tier 2: Production Tooling & Graph",
            capability="Bayesian Belief Network & Narrative Defense Swarm",
            integration_type="telemetry_source",
        ),
        FDERepositoryNode(
            name="eval-lake",
            repo_url="https://github.com/AAH20/eval-lake",
            tier="Tier 2: Production Tooling & Graph",
            capability="GenAI Evaluation, DuckDB ETL & Cryptographic GRC Lakehouse",
            integration_type="policy_contract",
        ),
        FDERepositoryNode(
            name="GRC_Claw",
            repo_url="https://github.com/AAH20/GRC_Claw",
            tier="Tier 2: Production Tooling & Graph",
            capability="ISO 42001 & NIST AI RMF Delegated Authority Reference",
            integration_type="policy_contract",
        ),

        # Tier 3: Strategic Playbooks & Defense Research
        FDERepositoryNode(
            name="a2z-soc",
            repo_url="https://github.com/AAH20/a2z-soc",
            tier="Tier 3: Strategic Playbooks & Research",
            capability="Continuous Compliance Engine & 30-Post FDE Operational Matrix",
            integration_type="policy_contract",
        ),
        FDERepositoryNode(
            name="acquisition-platform-research",
            repo_url="https://github.com/AAH20/acquisition-platform-research",
            tier="Tier 3: Strategic Playbooks & Research",
            capability="Palantir & Anduril Defense FDE Operating Model Research",
            integration_type="policy_contract",
        ),
        FDERepositoryNode(
            name="ai-native-internal-developer-platform",
            repo_url="https://github.com/AAH20/ai-native-internal-developer-platform",
            tier="Tier 3: Strategic Playbooks & Research",
            capability="AI-Native IDP Golden Paths & Delivery Economics",
            integration_type="native_control",
        ),
        FDERepositoryNode(
            name="aiops-observability-platform",
            repo_url="https://github.com/AAH20/aiops-observability-platform",
            tier="Tier 3: Strategic Playbooks & Research",
            capability="Kubernetes OpenTelemetry & RCA SRE Evidence",
            integration_type="telemetry_source",
        ),
        FDERepositoryNode(
            name="nvidia-ai-factory-deployment-automation",
            repo_url="https://github.com/AAH20/nvidia-ai-factory-deployment-automation",
            tier="Tier 3: Strategic Playbooks & Research",
            capability="NVIDIA GPU Factory NCCL/RoCE Cluster Deployment",
            integration_type="native_control",
        ),
        FDERepositoryNode(
            name="azure-cloud-migration-modernization-platform",
            repo_url="https://github.com/AAH20/azure-cloud-migration-modernization-platform",
            tier="Tier 3: Strategic Playbooks & Research",
            capability="Azure Migration Landing Zones & Dependency Waves",
            integration_type="native_control",
        ),
        FDERepositoryNode(
            name="enterprise-ai-integration-platform",
            repo_url="https://github.com/AAH20/enterprise-ai-integration-platform",
            tier="Tier 3: Strategic Playbooks & Research",
            capability="SAP/Salesforce/Oracle Durable Workflow Integration",
            integration_type="policy_contract",
        ),
        FDERepositoryNode(
            name="llm-inference-optimization-platform",
            repo_url="https://github.com/AAH20/llm-inference-optimization-platform",
            tier="Tier 3: Strategic Playbooks & Research",
            capability="LLM Model Routing, NIM Gateways & GPU FinOps",
            integration_type="telemetry_source",
        ),
        FDERepositoryNode(
            name="real-time-ai-data-platform",
            repo_url="https://github.com/AAH20/real-time-ai-data-platform",
            tier="Tier 3: Strategic Playbooks & Research",
            capability="Real-time Fabric & Databricks Lakehouse Engineering",
            integration_type="telemetry_source",
        ),
    ]

    @classmethod
    def get_all_nodes(cls) -> List[FDERepositoryNode]:
        return cls.PORTFOLIO_NODES

    @classmethod
    def get_by_tier(cls, tier: str) -> List[FDERepositoryNode]:
        return [n for n in cls.PORTFOLIO_NODES if n.tier.startswith(tier)]

    @classmethod
    def get_node(cls, name: str) -> Optional[FDERepositoryNode]:
        for n in cls.PORTFOLIO_NODES:
            if n.name.lower() == name.lower():
                return n
        return None
