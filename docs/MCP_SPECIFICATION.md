# Apex_FDE_Matrix: Model Context Protocol (MCP) Tool Specification

*Version: 2024-11-05 Protocol Compliant — JSON-RPC 2.0*

---

## Tool 1: `matrix_query_topology`
Queries the Causal Infrastructure Knowledge Graph for structural nodes, current metrics, and status.

### Input Schema
```json
{
  "type": "object",
  "properties": {
    "resource_type": {
      "type": "string",
      "description": "Filter by resource type (bare_metal_node, gpu_device, k8s_pod, k8s_service, bgp_router, ebpf_socket_probe)"
    },
    "status": {
      "type": "string",
      "description": "Filter by operational status (healthy, degraded, critical, isolated)"
    },
    "min_criticality": {
      "type": "number",
      "description": "Minimum criticality weight (0.0 to 10.0)"
    },
    "name_pattern": {
      "type": "string",
      "description": "Regex pattern matched against resource name"
    }
  }
}
```

---

## Tool 2: `matrix_simulate_blast_radius`
Mathematically computes the downstream failure reachability and impact score for a potential mutation target.

### Input Schema
```json
{
  "type": "object",
  "required": ["target_node_id"],
  "properties": {
    "target_node_id": {
      "type": "string",
      "description": "Unique identifier of target infrastructure node"
    },
    "attenuation_factor": {
      "type": "number",
      "description": "Fault tolerance attenuation factor (default: 0.85)"
    }
  }
}
```

---

## Tool 3: `matrix_diagnose_incident`
Dispatches an active incident trace to the frontier SRE swarm (Claude Opus 5.5, GPT-6 Astra, Gemini 4 Argon) and collects a quorum consensus vote.

### Input Schema
```json
{
  "type": "object",
  "required": ["incident_id", "impacted_node_id", "symptom"],
  "properties": {
    "incident_id": {
      "type": "string",
      "description": "Incident ticket ID (e.g. INC-4091)"
    },
    "impacted_node_id": {
      "type": "string",
      "description": "Degraded node reporting telemetry anomaly"
    },
    "symptom": {
      "type": "string",
      "description": "Error trace or observed symptom description"
    },
    "max_acceptable_blast_radius": {
      "type": "number",
      "description": "Maximum blast radius threshold before Strategic Architect exercises veto"
    }
  }
}
```

---

## Tool 4: `matrix_execute_guarded_mutation`
Executes an atomic infrastructure mutation with automatic compensatory rollback on error.

### Input Schema
```json
{
  "type": "object",
  "required": ["action_type", "target_node_id"],
  "properties": {
    "action_type": {
      "type": "string",
      "description": "Action primitive: cordon_node, drain_node, uncordon_node, scale_replicas, attach_ebpf_probe, pivot_bgp_route"
    },
    "target_node_id": {
      "type": "string",
      "description": "Target node ID to mutate"
    },
    "parameters": {
      "type": "object",
      "description": "Action specific parameter dictionary"
    },
    "dry_run": {
      "type": "boolean",
      "description": "Simulate mutation without persisting state changes"
    }
  }
}
```

---

## Tool 5: `matrix_get_health_metrics`
Returns global topology health, PageRank distribution, and detected single points of failure (SPOFs).
