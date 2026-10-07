# Forward Deployed Engineer Field Manual: Air-Gapped Enterprise Deployment

*Operational Runbook for Deploying Apex_FDE_Matrix in Fortune 500 & Sovereign Defense Enclaves*

---

## 1. Landing in the Client Environment

When arriving on-site as an FDE at a bank, hyperscaler, or defense contractor, you are typically granted access to a bastion jump-host with zero external internet connectivity.

### Why Zero-Dependency Matters
Most agentic frameworks fail instantly because they require downloading hundreds of megabytes of Python wheels (`pip install ...`), which is blocked by enterprise proxy firewalls.

`Apex_FDE_Matrix` is **100% pure Python 3.10+ standard library**:
```bash
# Clone or scp the single repository folder
cd /opt/enterprise/apex_fde_matrix

# Verify installation with zero external dependencies
python3 -m unittest discover -s tests -p "test_*.py"
```

---

## 2. Ingesting Enterprise Assets into the Digital Twin

Connect your infrastructure collectors to populate the graph:

```python
from apex_fde_matrix import InfrastructureTopology
from apex_fde_matrix.adapters.baremetal import BareMetalGPUAdapter
from apex_fde_matrix.adapters.kubernetes import KubernetesTopologyAdapter

# 1. Initialize sovereign digital twin
topo = InfrastructureTopology()

# 2. Ingest bare-metal GPU clusters
BareMetalGPUAdapter.ingest_gpu_cluster(
    topo,
    cluster_name="h100_core",
    node_count=16,
    gpus_per_node=8,
)

# 3. Map Kubernetes service tiers
KubernetesTopologyAdapter.ingest_service_stack(
    topo,
    namespace="production",
    service_name="quant_matching_engine",
    replica_count=8,
    host_node_id="bm_node_h100_core_01",
)
```

---

## 3. Connecting to the Sovereign Stack

### Integrating Paperclip (Company OS)
Paperclip establishes your reporting chain and protects your token/dollar budget:
```python
from apex_fde_matrix.adapters.paperclip import PaperclipCompanyAdapter

paperclip = PaperclipCompanyAdapter("Enterprise Sovereign")
paperclip.register_agent("hermes_sre", role="Forward Deployed SRE", max_spend_per_action=10.0)
goal = paperclip.create_goal(
    title="Ensure 99.999% Service Availability",
    assigned_agent_id="hermes_sre",
    budget_usd_cap=100.0,
)
```

### Integrating Hermes & NVIDIA NIM
Deploy persistent SRE agents using on-premise model weights:
```python
from apex_fde_matrix.adapters.hermes import HermesAgentAdapter
from apex_fde_matrix.adapters.nim import NvidiaNIMClient

hermes = HermesAgentAdapter("hermes_sre")
hermes.register_matrix_skills()

# Point to internal DGX cluster hosting Nemotron or Hermes 3
nim = NvidiaNIMClient(
    base_url="http://10.200.0.50:8000/v1",
    default_model="nvidia/llama-3.1-nemotron-70b",
)
```

---

## 4. Serving via Model Context Protocol (MCP)

To allow IDEs, Claude Desktop, or external agent orchestrators to query your digital twin:
```bash
python3 -m apex_fde_matrix mcp
```
Configure your client's `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "apex_fde_matrix": {
      "command": "python3",
      "args": ["-m", "apex_fde_matrix", "mcp"]
    }
  }
}
```
