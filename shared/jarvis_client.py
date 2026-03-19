"""
Unified Jarvis client — multi-LLM with synthesis.

Async-first, with sync wrapper for legacy callers.

Usage (async):
    from shared.jarvis_client import Jarvis
    jarvis = Jarvis()
    result = await jarvis.ask("What's the play?")
    print(result["synthesis"]["unified_answer"])

Usage (sync):
    from shared.jarvis_client import jarvis_ask
    result = jarvis_ask("What's the play?")
    print(result["synthesis"]["unified_answer"])

Result shape:
    {
        "request_id": "...",
        "models": { "anthropic_claude": { "status": "completed", "response": "..." }, ... },
        "synthesis": {
            "unified_answer": "...",
            "confidence_score": 0.85,
            "consensus_points": ["..."],
            "disagreements": ["..."],
        }
    }
"""

import asyncio
import json
import os
import time
from dataclasses import dataclass, field
from pathlib import Path

import httpx

# Resolve token: env var > jarvis.txt at project root
_PROJECT_ROOT = Path(__file__).resolve().parent.parent

def _load_token() -> str:
    token = os.environ.get("JARVIS_TOKEN")
    if token:
        return token
    txt = _PROJECT_ROOT / "jarvis.txt"
    if txt.exists():
        for line in txt.read_text().splitlines():
            if line.startswith("Auth Token:"):
                return line.split(":", 1)[1].strip()
            # Also try bare token lines (64+ chars, no spaces)
            stripped = line.strip()
            if len(stripped) > 60 and " " not in stripped and stripped.startswith("ey"):
                return stripped
    raise RuntimeError("No Jarvis token found. Set JARVIS_TOKEN env var or check jarvis.txt")

BASE_URL = os.environ.get("JARVIS_URL", "https://nodes.bio/api/jarvis")
DEFAULT_MODELS = ["openai_gpt", "anthropic_claude", "perplexity", "xai_grok"]
POLL_INTERVAL = 2
TIMEOUT = 90


@dataclass
class Jarvis:
    base_url: str = BASE_URL
    token: str = ""
    models: list = field(default_factory=lambda: list(DEFAULT_MODELS))
    timeout: int = TIMEOUT

    def __post_init__(self):
        if not self.token:
            self.token = _load_token()

    def _headers(self):
        return {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}

    async def ask(self, prompt: str, models: list | None = None) -> dict:
        """Submit prompt → poll → synthesize → return everything."""
        models = models or self.models
        async with httpx.AsyncClient(timeout=self.timeout, headers=self._headers()) as client:
            # Submit
            resp = await client.post(
                f"{self.base_url}/generate",
                json={"prompt": prompt, "models": models},
            )
            resp.raise_for_status()
            data = resp.json()
            request_id = data["request_id"]

            # Poll
            t0 = time.monotonic()
            status = data
            while time.monotonic() - t0 < self.timeout:
                await asyncio.sleep(POLL_INTERVAL)
                resp = await client.get(f"{self.base_url}/status/{request_id}")
                if resp.status_code != 200 or not resp.text.strip():
                    continue
                status = resp.json()
                if status.get("status") == "completed":
                    break
            else:
                return {"request_id": request_id, "models": status.get("models", {}), "synthesis": None}

            # Synthesize
            resp = await client.post(f"{self.base_url}/synthesize/{request_id}")
            synthesis = resp.json() if resp.status_code == 200 else None

            return {
                "request_id": request_id,
                "models": status.get("models", {}),
                "synthesis": synthesis,
            }


# ── Sync wrapper ──────────────────────────────────────────────

def jarvis_ask(prompt: str, models: list | None = None, timeout: int = TIMEOUT) -> dict:
    """Blocking wrapper around Jarvis.ask() for legacy callers."""
    j = Jarvis(timeout=timeout)
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        # Already inside an event loop (e.g. Jupyter, Flask) — run in thread
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            return pool.submit(asyncio.run, j.ask(prompt, models)).result()
    return asyncio.run(j.ask(prompt, models))
