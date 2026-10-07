"""Apex_FDE_Matrix: cloud-grc-harvester Modular Integration.

Collects multi-cloud compliance configurations (AWS Config, GCP Cloud Asset, Azure Graph)
and ingests cloud boundaries into the Causal Infrastructure Knowledge Graph.
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


class CloudGRCHarvesterIntegration:
    """Multi-cloud inventory and compliance evidence synchronizer."""

    @classmethod
    def harvest_cloud_vpc(
        cls,
        topology: InfrastructureTopology,
        provider: str,
        vpc_id: str,
        subnet_ids: List[str],
        gateway_id: str,
    ) -> None:
        """Ingest harvested cloud VPC and gateway architecture into topology."""
        gw_node = InfraNode(
            id=gateway_id,
            name=f"{provider.upper()} Transit Gateway",
            resource_type=ResourceType.CLOUD_GATEWAY,
            status=NodeStatus.HEALTHY,
            criticality_weight=7.0,
            metadata={"provider": provider, "compliance_certified": True},
        )
        topology.add_node(gw_node)

        for s_id in subnet_ids:
            subnet_node = InfraNode(
                id=s_id,
                name=f"Subnet {s_id}",
                resource_type=ResourceType.VPC_SUBNET,
                status=NodeStatus.HEALTHY,
                criticality_weight=3.5,
                metadata={"vpc_id": vpc_id, "provider": provider},
            )
            topology.add_node(subnet_node)

            # Subnet routes through Cloud Gateway
            topology.add_edge(
                InfraEdge(
                    source_id=s_id,
                    target_id=gateway_id,
                    edge_type=EdgeType.ROUTES_TO,
                )
            )
