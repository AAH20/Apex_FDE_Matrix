"""Unit tests for the enterprise adapters (Paperclip, Hermes, DeepAgents, NIM, Bare-Metal, K8s, eBPF)."""

import unittest

from apex_fde_matrix.adapters.baremetal import BareMetalGPUAdapter
from apex_fde_matrix.adapters.deepagents import DeepAgentsHarnessAdapter
from apex_fde_matrix.adapters.ebpf import EBPFTelemetryAdapter
from apex_fde_matrix.adapters.hermes import HermesAgentAdapter
from apex_fde_matrix.adapters.kubernetes import KubernetesTopologyAdapter
from apex_fde_matrix.adapters.nim import NvidiaNIMClient
from apex_fde_matrix.adapters.paperclip import PaperclipCompanyAdapter
from apex_fde_matrix.graph.topology import InfrastructureTopology


class TestAdapters(unittest.TestCase):
    def test_paperclip_adapter(self) -> None:
        pc = PaperclipCompanyAdapter()
        pc.register_agent("sre_lead", "Staff SRE", max_spend_per_action=10.0)
        goal = pc.create_goal("Maintain 99.99% Availability", assigned_agent_id="sre_lead", budget_usd_cap=50.0)

        # Spend within budget
        auth1 = pc.authorize_mutation_spend(goal.goal_id, "sre_lead", 8.0)
        self.assertTrue(auth1)

        # Spend exceeding agent single action cap ($10)
        auth2 = pc.authorize_mutation_spend(goal.goal_id, "sre_lead", 15.0)
        self.assertFalse(auth2)

    def test_hermes_adapter(self) -> None:
        hermes = HermesAgentAdapter("hermes_fde_01")
        skills = hermes.register_matrix_skills()
        self.assertIn("matrix_query_topology", skills)

        hermes.record_episodic_memory("INC-1", "node_x", "cordon_node", True, "Resolved flapping route")
        recalled = hermes.recall_previous_fixes("node_x")
        self.assertEqual(len(recalled), 1)
        self.assertEqual(recalled[0]["remediation_action"], "cordon_node")

    def test_deepagents_adapter(self) -> None:
        harness = DeepAgentsHarnessAdapter("TestHarness")
        task = harness.spawn_sub_agent("kernel_auditor", "Audit dmesg log")
        self.assertEqual(task.status, "pending")

        harness.complete_sub_agent_task(task.task_id, {"kernel_panics_found": 0})
        summary = harness.consolidate_findings()
        self.assertEqual(summary["completed_count"], 1)

    def test_nim_client_mock(self) -> None:
        client = NvidiaNIMClient(mock_mode=True)
        resp = client.chat_completion([{"role": "user", "content": "check node"}])
        self.assertIn("NVIDIA NIM", resp["choices"][0]["message"]["content"])

    def test_baremetal_and_k8s_and_ebpf(self) -> None:
        topo = InfrastructureTopology()
        BareMetalGPUAdapter.ingest_gpu_cluster(topo, "cluster_alpha", node_count=2, gpus_per_node=4)
        self.assertTrue(topo.node_count > 10)

        KubernetesTopologyAdapter.ingest_service_stack(
            topo, "ml_serving", "vllm_service", replica_count=2, host_node_id="bm_node_cluster_alpha_01"
        )
        probe_id = EBPFTelemetryAdapter.attach_socket_probe(topo, "bm_node_cluster_alpha_01")
        self.assertIsNotNone(topo.get_node(probe_id))


if __name__ == "__main__":
    unittest.main()
