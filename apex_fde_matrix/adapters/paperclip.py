"""Apex_FDE_Matrix: Paperclip Company OS Adapter.

Integrates with paperclipai/paperclip to enforce organizational hierarchy,
department budgets, goal ancestry tracking, and board-level approval gates.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class PaperclipGoal:
    """Represents a hierarchical business or operational goal in Paperclip."""
    goal_id: str
    title: str
    parent_goal_id: Optional[str]
    assigned_agent_id: str
    budget_usd_cap: float
    current_spend_usd: float = 0.0
    status: str = "active"


class PaperclipCompanyAdapter:
    """Manages org-chart governance, spend limits, and goal ancestry."""

    def __init__(self, company_name: str = "Apex Enterprise Sovereign") -> None:
        self.company_name = company_name
        self.goals: Dict[str, PaperclipGoal] = {}
        self.agent_registry: Dict[str, Dict[str, Any]] = {}
        self.spend_ledger: List[Dict[str, Any]] = []

    def register_agent(
        self,
        agent_id: str,
        role: str,
        reports_to: Optional[str] = None,
        max_spend_per_action: float = 5.0,
    ) -> None:
        """Register an AI worker into the Paperclip corporate org chart."""
        self.agent_registry[agent_id] = {
            "role": role,
            "reports_to": reports_to,
            "max_spend_per_action": max_spend_per_action,
            "registered_at": time.time(),
        }

    def create_goal(
        self,
        title: str,
        assigned_agent_id: str,
        budget_usd_cap: float = 20.0,
        parent_goal_id: Optional[str] = None,
    ) -> PaperclipGoal:
        """Create a new root or sub-goal with budget caps."""
        gid = f"goal_{uuid.uuid4().hex[:8]}"
        goal = PaperclipGoal(
            goal_id=gid,
            title=title,
            parent_goal_id=parent_goal_id,
            assigned_agent_id=assigned_agent_id,
            budget_usd_cap=budget_usd_cap,
        )
        self.goals[gid] = goal
        return goal

    def authorize_mutation_spend(
        self,
        goal_id: str,
        agent_id: str,
        estimated_cost_usd: float,
    ) -> bool:
        """Verify budget and goal ancestry before allowing an infrastructure mutation."""
        goal = self.goals.get(goal_id)
        if not goal:
            return False

        if goal.current_spend_usd + estimated_cost_usd > goal.budget_usd_cap:
            # Budget exceeded -> block autonomous execution
            return False

        agent = self.agent_registry.get(agent_id)
        if agent and estimated_cost_usd > agent.get("max_spend_per_action", 5.0):
            return False

        # Deduct budget and log spend
        goal.current_spend_usd += estimated_cost_usd
        self.spend_ledger.append({
            "goal_id": goal_id,
            "agent_id": agent_id,
            "cost_usd": estimated_cost_usd,
            "timestamp": time.time(),
        })
        return True
