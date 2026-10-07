"""Apex_FDE_Matrix: Mutation Action & Execution Plan Modeling.

Formal representation of infrastructure mutations with Hoare pre/post-conditions.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


class ActionType(str, Enum):
    """Atomic infrastructure mutation primitives."""
    CORDON_NODE = "cordon_node"
    UNCORDON_NODE = "uncordon_node"
    DRAIN_NODE = "drain_node"
    SCALE_REPLICAS = "scale_replicas"
    ATTACH_EBPF_PROBE = "attach_ebpf_probe"
    DETACH_EBPF_PROBE = "detach_ebpf_probe"
    PIVOT_BGP_ROUTE = "pivot_bgp_route"
    RESTORE_BGP_ROUTE = "restore_bgp_route"
    UPDATE_CONFIG = "update_config"


@dataclass
class MutationAction:
    """An individual atomic mutation step in an infrastructure DAG."""
    action_id: str
    action_type: ActionType
    target_node_id: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    inverse_action_type: Optional[ActionType] = None
    inverse_parameters: Dict[str, Any] = field(default_factory=dict)
    depends_on_action_ids: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action_id": self.action_id,
            "action_type": self.action_type.value,
            "target_node_id": self.target_node_id,
            "parameters": self.parameters,
            "inverse_action_type": self.inverse_action_type.value if self.inverse_action_type else None,
            "inverse_parameters": self.inverse_parameters,
            "depends_on": self.depends_on_action_ids,
        }


@dataclass
class MutationPlan:
    """Ordered DAG of mutation actions forming a coherent infrastructure change."""
    plan_id: str
    actions: List[MutationAction]
    max_blast_radius: float
    description: str
    created_at: float = field(default_factory=time.time)

    def get_action(self, action_id: str) -> Optional[MutationAction]:
        for act in self.actions:
            if act.action_id == action_id:
                return act
        return None
