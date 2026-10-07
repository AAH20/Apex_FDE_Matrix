"""Apex_FDE_Matrix: Paperclip + Hermes + NVIDIA NIM Sovereign Stack Demo.

Demonstrates how Paperclip provides organizational governance and budget caps,
Nous Research Hermes Agent acts as the persistent worker,
NVIDIA NIM provides open-weight inference (Nemotron/Hermes 3/DeepSeek),
and Apex_FDE_Matrix provides the Causal Infrastructure Knowledge Graph & Safe Actuation.
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
    compute_blast_radius,
)
from apex_fde_matrix.adapters.baremetal import BareMetalGPUAdapter
from apex_fde_matrix.adapters.hermes import HermesAgentAdapter
from apex_fde_matrix.adapters.nim import NvidiaNIMClient
from apex_fde_matrix.adapters.paperclip import PaperclipCompanyAdapter


def main() -> None:
    print("=" * 76)
    print(" Apex_FDE_Matrix: Sovereign Enterprise Stack Integration Demo")
    print(" [Paperclip (Company OS) + Hermes (Agent) + NVIDIA NIM + Matrix]")
    print("=" * 76)

    # 1. Initialize Paperclip "Company OS"
    print("\n[*] Step 1: Initializing Paperclip Corporate Org Chart & Budgets...")
    paperclip = PaperclipCompanyAdapter("Apex Sovereign Infrastructure Corp")
    paperclip.register_agent("hermes_sre_01", role="Forward Deployed SRE", max_spend_per_action=10.0)
    goal = paperclip.create_goal(
        title="Zero-Outage Autonomous GPU Cluster Management",
        assigned_agent_id="hermes_sre_01",
        budget_usd_cap=50.0,
    )
    print(f"    - Goal Registered: '{goal.title}' [Budget Cap: ${goal.budget_usd_cap}]")

    # 2. Initialize Hermes Agent & Bind Matrix Skills
    print("\n[*] Step 2: Bootstrapping Hermes Agent with Matrix Skills & Memory...")
    hermes = HermesAgentAdapter(agent_id="hermes_sre_01")
    skills = hermes.register_matrix_skills()
    print(f"    - Registered {len(skills)} Matrix skills into Hermes skill bank.")

    # 3. Setup Digital Twin
    print("\n[*] Step 3: Spinning up Causal Infrastructure Knowledge Graph...")
    topo = InfrastructureTopology()
    BareMetalGPUAdapter.ingest_gpu_cluster(topo, cluster_name="enterprise_dgx", node_count=4, gpus_per_node=8)
    print(f"    - Ingested {topo.node_count} nodes & {topo.edge_count} interconnects into digital twin.")

    # 4. Simulated Anomaly on GPU Node 02
    target_node = "bm_node_enterprise_dgx_02"
    print(f"\n[*] Step 4: Incident Detected on '{target_node}'. Querying NIM for reasoning...")
    nim = NvidiaNIMClient(mock_mode=True, default_model="nvidia/llama-3.1-nemotron-70b")
    nim_resp = nim.chat_completion([{"role": "user", "content": f"Analyze node {target_node}"}])
    print(f"    - NIM (Nemotron 70B): {nim_resp['choices'][0]['message']['content']}")

    # 5. Pre-Execution Blast Radius Simulation via Matrix
    print("\n[*] Step 5: Hermes executes Matrix Blast Radius Verification...")
    blast = compute_blast_radius(topo, target_node)
    print(f"    - Blast Radius Impact Score: {blast.impact_score:.2f}")
    print(f"    - Direct Dependents at Risk: {blast.direct_dependents}")

    # 6. Budget Authorization via Paperclip
    print("\n[*] Step 6: Requesting Paperclip budget approval for remediation mutation...")
    authorized = paperclip.authorize_mutation_spend(goal.goal_id, hermes.agent_id, estimated_cost_usd=2.50)
    print(f"    - Paperclip Budget Authorization: {'APPROVED' if authorized else 'DENIED'}")
    print(f"    - Remaining Goal Budget: ${goal.budget_usd_cap - goal.current_spend_usd:.2f}")

    # 7. Safe Execution with Automatic Rollback
    print("\n[*] Step 7: Executing guarded mutation plan with rollback guarantee...")
    executor = BoundedExecutor(topo)
    plan = MutationPlan(
        plan_id="hermes_drain_dgx_02",
        actions=[
            MutationAction(action_id="cordon", action_type=ActionType.CORDON_NODE, target_node_id=target_node),
            MutationAction(action_id="drain", action_type=ActionType.DRAIN_NODE, target_node_id=target_node),
        ],
        max_blast_radius=25.0,
        description="Hermes-initiated bounded drain of degraded DGX node",
    )
    result = executor.execute_plan(plan)
    print(f"    - Execution Success: {result.success} (Time: {result.elapsed_ms} ms)")

    # 8. Record to Hermes Persistent Episodic Memory
    hermes.record_episodic_memory(
        incident_id="INC-PAPERCLIP-01",
        impacted_node_id=target_node,
        remediation_action="drain_and_cordon",
        success=result.success,
        notes="Successfully drained without RoCE spine degradation",
    )
    print("\n[+] Step 8: Outcome written to Hermes episodic memory across sessions.")
    print("=" * 76)


if __name__ == "__main__":
    main()
