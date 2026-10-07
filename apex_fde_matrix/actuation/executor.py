"""Apex_FDE_Matrix: Bounded Mutation Sandbox Executor.

Step-by-step DAG execution with automatic rollback triggering upon invariant violation.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from apex_fde_matrix.actuation.mutation import (
    ActionType,
    MutationAction,
    MutationPlan,
)
from apex_fde_matrix.actuation.rollback import RollbackDAGGenerator
from apex_fde_matrix.graph.model import NodeStatus
from apex_fde_matrix.graph.topology import InfrastructureTopology


@dataclass
class ExecutionResult:
    """Audit report of a mutation execution cycle."""
    plan_id: str
    success: bool
    executed_action_ids: List[str]
    rolled_back: bool
    rollback_action_ids: List[str]
    error_message: Optional[str]
    elapsed_ms: float
    audit_trail: List[Dict[str, Any]] = field(default_factory=list)


class BoundedExecutor:
    """Executes mutation plans with atomic rollback safety in the digital twin."""

    def __init__(self, topology: InfrastructureTopology) -> None:
        self.topology = topology

    def execute_plan(
        self,
        plan: MutationPlan,
        dry_run: bool = False,
    ) -> ExecutionResult:
        """Execute all actions in plan DAG. Trigger compensatory rollback on any error."""
        start_time = time.perf_counter()
        snapshot = self.topology.snapshot()
        executed_actions: List[MutationAction] = []
        audit_trail: List[Dict[str, Any]] = []

        try:
            for action in plan.actions:
                audit_entry = {
                    "action_id": action.action_id,
                    "action_type": action.action_type.value,
                    "target_node_id": action.target_node_id,
                    "dry_run": dry_run,
                    "timestamp": time.time(),
                }

                if not dry_run:
                    self._apply_action(action)

                executed_actions.append(action)
                audit_trail.append(audit_entry)

            elapsed = (time.perf_counter() - start_time) * 1000.0
            return ExecutionResult(
                plan_id=plan.plan_id,
                success=True,
                executed_action_ids=[a.action_id for a in executed_actions],
                rolled_back=False,
                rollback_action_ids=[],
                error_message=None,
                elapsed_ms=round(elapsed, 3),
                audit_trail=audit_trail,
            )

        except Exception as exc:
            # Failure detected -> execute compensatory rollback DAG
            err_msg = str(exc)
            audit_trail.append({"event": "execution_failure", "error": err_msg, "timestamp": time.time()})

            executed_subplan = MutationPlan(
                plan_id=f"partial_{plan.plan_id}",
                actions=executed_actions,
                max_blast_radius=plan.max_blast_radius,
                description="Partial plan for rollback",
            )
            rollback_plan = RollbackDAGGenerator.generate_rollback_plan(executed_subplan)

            rollback_executed: List[str] = []
            for rb_act in rollback_plan.actions:
                try:
                    if not dry_run:
                        self._apply_action(rb_act)
                    rollback_executed.append(rb_act.action_id)
                except Exception as rb_exc:
                    audit_trail.append({
                        "event": "rollback_error",
                        "action_id": rb_act.action_id,
                        "error": str(rb_exc),
                    })

            # Re-verify and restore snapshot state integrity if necessary
            if not dry_run:
                self.topology.restore_snapshot(snapshot)

            elapsed = (time.perf_counter() - start_time) * 1000.0
            return ExecutionResult(
                plan_id=plan.plan_id,
                success=False,
                executed_action_ids=[a.action_id for a in executed_actions],
                rolled_back=True,
                rollback_action_ids=rollback_executed,
                error_message=err_msg,
                elapsed_ms=round(elapsed, 3),
                audit_trail=audit_trail,
            )

    def _apply_action(self, action: MutationAction) -> None:
        """Apply mutation semantics to the in-memory digital twin."""
        node = self.topology.get_node(action.target_node_id)
        if node is None:
            raise KeyError(f"Target node '{action.target_node_id}' does not exist.")

        if action.action_type in (ActionType.CORDON_NODE, ActionType.DRAIN_NODE):
            node.status = NodeStatus.DEGRADED
            node.metadata["cordoned"] = True
        elif action.action_type == ActionType.UNCORDON_NODE:
            node.status = NodeStatus.HEALTHY
            node.metadata.pop("cordoned", None)
        elif action.action_type == ActionType.SCALE_REPLICAS:
            replicas = action.parameters.get("replicas", 1)
            node.metadata["replicas"] = replicas
        elif action.action_type == ActionType.ATTACH_EBPF_PROBE:
            probes = node.metadata.setdefault("ebpf_probes", [])
            probes.append(action.parameters.get("probe_id", "trace_sock"))
        elif action.action_type == ActionType.DETACH_EBPF_PROBE:
            probes = node.metadata.get("ebpf_probes", [])
            probe_id = action.parameters.get("probe_id", "trace_sock")
            if probe_id in probes:
                probes.remove(probe_id)
        elif action.action_type == ActionType.PIVOT_BGP_ROUTE:
            node.metadata["bgp_route_override"] = action.parameters.get("next_hop")
        elif action.action_type == ActionType.RESTORE_BGP_ROUTE:
            node.metadata.pop("bgp_route_override", None)
        elif action.action_type == ActionType.UPDATE_CONFIG:
            for k, v in action.parameters.items():
                node.metadata[k] = v
