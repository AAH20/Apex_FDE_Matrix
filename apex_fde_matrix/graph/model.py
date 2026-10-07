"""Apex_FDE_Matrix: Graph Data Models and Primitive Structures.

Pure Python 3.10+ standard library. Zero external dependencies.
Incubated under Apex Growth Systems LLC - Sole Managing Member: Ahmed Hassan.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set


class ResourceType(str, Enum):
    """Categorization of infrastructure resources across physical and logical domains."""
    # Physical / Hardware
    BARE_METAL_NODE = "bare_metal_node"
    GPU_DEVICE = "gpu_device"
    NVLINK_FABRIC = "nvlink_fabric"
    ROCE_INTERFACE = "roce_interface"
    BGP_ROUTER = "bgp_router"

    # Virtual / Orchestration
    K8S_CLUSTER = "k8s_cluster"
    K8S_NAMESPACE = "k8s_namespace"
    K8S_DEPLOYMENT = "k8s_deployment"
    K8S_POD = "k8s_pod"
    K8S_SERVICE = "k8s_service"

    # Network / Kernel
    EBPF_SOCKET_PROBE = "ebpf_socket_probe"
    VPC_SUBNET = "vpc_subnet"
    CLOUD_GATEWAY = "cloud_gateway"
    DATABASE = "database"


class EdgeType(str, Enum):
    """Directional dependency and physical connection types."""
    DEPENDS_ON = "depends_on"
    ROUTES_TO = "routes_to"
    HOSTS = "hosts"
    REPLICATES_TO = "replicates_to"
    POWERS = "powers"
    CONNECTED_VIA = "connected_via"
    MONITORS = "monitors"


class NodeStatus(str, Enum):
    """Operational health state of an infrastructure node."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    ISOLATED = "isolated"
    UNKNOWN = "unknown"


@dataclass
class InfraNode:
    """Represents a discrete infrastructure asset in the digital twin."""
    id: str
    name: str
    resource_type: ResourceType
    status: NodeStatus = NodeStatus.HEALTHY
    criticality_weight: float = 1.0  # 0.1 (ephemeral worker) to 10.0 (core database/BGP spine)
    metadata: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, float] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "resource_type": self.resource_type.value,
            "status": self.status.value,
            "criticality_weight": self.criticality_weight,
            "metadata": self.metadata,
            "metrics": self.metrics,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> InfraNode:
        return cls(
            id=data["id"],
            name=data["name"],
            resource_type=ResourceType(data["resource_type"]),
            status=NodeStatus(data.get("status", NodeStatus.HEALTHY.value)),
            criticality_weight=float(data.get("criticality_weight", 1.0)),
            metadata=data.get("metadata", {}),
            metrics=data.get("metrics", {}),
            created_at=data.get("created_at", time.time()),
        )


@dataclass
class InfraEdge:
    """Represents a directional dependency or transmission route between nodes."""
    source_id: str
    target_id: str
    edge_type: EdgeType
    latency_ms: float = 0.0
    bandwidth_gbps: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "edge_type": self.edge_type.value,
            "latency_ms": self.latency_ms,
            "bandwidth_gbps": self.bandwidth_gbps,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> InfraEdge:
        return cls(
            source_id=data["source_id"],
            target_id=data["target_id"],
            edge_type=EdgeType(data["edge_type"]),
            latency_ms=float(data.get("latency_ms", 0.0)),
            bandwidth_gbps=float(data.get("bandwidth_gbps", 0.0)),
            metadata=data.get("metadata", {}),
        )


@dataclass
class BlastRadiusResult:
    """Formal mathematical blast radius report for a potential mutation target."""
    target_node_id: str
    impact_score: float
    affected_nodes_count: int
    direct_dependents: List[str]
    transitive_dependents: List[str]
    critical_dependents: List[str]
    attenuation_factor: float
    calculation_time_ms: float
