"""Apex_FDE_Matrix: apex-zero-loop Modular Integration.

Formal verification of cycle-breaking and loop prevention in multi-agent SRE workflows.
"""

from __future__ import annotations

from typing import List, Tuple

from apex_fde_matrix.graph.topology import InfrastructureTopology


class ZeroLoopIntegration:
    """Verifies that infrastructure changes do not introduce circular deadlocks or infinite healing loops."""

    @classmethod
    def verify_no_cycles(cls, topology: InfrastructureTopology) -> Tuple[bool, List[List[str]]]:
        """Detect strongly connected components (cycles) in the topology graph."""
        cycles = topology.detect_cycles()
        if cycles:
            return False, cycles
        return True, []

    @classmethod
    def verify_action_acyclic(
        cls,
        topology: InfrastructureTopology,
        source_id: str,
        target_id: str,
    ) -> bool:
        """Check if adding a dependency edge from source to target would create a cycle.

        Adding source -> target creates a cycle if target can already reach source.
        """
        path = topology.find_shortest_path(target_id, source_id)
        return path is None
