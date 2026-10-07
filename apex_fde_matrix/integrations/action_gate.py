"""Apex_FDE_Matrix: agent-action-gate Modular Integration.

Runtime Gate/Prove interception for agent and MCP tool calls.
Enforces strict policy that unattended destructive tools are hard DENIED.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class GateVerdict(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    REQUIRE_HUMAN_APPROVAL = "REQUIRE_HUMAN_APPROVAL"


@dataclass
class GateAuditReceipt:
    """Instant audit receipt emitted by AgentActionGate."""
    request_id: str
    tool_name: str
    target_node_id: str
    verdict: GateVerdict
    reason: str
    timestamp: float


class AgentActionGateIntegration:
    """Enforces runtime action gates on autonomous SRE agent mutations."""

    DESTRUCTIVE_ACTIONS = {
        "format_volume",
        "purge_cluster",
        "drop_database",
        "kill_all_nodes",
        "unattended_reboot",
        "delete_namespace",
    }

    def __init__(self, strict_mode: bool = True) -> None:
        self.strict_mode = strict_mode
        self.audit_log: List[GateAuditReceipt] = []

    def evaluate_tool_call(
        self,
        tool_name: str,
        target_node_id: str,
        parameters: Dict[str, Any],
        is_unattended: bool = True,
    ) -> Tuple[GateVerdict, str]:
        """Intercept and evaluate tool call safety."""
        # Rule 1: Unattended destructive actions are hard-DENIED
        if is_unattended and (tool_name.lower() in self.DESTRUCTIVE_ACTIONS or parameters.get("destructive")):
            verdict = GateVerdict.DENY
            reason = f"Unattended destructive tool '{tool_name}' blocked by agent-action-gate policy."
        elif not is_unattended and tool_name.lower() in self.DESTRUCTIVE_ACTIONS:
            verdict = GateVerdict.REQUIRE_HUMAN_APPROVAL
            reason = f"Destructive tool '{tool_name}' requires human-in-the-loop authorization."
        else:
            verdict = GateVerdict.ALLOW
            reason = "Tool call passes safety gate policy."

        receipt = GateAuditReceipt(
            request_id=f"gate_{len(self.audit_log) + 1:04d}",
            tool_name=tool_name,
            target_node_id=target_node_id,
            verdict=verdict,
            reason=reason,
            timestamp=time.time(),
        )
        self.audit_log.append(receipt)
        return verdict, reason
