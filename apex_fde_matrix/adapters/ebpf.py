"""Apex_FDE_Matrix: eBPF Kernel Probe & Network Flow Adapter.

Ingests kernel-level socket connections, L4/L7 flow metrics, and trace probes.
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


class EBPFTelemetryAdapter:
    """Attaches kernel-level eBPF observability probes and flow maps to the topology."""

    @classmethod
    def attach_socket_probe(
        cls,
        topology: InfrastructureTopology,
        target_node_id: str,
        probe_name: str = "tcp_retransmit_monitor",
    ) -> str:
        """Attach an eBPF trace probe to a node."""
        probe_id = f"ebpf_{target_node_id}_{probe_name}"
        probe_node = InfraNode(
            id=probe_id,
            name=f"eBPF Probe: {probe_name}",
            resource_type=ResourceType.EBPF_SOCKET_PROBE,
            status=NodeStatus.HEALTHY,
            criticality_weight=1.5,
            metadata={"hook": "kprobe/tcp_v4_connect", "sampling_rate": 1.0},
        )
        topology.add_node(probe_node)

        # Probe MONITORS the target node
        topology.add_edge(
            InfraEdge(
                source_id=probe_id,
                target_id=target_node_id,
                edge_type=EdgeType.MONITORS,
            )
        )
        return probe_id

    @classmethod
    def inject_flow_telemetry(
        cls,
        topology: InfrastructureTopology,
        source_id: str,
        target_id: str,
        latency_ms: float,
        bandwidth_gbps: float,
    ) -> None:
        """Update or create edge telemetry between two nodes based on live eBPF stream."""
        existing_edge = topology.get_edge(source_id, target_id)
        if existing_edge:
            existing_edge.latency_ms = latency_ms
            existing_edge.bandwidth_gbps = bandwidth_gbps
        else:
            edge = InfraEdge(
                source_id=source_id,
                target_id=target_id,
                edge_type=EdgeType.ROUTES_TO,
                latency_ms=latency_ms,
                bandwidth_gbps=bandwidth_gbps,
            )
            topology.add_edge(edge)
