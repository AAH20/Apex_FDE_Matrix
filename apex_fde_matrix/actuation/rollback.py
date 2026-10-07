"""Apex_FDE_Matrix: Compensatory Rollback DAG Generator.

Synthesizes exact mathematical inverse actions and reversal dependency trees.
"""

from __future__ import annotations

import uuid
from typing import List

from apex_fde_matrix.actuation.mutation import (
    ActionType,
    MutationAction,
    MutationPlan,
)


class RollbackDAGGenerator:
    """Derives deterministic compensatory inverse plans from forward execution DAGs."""

    # Default semantic inverse pairings
    INVERSE_PAIRS = {
        ActionType.CORDON_NODE: ActionType.UNCORDON_NODE,
        ActionType.UNCORDON_NODE: ActionType.CORDON_NODE,
        ActionType.DRAIN_NODE: ActionType.UNCORDON_NODE,
        ActionType.ATTACH_EBPF_PROBE: ActionType.DETACH_EBPF_PROBE,
        ActionType.DETACH_EBPF_PROBE: ActionType.ATTACH_EBPF_PROBE,
        ActionType.PIVOT_BGP_ROUTE: ActionType.RESTORE_BGP_ROUTE,
        ActionType.RESTORE_BGP_ROUTE: ActionType.PIVOT_BGP_ROUTE,
    }

    @classmethod
    def generate_rollback_plan(cls, forward_plan: MutationPlan) -> MutationPlan:
        """Create an exact compensatory inverse execution DAG.

        Reverses action order: [A_1, A_2, ..., A_k] -> [A_k_inv, ..., A_2_inv, A_1_inv].
        """
        rollback_actions: List[MutationAction] = []
        prev_rollback_id: str | None = None

        for forward_action in reversed(forward_plan.actions):
            rollback_id = f"rb_{forward_action.action_id}_{uuid.uuid4().hex[:6]}"

            # Determine inverse action type
            inv_type = forward_action.inverse_action_type or cls.INVERSE_PAIRS.get(
                forward_action.action_type, ActionType.UPDATE_CONFIG
            )

            # Determine inverse parameters
            inv_params = dict(forward_action.inverse_parameters)
            if not inv_params and forward_action.action_type == ActionType.SCALE_REPLICAS:
                # Invert replica scale: restore prior replica count if present
                prior_replicas = forward_action.parameters.get("prior_replicas", 1)
                inv_params = {"replicas": prior_replicas}

            rollback_action = MutationAction(
                action_id=rollback_id,
                action_type=inv_type,
                target_node_id=forward_action.target_node_id,
                parameters=inv_params,
                depends_on_action_ids=[prev_rollback_id] if prev_rollback_id else [],
            )
            rollback_actions.append(rollback_action)
            prev_rollback_id = rollback_id

        return MutationPlan(
            plan_id=f"rollback_{forward_plan.plan_id}",
            actions=rollback_actions,
            max_blast_radius=forward_plan.max_blast_radius,
            description=f"Compensatory Rollback DAG for {forward_plan.plan_id}",
        )
