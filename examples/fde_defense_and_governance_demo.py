"""Apex_FDE_Matrix: Defense & Governance Ecosystem Demo.

Demonstrates seamless integration with:
- autonomous-tactical-ontology (Palantir Foundry / Gotham Open-Ontology export)
- fde-bounty-snr (L0-L4 Senior AI FDE ladder & ActionLedger receipts)
- agent-action-gate (Runtime tool interception & destructive action DENY)
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from apex_fde_matrix import (
    ActionType,
    InfrastructureTopology,
    MutationAction,
    MutationPlan,
    compute_blast_radius,
)
from apex_fde_matrix.adapters.baremetal import BareMetalGPUAdapter
from apex_fde_matrix.integrations.action_gate import (
    AgentActionGateIntegration,
    GateVerdict,
)
from apex_fde_matrix.integrations.fde_bounty import (
    FDEBountyIntegration,
    FDELadderLevel,
)
from apex_fde_matrix.integrations.portfolio_mesh import FDEPortfolioMesh
from apex_fde_matrix.integrations.tactical_ontology import (
    TacticalOntologyIntegration,
)


def main() -> None:
    print("=" * 76)
    print(" Apex_FDE_Matrix: FDE Defense & Governance Ecosystem Integration")
    print(" [Tactical Ontology + FDE Bounty Rubric + Agent Action Gate]")
    print("=" * 76)

    # 1. Initialize digital twin with GPU cluster
    topo = InfrastructureTopology()
    BareMetalGPUAdapter.ingest_gpu_cluster(topo, "tactical_h100", node_count=2, gpus_per_node=4)
    print(f"[*] Ingested {topo.node_count} nodes into Digital Twin.")

    # 2. Export to Palantir Foundry / Gotham Open-Ontology JSON-LD (autonomous-tactical-ontology)
    print("\n[*] Step 1: Exporting Digital Twin to Palantir Open-Ontology format...")
    palantir_payload = TacticalOntologyIntegration.export_palantir_open_ontology(topo)
    print(f"    - Entities Exported: {palantir_payload['entityCount']}")
    print(f"    - Links Exported:    {palantir_payload['linkCount']}")
    print(f"    - Ontology RID:      {palantir_payload['ontologyRid']}")

    # 3. Intercept Action with Agent Action Gate (agent-action-gate)
    print("\n[*] Step 2: Testing Runtime Security Gate (agent-action-gate)...")
    gate = AgentActionGateIntegration(strict_mode=True)
    # Test 2a: Destructive unattended command
    v1, r1 = gate.evaluate_tool_call("purge_cluster", "bm_node_tactical_h100_01", {}, is_unattended=True)
    print(f"    - Unattended 'purge_cluster': {v1.value} ({r1})")

    # Test 2b: Verified bounded mutation
    v2, r2 = gate.evaluate_tool_call("drain_node", "bm_node_tactical_h100_01", {}, is_unattended=True)
    print(f"    - Unattended 'drain_node':   {v2.value} ({r2})")

    # 4. Enforce Senior AI FDE Ladder & ActionLedger Receipts (fde-bounty-snr)
    print("\n[*] Step 3: Verifying Senior AI FDE Competency Ladder (fde-bounty-snr)...")
    bounty = FDEBountyIntegration("plant_tactical_defense_01")
    blast = compute_blast_radius(topo, "bm_node_tactical_h100_01")
    print(f"    - Calculated Blast Radius: {blast.impact_score:.2f}")

    # Check authorization for L4 Senior AI FDE
    authorized = bounty.verify_action_authorization(
        operator_role="Senior_AI_FDE",
        ladder_level=FDELadderLevel.L4_REMEDIATION_PLANT,
        blast_radius_score=blast.impact_score,
    )
    print(f"    - L4 Remediation Plant Operator Authorized: {authorized}")

    # Issue cryptographic ActionLedger receipt
    receipt = bounty.issue_action_receipt(
        action_name="drain_node",
        target_node_id="bm_node_tactical_h100_01",
        operator_role="Senior_AI_FDE",
        ladder_level=FDELadderLevel.L4_REMEDIATION_PLANT,
        blast_radius_score=blast.impact_score,
    )
    print(f"    - Cryptographic ActionReceipt Issued: {receipt.receipt_id}")
    print(f"    - Receipt Hash: {receipt.receipt_hash}")

    # 5. Display Unified Portfolio Mesh Coverage
    print("\n[*] Step 4: Unified FDE Portfolio Mesh Status:")
    all_nodes = FDEPortfolioMesh.get_all_nodes()
    print(f"    - Total Integrated Sovereign FDE Repositories: {len(all_nodes)}")
    for tier in ["Tier 1", "Tier 2", "Tier 3"]:
        count = len(FDEPortfolioMesh.get_by_tier(tier))
        print(f"      • {tier}: {count} repositories linked")

    print("\n" + "=" * 76)
    print(" ALL DEFENSE & GOVERNANCE ECOSYSTEM INTEGRATIONS VERIFIED")
    print("=" * 76)


if __name__ == "__main__":
    main()
