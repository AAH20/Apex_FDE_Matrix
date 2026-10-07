"""Apex_FDE_Matrix: Bare-Metal & GPU Cluster Topology Adapter.

Parses physical GPU fabrics (H100, B200, NVLink, RoCE v2, PCIe) into the digital twin.
"""

from __future__ import annotations

from typing import Any, Dict, List

from apex_fde_matrix.graph.model import (
    EdgeType,
    InfraEdge,
    InfraNode,
    NodeStatus,
    ResourceType,
)
from apex_fde_matrix.graph.topology import InfrastructureTopology


class BareMetalGPUAdapter:
    """Ingests physical server and high-speed GPU interconnect topologies."""

    @classmethod
    def ingest_gpu_cluster(
        cls,
        topology: InfrastructureTopology,
        cluster_name: str,
        node_count: int = 4,
        gpus_per_node: int = 8,
    ) -> None:
        """Construct synthetic or discovered multi-node GPU cluster with NVLink and RoCE."""
        spine_router = InfraNode(
            id=f"{cluster_name}_spine_bgp_01",
            name=f"{cluster_name} 800G Spine BGP Router",
            resource_type=ResourceType.BGP_ROUTER,
            status=NodeStatus.HEALTHY,
            criticality_weight=9.5,
            metadata={"bandwidth_tbps": 51.2, "protocols": ["BGP-EVPN", "RoCEv2"]},
        )
        topology.add_node(spine_router)

        for n_idx in range(1, node_count + 1):
            node_id = f"bm_node_{cluster_name}_{n_idx:02d}"
            bm_node = InfraNode(
                id=node_id,
                name=f"DGX-H100 Node {n_idx:02d}",
                resource_type=ResourceType.BARE_METAL_NODE,
                status=NodeStatus.HEALTHY,
                criticality_weight=6.0,
                metadata={"arch": "x86_64", "numa_nodes": 2, "ram_gb": 2048},
            )
            topology.add_node(bm_node)

            # Node connects to Spine router via RoCE v2
            topology.add_edge(
                InfraEdge(
                    source_id=node_id,
                    target_id=spine_router.id,
                    edge_type=EdgeType.CONNECTED_VIA,
                    bandwidth_gbps=800.0,
                )
            )

            # Add GPUs to this bare-metal host
            prev_gpu_id: str | None = None
            for g_idx in range(1, gpus_per_node + 1):
                gpu_id = f"{node_id}_gpu_{g_idx:02d}"
                gpu_node = InfraNode(
                    id=gpu_id,
                    name=f"NVIDIA H100 SXM5 {g_idx:02d}",
                    resource_type=ResourceType.GPU_DEVICE,
                    status=NodeStatus.HEALTHY,
                    criticality_weight=4.0,
                    metadata={"vram_gb": 80, "pcie_gen": 5},
                )
                topology.add_node(gpu_node)

                # Bare-metal host HOSTS GPU
                topology.add_edge(
                    InfraEdge(
                        source_id=node_id,
                        target_id=gpu_id,
                        edge_type=EdgeType.HOSTS,
                    )
                )

                # NVLink interconnect between adjacent GPUs
                if prev_gpu_id:
                    topology.add_edge(
                        InfraEdge(
                            source_id=prev_gpu_id,
                            target_id=gpu_id,
                            edge_type=EdgeType.CONNECTED_VIA,
                            bandwidth_gbps=900.0,
                            metadata={"fabric": "NVLink4"},
                        )
                    )
                prev_gpu_id = gpu_id
