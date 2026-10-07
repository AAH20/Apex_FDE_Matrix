"""Unit tests for the Bounded Actuation & Compensatory Rollback Engine."""

import unittest

from apex_fde_matrix.actuation.executor import BoundedExecutor
from apex_fde_matrix.actuation.mutation import (
    ActionType,
    MutationAction,
    MutationPlan,
)
from apex_fde_matrix.actuation.rollback import RollbackDAGGenerator
from apex_fde_matrix.graph.model import InfraNode, NodeStatus, ResourceType
from apex_fde_matrix.graph.topology import InfrastructureTopology


class TestActuationAndRollback(unittest.TestCase):
    def setUp(self) -> None:
        self.topo = InfrastructureTopology()
        self.node = InfraNode(
            id="node_prod_1",
            name="Prod Node 1",
            resource_type=ResourceType.BARE_METAL_NODE,
            status=NodeStatus.HEALTHY,
        )
        self.topo.add_node(self.node)
        self.executor = BoundedExecutor(self.topo)

    def test_forward_execution_success(self) -> None:
        plan = MutationPlan(
            plan_id="plan_01",
            actions=[
                MutationAction(
                    action_id="act_01",
                    action_type=ActionType.CORDON_NODE,
                    target_node_id="node_prod_1",
                ),
                MutationAction(
                    action_id="act_02",
                    action_type=ActionType.UPDATE_CONFIG,
                    target_node_id="node_prod_1",
                    parameters={"kernel_tuning": "performance"},
                ),
            ],
            max_blast_radius=10.0,
            description="Cordon and tune",
        )
        res = self.executor.execute_plan(plan)
        self.assertTrue(res.success)
        self.assertFalse(res.rolled_back)
        self.assertEqual(len(res.executed_action_ids), 2)
        # Verify state mutated
        node = self.topo.get_node("node_prod_1")
        self.assertTrue(node.metadata.get("cordoned"))
        self.assertEqual(node.metadata.get("kernel_tuning"), "performance")

    def test_rollback_on_failure(self) -> None:
        plan = MutationPlan(
            plan_id="plan_fail",
            actions=[
                MutationAction(
                    action_id="act_01",
                    action_type=ActionType.CORDON_NODE,
                    target_node_id="node_prod_1",
                ),
                # This action targets non-existent node -> fails!
                MutationAction(
                    action_id="act_02_fail",
                    action_type=ActionType.CORDON_NODE,
                    target_node_id="non_existent_node",
                ),
            ],
            max_blast_radius=10.0,
            description="Fail and rollback",
        )
        res = self.executor.execute_plan(plan)
        self.assertFalse(res.success)
        self.assertTrue(res.rolled_back)
        self.assertIn("non_existent_node", str(res.error_message))

        # Node 1 should be restored to prior uncordoned healthy state!
        node = self.topo.get_node("node_prod_1")
        self.assertEqual(node.status, NodeStatus.HEALTHY)
        self.assertNotIn("cordoned", node.metadata)

    def test_rollback_dag_generator(self) -> None:
        forward_plan = MutationPlan(
            plan_id="fwd_plan",
            actions=[
                MutationAction(action_id="a1", action_type=ActionType.CORDON_NODE, target_node_id="node_prod_1"),
                MutationAction(action_id="a2", action_type=ActionType.ATTACH_EBPF_PROBE, target_node_id="node_prod_1"),
            ],
            max_blast_radius=10.0,
            description="Test plan",
        )
        rollback = RollbackDAGGenerator.generate_rollback_plan(forward_plan)
        self.assertEqual(len(rollback.actions), 2)
        # Sequence must be reversed!
        self.assertEqual(rollback.actions[0].action_type, ActionType.DETACH_EBPF_PROBE)
        self.assertEqual(rollback.actions[1].action_type, ActionType.UNCORDON_NODE)


if __name__ == "__main__":
    unittest.main()
