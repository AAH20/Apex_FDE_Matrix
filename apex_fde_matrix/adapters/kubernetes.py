"""Apex_FDE_Matrix: Kubernetes Multi-Cluster Topology Adapter.

Maps Namespaces, Deployments, Pods, and Services into the digital twin.
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


class KubernetesTopologyAdapter:
    """Ingests Kubernetes microservice architectures into the infrastructure graph."""

    @classmethod
    def ingest_service_stack(
        cls,
        topology: InfrastructureTopology,
        namespace: str,
        service_name: str,
        replica_count: int,
        host_node_id: str,
    ) -> None:
        """Create Service -> Deployment -> Pods hierarchy mapped to physical host."""
        svc_id = f"k8s_svc_{namespace}_{service_name}"
        svc_node = InfraNode(
            id=svc_id,
            name=f"k8s Service {service_name}",
            resource_type=ResourceType.K8S_SERVICE,
            status=NodeStatus.HEALTHY,
            criticality_weight=5.0,
            metadata={"namespace": namespace, "type": "ClusterIP"},
        )
        topology.add_node(svc_node)

        deploy_id = f"k8s_deploy_{namespace}_{service_name}"
        deploy_node = InfraNode(
            id=deploy_id,
            name=f"Deployment {service_name}",
            resource_type=ResourceType.K8S_DEPLOYMENT,
            status=NodeStatus.HEALTHY,
            criticality_weight=4.0,
            metadata={"replicas": replica_count},
        )
        topology.add_node(deploy_node)

        # Service routes to Deployment
        topology.add_edge(
            InfraEdge(
                source_id=svc_id,
                target_id=deploy_id,
                edge_type=EdgeType.ROUTES_TO,
            )
        )

        for p_idx in range(1, replica_count + 1):
            pod_id = f"k8s_pod_{namespace}_{service_name}_{p_idx:02d}"
            pod_node = InfraNode(
                id=pod_id,
                name=f"Pod {service_name}-{p_idx:02d}",
                resource_type=ResourceType.K8S_POD,
                status=NodeStatus.HEALTHY,
                criticality_weight=2.0,
                metadata={"pod_ip": f"10.244.1.{10 + p_idx}"},
            )
            topology.add_node(pod_node)

            # Deployment manages/hosts Pod
            topology.add_edge(
                InfraEdge(
                    source_id=deploy_id,
                    target_id=pod_id,
                    edge_type=EdgeType.HOSTS,
                )
            )

            # Pod is hosted on bare-metal node if node exists
            if topology.get_node(host_node_id):
                topology.add_edge(
                    InfraEdge(
                        source_id=pod_id,
                        target_id=host_node_id,
                        edge_type=EdgeType.DEPENDS_ON,
                    )
                )
