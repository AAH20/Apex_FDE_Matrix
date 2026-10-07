"""Apex_FDE_Matrix: NVIDIA NIM & Open-Weight Inference Client.

Pure Python standard library client for NVIDIA Inference Microservices (NIM)
and open-weight model endpoints (Hermes 3, Nemotron 70B, DeepSeek R1).
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional


class NvidiaNIMClient:
    """Standard OpenAI-compatible client for NVIDIA NIM microservices."""

    def __init__(
        self,
        base_url: str = "http://localhost:8000/v1",
        api_key: Optional[str] = None,
        default_model: str = "nvidia/llama-3.1-nemotron-70b",
        mock_mode: bool = False,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or "EMPTY"
        self.default_model = default_model
        self.mock_mode = mock_mode

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> Dict[str, Any]:
        """Execute chat completion against NIM endpoint."""
        target_model = model or self.default_model

        if self.mock_mode:
            return {
                "id": "mock_nim_chat_01",
                "model": target_model,
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": (
                                f"[NVIDIA NIM ({target_model})]: Analyzed system state. "
                                "Verification confirmed. Proceeding with bounded remediation."
                            ),
                        },
                        "finish_reason": "stop",
                    }
                ],
                "usage": {"prompt_tokens": 120, "completion_tokens": 35, "total_tokens": 155},
            }

        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": target_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        data = json.dumps(payload).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                resp_data = resp.read().decode("utf-8")
                return json.loads(resp_data)
        except urllib.error.URLError as err:
            return {
                "error": True,
                "message": f"NIM endpoint unreachable at {url}: {str(err)}",
            }
