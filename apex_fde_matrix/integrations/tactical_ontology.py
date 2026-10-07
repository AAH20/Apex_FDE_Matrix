"""Apex_FDE_Matrix: autonomous-tactical-ontology Modular Integration.

Bridges the digital twin to Palantir Foundry & Gotham Open-Ontology JSON-LD formats,
eliminating manual defense FDE entity mapping bottlenecks.
"""

from __future__ import annotations

import json
import time
from typing import Any, Dict, List

from apex_fde_matrix.graph.topology import InfrastructureTopology


class TacticalOntologyIntegration:
    """Exports digital twin topologies into Palantir Open-Ontology JSON-LD specifications."""

    @classmethod
    def export_palantir_open_ontology(
        cls,
        topology: InfrastructureTopology,
        ontology_rid: str = "ri.ontology.main.ontology.apex-fde-tactical",
    ) -> Dict[str, Any]:
        """Convert in-memory digital twin into Palantir Gotham/Foundry Open-Ontology format."""
        entities: List[Dict[str, Any]] = []
        links: List[Dict[str, Any]] = []

        for node in topology.get_nodes():
            entity = {
                "@id": f"urn:palantir:objectType:{node.resource_type.value}:{node.id}",
                "@type": f"palantir:{node.resource_type.value.capitalize()}",
                "primaryKey": node.id,
                "title": node.name,
                "properties": {
                    "status": node.status.value,
                    "criticality": node.criticality_weight,
                    "metadata": node.metadata,
                    "metrics": node.metrics,
                },
            }
            entities.append(entity)

        # Map edges to Palantir link types
        for node in topology.get_nodes():
            for edge in topology.get_outbound_edges(node.id):
                link = {
                    "@id": f"urn:palantir:linkType:{edge.edge_type.value}:{edge.source_id}->{edge.target_id}",
                    "@type": f"palantir:Link:{edge.edge_type.value.upper()}",
                    "source": f"urn:palantir:objectType:{node.resource_type.value}:{edge.source_id}",
                    "target": f"urn:palantir:objectType:{topology.get_node(edge.target_id).resource_type.value}:{edge.target_id}",  # type: ignore
                    "properties": {
                        "latency_ms": edge.latency_ms,
                        "bandwidth_gbps": edge.bandwidth_gbps,
                    },
                }
                links.append(link)

        return {
            "@context": {
                "palantir": "https://palantir.com/ontologies/v1/",
                "apex": "https://a2zsoc.com/ontologies/fde/v1/",
            },
            "ontologyRid": ontology_rid,
            "generatedAt": time.time(),
            "entityCount": len(entities),
            "linkCount": len(links),
            "entities": entities,
            "links": links,
        }
