"""Apex_FDE_Matrix: Full Autonomous Incident Remediation Walkthrough.

Demonstrates incident detection, multi-agent triage, blast radius calculation,
consensus voting, and bounded execution with compensatory rollback.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from apex_fde_matrix import (
    ActionType,
    BoundedExecutor,
    InfrastructureTopology,
    MutationAction,
    MutationPlan,
    SRESwarmOrchestrator,
)
from apex_fde_matrix.adapters.baremetal import BareMetalGPUAdapter
from apex_fde_matrix.adapters.kubernetes import KubernetesTopologyAdapter


def main() -> None:
    print("=" * 72)
    print(" Apex_FDE_Matrix: Autonomous SRE Incident Remediation Demo")
    print("=" * 72)

    # 1. Setup digital twin
    topo = InfrastructureTopology()
    BareMetalGPUAdapter.ingest_gpu_cluster(topo, "h100_cluster", node_count=3, gpus_per_node=4)
    KubernetesTopologyAdapter.ingest_service_stack(
        topo, "serving", "nemotron_inference", replica_count=3, host_node_id="bm_node_h100_cluster_01"
    )

    print(f"[*] Ingested digital twin with {topo.node_count} nodes.")

    # 2. Trigger SRE swarm diagnosis on degraded node
    orchestrator = SRESwarmOrchestrator(topo)
    diagnosis = orchestrator.handle_incident(
        incident_id="INC-9912",
        impacted_node_id="bm_node_h100_cluster_01",
        symptom_description="High NVLink packet error rate & PCIe bus reset",
        max_acceptable_blast_radius=30.0,
    )

    print(f"\n[+] Triage Complete:")
    print(f"    - Blast Radius Impact: {diagnosis['blast_radius']['impact_score']}")
    print(f"    - Consensus Approved:  {diagnosis['consensus']['approved']}")
    print(f"    - Consensus Hash:      {diagnosis['consensus']['consensus_hash'][:16]}...")

    # 3. Formulate bounded mutation DAG
    executor = BoundedExecutor(topo)
    plan = MutationPlan(
        plan_id="remediate_inc_9912",
        actions=[
            MutationAction(
                action_id="step_1_cordon",
                action_type=ActionType.CORDON_NODE,
                target_node_id="bm_node_h100_cluster_01",
            ),
            MutationAction(
                action_id="step_2_drain",
                action_type=ActionType.DRAIN_NODE,
                target_node_id="bm_node_h100_cluster_01",
            ),
        ],
        max_blast_radius=30.0,
        description="Safely cordon and drain node 01 to allow PCIe warm reset",
    )

    # 4. Execute mutation with rollback guarantees
    print("\n[*] Executing verified mutation plan...")
    result = executor.execute_plan(plan)
    print(f"    - Success: {result.success}")
    print(f"    - Actions Executed: {result.executed_action_ids}")
    print(f"    - Execution Time: {result.elapsed_ms} ms")

    # 5. Verify node state in digital twin
    node = topo.get_node("bm_node_h100_cluster_01")
    print(f"\n[+] Node State: {node.status.value} (Cordoned: {node.metadata.get('cordoned')})")
    print("=" * 72)


if __name__ == "__main__":
    main()
