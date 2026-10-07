"""Apex_FDE_Matrix: Standard Model Context Protocol (MCP) Tools.

Tool schemas and handler functions exposing the digital twin to frontier agents.
"""

from __future__ import annotations

import json
from typing import Any, Callable, Dict, List

from apex_fde_matrix.actuation.executor import BoundedExecutor
from apex_fde_matrix.actuation.mutation import ActionType, MutationAction, MutationPlan
from apex_fde_matrix.graph.blast_radius import (
    compute_betweenness_centrality,
    compute_blast_radius,
    compute_pagerank,
)
from apex_fde_matrix.graph.model import NodeStatus, ResourceType
from apex_fde_matrix.graph.query_engine import GraphQueryEngine
from apex_fde_matrix.graph.topology import InfrastructureTopology
from apex_fde_matrix.swarm.orchestrator import SRESwarmOrchestrator


class MCPToolRegistry:
    """Registry of tools made available to Claude, GPT-6, Gemini, and Hermes over MCP."""

    def __init__(
        self,
        topology: InfrastructureTopology,
        orchestrator: SRESwarmOrchestrator,
        executor: BoundedExecutor,
    ) -> None:
        self.topology = topology
        self.orchestrator = orchestrator
        self.executor = executor
        self.query_engine = GraphQueryEngine(topology)

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Return MCP tool schemas."""
        return [
            {
                "name": "matrix_query_topology",
                "description": "Query the Causal Infrastructure Knowledge Graph for nodes, dependencies, and health states.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "resource_type": {"type": "string", "description": "Filter by resource type (e.g. bare_metal_node, k8s_pod, bgp_router)"},
                        "status": {"type": "string", "description": "Filter by node status (healthy, degraded, critical)"},
                        "min_criticality": {"type": "number", "description": "Minimum criticality weight (0.0 to 10.0)"},
                        "name_pattern": {"type": "string", "description": "Regex pattern for node name"},
                    },
                },
            },
            {
                "name": "matrix_simulate_blast_radius",
                "description": "Mathematically compute downstream blast radius and affected dependents before executing any change.",
                "inputSchema": {
                    "type": "object",
                    "required": ["target_node_id"],
                    "properties": {
                        "target_node_id": {"type": "string", "description": "Target infrastructure node ID to evaluate"},
                        "attenuation_factor": {"type": "number", "description": "Fault tolerance dampening factor (default 0.85)"},
                    },
                },
            },
            {
                "name": "matrix_diagnose_incident",
                "description": "Trigger multi-agent SRE swarm triage (Claude Opus, GPT-6 Astra, Gemini 4 Argon) and consensus vote.",
                "inputSchema": {
                    "type": "object",
                    "required": ["incident_id", "impacted_node_id", "symptom"],
                    "properties": {
                        "incident_id": {"type": "string", "description": "Unique incident ticket identifier"},
                        "impacted_node_id": {"type": "string", "description": "Anomalous node ID reporting errors"},
                        "symptom": {"type": "string", "description": "Observed symptom or error trace"},
                        "max_acceptable_blast_radius": {"type": "number", "description": "Maximum blast radius threshold before veto"},
                    },
                },
            },
            {
                "name": "matrix_execute_guarded_mutation",
                "description": "Execute a bounded mutation action with automatic compensatory rollback on failure.",
                "inputSchema": {
                    "type": "object",
                    "required": ["action_type", "target_node_id"],
                    "properties": {
                        "action_type": {"type": "string", "description": "Action type (cordon_node, drain_node, uncordon_node, scale_replicas)"},
                        "target_node_id": {"type": "string", "description": "Node ID to mutate"},
                        "parameters": {"type": "object", "description": "Action configuration parameters"},
                        "dry_run": {"type": "boolean", "description": "Simulate mutation without persisting changes"},
                    },
                },
            },
            {
                "name": "matrix_get_health_metrics",
                "description": "Retrieve comprehensive topological metrics, PageRank distribution, and detected single points of failure.",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                },
            },
        ]

    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Dispatch MCP tool execution."""
        if name == "matrix_query_topology":
            rtype = ResourceType(arguments["resource_type"]) if arguments.get("resource_type") else None
            status = NodeStatus(arguments["status"]) if arguments.get("status") else None
            min_crit = arguments.get("min_criticality")
            pattern = arguments.get("name_pattern")
            nodes = self.query_engine.find_nodes(
                resource_type=rtype,
                status=status,
                min_criticality=min_crit,
                name_pattern=pattern,
            )
            return {"count": len(nodes), "nodes": [n.to_dict() for n in nodes]}

        elif name == "matrix_simulate_blast_radius":
            target_id = arguments["target_node_id"]
            attenuation = arguments.get("attenuation_factor", 0.85)
            res = compute_blast_radius(self.topology, target_id, attenuation_factor=attenuation)
            return {
                "target_node_id": res.target_node_id,
                "impact_score": res.impact_score,
                "affected_nodes_count": res.affected_nodes_count,
                "direct_dependents": res.direct_dependents,
                "transitive_dependents": res.transitive_dependents,
                "critical_dependents": res.critical_dependents,
                "calculation_time_ms": res.calculation_time_ms,
            }

        elif name == "matrix_diagnose_incident":
            incident_id = arguments["incident_id"]
            impacted_node = arguments["impacted_node_id"]
            symptom = arguments["symptom"]
            max_blast = arguments.get("max_acceptable_blast_radius", 25.0)
            return self.orchestrator.handle_incident(
                incident_id=incident_id,
                impacted_node_id=impacted_node,
                symptom_description=symptom,
                max_acceptable_blast_radius=max_blast,
            )

        elif name == "matrix_execute_guarded_mutation":
            action_type = ActionType(arguments["action_type"])
            target_id = arguments["target_node_id"]
            params = arguments.get("parameters", {})
            dry_run = arguments.get("dry_run", False)

            action = MutationAction(
                action_id=f"mcp_act_{target_id}_{action_type.value}",
                action_type=action_type,
                target_node_id=target_id,
                parameters=params,
            )
            plan = MutationPlan(
                plan_id=f"mcp_plan_{target_id}",
                actions=[action],
                max_blast_radius=50.0,
                description=f"MCP-initiated guarded mutation on {target_id}",
            )
            res = self.executor.execute_plan(plan, dry_run=dry_run)
            return {
                "plan_id": res.plan_id,
                "success": res.success,
                "executed_action_ids": res.executed_action_ids,
                "rolled_back": res.rolled_back,
                "rollback_action_ids": res.rollback_action_ids,
                "elapsed_ms": res.elapsed_ms,
            }

        elif name == "matrix_get_health_metrics":
            pagerank = compute_pagerank(self.topology)
            spofs = compute_betweenness_centrality(self.topology)
            top_spofs = sorted(spofs.items(), key=lambda x: x[1], reverse=True)[:5]
            return {
                "total_nodes": self.topology.node_count,
                "total_edges": self.topology.edge_count,
                "top_pagerank_nodes": sorted(pagerank.items(), key=lambda x: x[1], reverse=True)[:5],
                "top_betweenness_spofs": top_spofs,
            }

        raise ValueError(f"Unknown MCP tool '{name}'.")
