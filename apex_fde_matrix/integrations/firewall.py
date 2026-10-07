"""Apex_FDE_Matrix: agent-jailbreak-firewall Modular Integration.

Semantic tripwire scanning incoming prompts, tool calls, and mutation parameters
for malicious injections, escape sequences, and privilege escalation attempts.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Tuple


class FirewallIntegration:
    """Interceptors connecting to agent-jailbreak-firewall."""

    SUSPICIOUS_PATTERNS = [
        re.compile(r"(?i)\bignore\s+(all\s+)?previous\s+instructions\b"),
        re.compile(r"(?i)\bsystem\s+prompt\s+override\b"),
        re.compile(r"(?i)\brm\s+-rf\s+/"),
        re.compile(r"(?i)\bdd\s+if=/dev/zero"),
        re.compile(r"(?i)\bchmod\s+777\s+/"),
        re.compile(r"(?i)\biptables\s+-F\b"),
        re.compile(r"(?i)\bdisable_firewall\b"),
    ]

    @classmethod
    def sanitize_input(cls, text: str) -> Tuple[bool, str]:
        """Scan input string. Returns (is_clean, reason)."""
        for pat in cls.SUSPICIOUS_PATTERNS:
            if pat.search(text):
                return False, f"Flagged by firewall rule: {pat.pattern}"
        return True, "clean"

    @classmethod
    def inspect_parameters(cls, params: Dict[str, Any]) -> Tuple[bool, str]:
        """Deep scan dictionary parameters."""
        for k, v in params.items():
            if isinstance(v, str):
                clean, reason = cls.sanitize_input(v)
                if not clean:
                    return False, f"Parameter '{k}' rejected: {reason}"
        return True, "clean"
