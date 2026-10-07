"""Unit tests for the Causal Infrastructure Knowledge Graph engine."""

import unittest

from apex_fde_matrix.graph.blast_radius import (
    compute_betweenness_centrality,
    compute_blast_radius,
    compute_pagerank,
)
from apex_fde_matrix.graph.model import (
    EdgeType,
    InfraEdge,
    InfraNode,
    NodeStatus,
    ResourceType,
)
from apex_fde_matrix.graph.query_engine import GraphQueryEngine
from apex_fde_matrix.graph.topology import InfrastructureTopology


class TestGraphTopology(unittest.TestCase):
    def setUp(self) -> None:
        self.topo = InfrastructureTopology()
        # Node A: Database
        self.node_a = InfraNode(
            id="db_primary",
            name="Primary Postgres",
            resource_type=ResourceType.DATABASE,
            criticality_weight=9.0,
        )
        # Node B: API Gateway
        self.node_b = InfraNode(
            id="api_gateway",
            name="API Gateway",
            resource_type=ResourceType.K8S_SERVICE,
            criticality_weight=5.0,
        )
        # Node C: Worker
        self.node_c = InfraNode(
            id="worker_01",
            name="Worker Pod",
            resource_type=ResourceType.K8S_POD,
            criticality_weight=2.0,
        )
        self.topo.add_node(self.node_a)
        self.topo.add_node(self.node_b)
        self.topo.add_node(self.node_c)

        # worker -> api_gateway -> db_primary
        self.topo.add_edge(InfraEdge(source_id="worker_01", target_id="api_gateway", edge_type=EdgeType.DEPENDS_ON))
        self.topo.add_edge(InfraEdge(source_id="api_gateway", target_id="db_primary", edge_type=EdgeType.DEPENDS_ON))

    def test_node_and_edge_counts(self) -> None:
        self.assertEqual(self.topo.node_count, 3)
        self.assertEqual(self.topo.edge_count, 2)

    def test_shortest_path(self) -> None:
        path = self.topo.find_shortest_path("worker_01", "db_primary")
        self.assertEqual(path, ["worker_01", "api_gateway", "db_primary"])

    def test_blast_radius_calculation(self) -> None:
        # If db_primary fails, both api_gateway and worker_01 are impacted
        res = compute_blast_radius(self.topo, "db_primary", attenuation_factor=0.8)
        self.assertEqual(res.target_node_id, "db_primary")
        self.assertEqual(res.affected_nodes_count, 2)
        self.assertIn("api_gateway", res.direct_dependents)
        self.assertIn("worker_01", res.transitive_dependents)
        # Impact: 9.0 (db) + 5.0 * 0.8^1 (api) + 2.0 * 0.8^2 (worker) = 9 + 4 + 1.28 = 14.28
        self.assertAlmostEqual(res.impact_score, 14.28, places=2)

    def test_pagerank_and_betweenness(self) -> None:
        pr = compute_pagerank(self.topo)
        self.assertEqual(len(pr), 3)
        # db_primary has the most in-degree flow, should have highest rank
        self.assertTrue(pr["db_primary"] > pr["worker_01"])

        bw = compute_betweenness_centrality(self.topo)
        self.assertEqual(len(bw), 3)
        # api_gateway sits on the path between worker and db
        self.assertTrue(bw["api_gateway"] >= bw["worker_01"])

    def test_snapshot_restore(self) -> None:
        snap = self.topo.snapshot()
        self.topo.remove_node("worker_01")
        self.assertEqual(self.topo.node_count, 2)

        self.topo.restore_snapshot(snap)
        self.assertEqual(self.topo.node_count, 3)
        self.assertIsNotNone(self.topo.get_node("worker_01"))

    def test_query_engine(self) -> None:
        qe = GraphQueryEngine(self.topo)
        dbs = qe.find_nodes(resource_type=ResourceType.DATABASE)
        self.assertEqual(len(dbs), 1)
        self.assertEqual(dbs[0].id, "db_primary")


if __name__ == "__main__":
    unittest.main()
