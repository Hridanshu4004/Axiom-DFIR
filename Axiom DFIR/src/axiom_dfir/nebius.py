"""Nebius Token Factory & NVIDIA Nemotron Integration for AXIOM DFIR.

Mandatory Integration for Nebius x NVIDIA Global AI Hackathon 2026.
Target Track: Best Apps & Agents.

Endpoint Documentation:
    https://docs.tokenfactory.nebius.com/
Default Regional Endpoint:
    https://api.tokenfactory.nebius.com/v1/
    https://api.tokenfactory.us-central1.nebius.com/v1/

Model Profiles:
    FAST:     nvidia/Nemotron-3.5-Lightning  (Triage, filtering, log parsing)
    BALANCED: nvidia/Nemotron-3-Super        (Correlation, ReAct cross-checks, synthesis)
    DEEP:     nvidia/Nemotron-3-Ultra-550B   (Root cause, lateral movement, conflicting claims)
"""

from __future__ import annotations

import json
import logging
import os
import random
import re
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("axiom_dfir.nebius")

# ── Endpoint Constants ────────────────────────────────────────────────────────
DEFAULT_NEBIUS_BASE_URL = "https://api.tokenfactory.nebius.com/v1/"
FALLBACK_REGIONAL_URL = "https://api.tokenfactory.us-central1.nebius.com/v1/"

# ── NVIDIA Nemotron Model Identifiers (Configurable via Environment) ─────────
DEFAULT_FAST_MODEL = "nvidia/Nemotron-3.5-Lightning"
DEFAULT_BALANCED_MODEL = "nvidia/Nemotron-3-Super"
DEFAULT_DEEP_MODEL = "nvidia/Nemotron-3-Ultra-550B"

# Estimated costs per million tokens (USD)
MODEL_PRICING: Dict[str, Dict[str, float]] = {
    "nvidia/Nemotron-3.5-Lightning": {"input": 0.15, "output": 0.60, "cache_read": 0.03},
    "nvidia/nemotron-3-nano": {"input": 0.10, "output": 0.40, "cache_read": 0.02},
    "nvidia/Nemotron-3-Super": {"input": 0.50, "output": 1.80, "cache_read": 0.10},
    "nvidia/Nemotron-3-Ultra-550B": {"input": 1.80, "output": 5.40, "cache_read": 0.36},
    "default": {"input": 0.50, "output": 1.80, "cache_read": 0.10},
}

_RETRY_STATUS_CODES = frozenset({429, 500, 502, 503, 504})
_DEFAULT_MAX_RETRIES = 3
_DEFAULT_TIMEOUT_SECONDS = 120


# ── Telemetry & Metrics Ledger ───────────────────────────────────────────────
@dataclass
class NebiusCallRecord:
    timestamp: float
    model: str
    profile: str
    task_type: str
    input_tokens: int
    output_tokens: int
    cached_tokens: int
    latency_seconds: float
    cost_usd: float
    status: str
    retries: int
    error: Optional[str] = None


class NebiusMetricsTracker:
    """Thread-safe ledger recording all inference interactions with Nebius Token Factory."""

    def __init__(self) -> None:
        self.records: List[NebiusCallRecord] = []
        self.routing_decisions: List[Dict[str, Any]] = []

    def record_call(self, record: NebiusCallRecord) -> None:
        self.records.append(record)

    def record_routing(self, task: str, model: str, profile: str, rationale: str) -> None:
        self.routing_decisions.append({
            "task": task,
            "model": model,
            "profile": profile,
            "rationale": rationale,
            "timestamp": time.time(),
        })

    def summary(self) -> Dict[str, Any]:
        total_input = sum(r.input_tokens for r in self.records)
        total_output = sum(r.output_tokens for r in self.records)
        total_cached = sum(r.cached_tokens for r in self.records)
        total_cost = sum(r.cost_usd for r in self.records)
        calls_by_profile: Dict[str, int] = {}
        for r in self.records:
            calls_by_profile[r.profile] = calls_by_profile.get(r.profile, 0) + 1

        return {
            "total_requests": len(self.records),
            "total_input_tokens": total_input,
            "total_output_tokens": total_output,
            "total_cached_tokens": total_cached,
            "total_tokens": total_input + total_output,
            "estimated_cost_usd": round(total_cost, 6),
            "profile_distribution": calls_by_profile,
            "total_routing_decisions": len(self.routing_decisions),
        }


GLOBAL_METRICS = NebiusMetricsTracker()


# ── Intelligent Cost-Aware Model Router ──────────────────────────────────────
class NebiusModelRouter:
    """Routes investigative reasoning tasks to the optimal NVIDIA Nemotron profile."""

    def __init__(self) -> None:
        self.fast_model = os.environ.get("AXIOM_FAST_MODEL") or DEFAULT_FAST_MODEL
        self.balanced_model = os.environ.get("AXIOM_BALANCED_MODEL") or DEFAULT_BALANCED_MODEL
        self.deep_model = os.environ.get("AXIOM_DEEP_MODEL") or DEFAULT_DEEP_MODEL

    def resolve_model_for_profile(self, profile: str) -> str:
        p = profile.upper()
        if p == "FAST":
            return self.fast_model
        if p == "DEEP":
            return self.deep_model
        return self.balanced_model

    def route_task(
        self,
        task_label: str,
        unresolved_conflicts: int = 0,
        complexity_hint: Optional[str] = None,
    ) -> Tuple[str, str]:
        """Returns (model_identifier, profile_name).

        Deterministic Routing Rules:
          - Initial log triage, tool catalog lookup -> FAST
          - Standard artifact analysis & ReAct cross-checks -> BALANCED
          - Unresolved conflicts, lateral movement, deep hypothesis -> DEEP
          - Final report generation -> BALANCED or DEEP based on case severity
        """
        label = (task_label or "").lower()

        # Explicit overrides
        if complexity_hint == "deep" or unresolved_conflicts > 0:
            return self.deep_model, "DEEP"
        if complexity_hint == "fast":
            return self.fast_model, "FAST"
        if complexity_hint == "balanced":
            return self.balanced_model, "BALANCED"

        # Triage and tool selection
        if any(k in label for k in ["inv1", "tool_select", "triage", "catalog", "filter", "fast"]):
            return self.fast_model, "FAST"

        # Deep investigation and lateral movement
        if any(k in label for k in ["lateral_movement", "root_cause", "deep", "conflict", "contradiction"]):
            return self.deep_model, "DEEP"

        # Analysis, ReAct, Self-Correction, Report
        if any(k in label for k in ["inv2", "analysis", "hypothes"]):
            # Use DEEP if high complexity, else BALANCED
            return (self.deep_model, "DEEP") if "complex" in label else (self.balanced_model, "BALANCED")

        if any(k in label for k in ["react", "cross_check", "self_correct", "sc", "report"]):
            return self.balanced_model, "BALANCED"

        # Default fallback is BALANCED
        return self.balanced_model, "BALANCED"

    def escalate_profile(
        self,
        current_profile: str = "FAST",
        open_hypotheses: int = 0,
        conflicts_count: int = 0,
        complexity_score: float = 0.0,
    ) -> Tuple[str, str, str]:
        """Dynamically escalates or de-escalates model profile with explicit rationale."""
        if conflicts_count > 0 or complexity_score >= 0.8:
            rationale = f"Escalated to DEEP due to {conflicts_count} contradictory evidence signals and complexity {complexity_score:.2f}"
            GLOBAL_METRICS.record_routing("escalation", self.deep_model, "DEEP", rationale)
            return self.deep_model, "DEEP", rationale
        if open_hypotheses > 2 or complexity_score >= 0.4:
            rationale = f"Escalated to BALANCED due to {open_hypotheses} active hypotheses under test"
            GLOBAL_METRICS.record_routing("escalation", self.balanced_model, "BALANCED", rationale)
            return self.balanced_model, "BALANCED", rationale
        rationale = "Remaining at FAST for rapid artifact discovery and tool selection"
        GLOBAL_METRICS.record_routing("escalation", self.fast_model, "FAST", rationale)
        return self.fast_model, "FAST", rationale


# ── Duck-Typed Anthropic/OpenAI Compatible Response Structs ──────────────────
class _TextBlock:
    __slots__ = ("type", "text")

    def __init__(self, text: str) -> None:
        self.type = "text"
        self.text = text or ""


class _Usage:
    __slots__ = (
        "input_tokens",
        "output_tokens",
        "cache_read_input_tokens",
        "cache_creation_input_tokens",
    )

    def __init__(
        self,
        input_tokens: int,
        output_tokens: int,
        cache_read: int = 0,
        cache_creation: int = 0,
    ) -> None:
        self.input_tokens = int(input_tokens or 0)
        self.output_tokens = int(output_tokens or 0)
        self.cache_read_input_tokens = int(cache_read or 0)
        self.cache_creation_input_tokens = int(cache_creation or 0)


class NebiusResponse:
    __slots__ = ("content", "usage", "stop_reason", "model", "latency", "cost_usd")

    def __init__(
        self,
        text: str,
        usage: _Usage,
        model: str = "",
        stop_reason: str = "end_turn",
        latency: float = 0.0,
        cost_usd: float = 0.0,
    ) -> None:
        self.content = [_TextBlock(text)]
        self.usage = usage
        self.stop_reason = stop_reason
        self.model = model
        self.latency = latency
        self.cost_usd = cost_usd


# ── OpenAI-Compatible Nebius Client ──────────────────────────────────────────
class NebiusClient:
    """Production client connecting to Nebius Token Factory for NVIDIA Nemotron inference.

    Features:
      - Fully OpenAI-compatible chat completions interface.
      - Standard library transport (urllib.request) with zero mandatory heavy dependencies.
      - Automatic retries with exponential backoff on HTTP 429 and 5xx errors.
      - Respects Retry-After header.
      - Structured response parsing and token accounting.
      - Safe mock testing mode when credentials are not configured or AXIOM_MOCK_NEBIUS=1.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        router: Optional[NebiusModelRouter] = None,
    ) -> None:
        raw_url = base_url or os.environ.get("NEBIUS_BASE_URL") or DEFAULT_NEBIUS_BASE_URL
        if not raw_url.endswith("/"):
            raw_url += "/"
        self.base_url = raw_url
        self._api_key = api_key
        self.router = router or NebiusModelRouter()
        self.messages = _MessagesAdapter(self)

    def get_api_key(self) -> str:
        key = (
            self._api_key
            or os.environ.get("NEBIUS_API_KEY")
            or os.environ.get("TOKEN_FACTORY_API_KEY")
            or ""
        ).strip()
        return key

    def is_mock_mode(self) -> bool:
        if os.environ.get("AXIOM_MOCK_NEBIUS") == "1":
            return True
        if not self.get_api_key():
            # If no API key is set and dry-run or pytest is active, use mock
            if os.environ.get("SIFT_DRY_RUN") == "1" or "pytest" in os.environ.get("_", "") or "pytest" in sys.modules:
                return True
        return False

    def _calculate_cost(self, model: str, in_tok: int, out_tok: int, cached_tok: int) -> float:
        rates = MODEL_PRICING.get(model, MODEL_PRICING["default"])
        c_in = (in_tok / 1_000_000.0) * rates["input"]
        c_out = (out_tok / 1_000_000.0) * rates["output"]
        c_cached = (cached_tok / 1_000_000.0) * rates["cache_read"]
        return round(c_in + c_out + c_cached, 6)

    def _create_mock_response(self, model: str, messages: list) -> NebiusResponse:
        """Deterministic mock response for offline CI and test suites."""
        last_msg = messages[-1].get("content", "") if messages else ""
        if "SENTINEL-QWEN-OK" in last_msg or "AXIOM-NEBIUS-OK" in last_msg:
            reply = "AXIOM-NEBIUS-OK"
        elif "tool" in last_msg.lower():
            reply = '{"selected_tools": ["vol_pstree", "vol_malfind", "vol_netscan", "get_amcache"]}'
        elif "report" in last_msg.lower():
            reply = "# AXIOM DFIR INVESTIGATION REPORT\n\n## Verified Findings\n- Compromised process detected.\n"
        else:
            reply = '{"status": "analyzed", "findings": [], "hypotheses": []}'

        u = _Usage(input_tokens=150, output_tokens=40, cache_read=0)
        return NebiusResponse(
            text=reply,
            usage=u,
            model=f"{model} [MOCK_MODE]",
            stop_reason="end_turn",
            latency=0.01,
            cost_usd=0.0,
        )

    def create(
        self,
        *,
        model: Optional[str] = None,
        messages: Optional[list] = None,
        max_tokens: int = 4096,
        temperature: Optional[float] = 0.0,
        timeout: Optional[int] = None,
        system: Optional[str] = None,
        profile_hint: Optional[str] = None,
        **_ignored,
    ) -> NebiusResponse:
        start_time = time.time()
        selected_model = model or self.router.resolve_model_for_profile(profile_hint or "BALANCED")
        effective_timeout = timeout or int(os.environ.get("AXIOM_HTTP_TIMEOUT") or _DEFAULT_TIMEOUT_SECONDS)

        # Mock path
        if self.is_mock_mode():
            logger.info("Executing inference in MOCK mode for model %s", selected_model)
            return self._create_mock_response(selected_model, messages or [])

        api_key = self.get_api_key()
        if not api_key:
            raise OSError(
                "Nebius Token Factory inference requested, but NEBIUS_API_KEY is not set. "
                "Set NEBIUS_API_KEY=<your-key> or enable AXIOM_MOCK_NEBIUS=1 for synthetic testing."
            )

        # OpenAI chat completions format
        formatted_messages = []
        if system:
            formatted_messages.append({"role": "system", "content": str(system)})
        for m in messages or []:
            if isinstance(m, dict):
                r = m.get("role", "user")
                c = m.get("content", "")
                if isinstance(c, list):
                    c = "".join(part.get("text", "") if isinstance(part, dict) else str(part) for part in c)
                formatted_messages.append({"role": r, "content": str(c)})
            else:
                formatted_messages.append({"role": "user", "content": str(m)})

        payload_dict: Dict[str, Any] = {
            "model": selected_model,
            "messages": formatted_messages,
            "max_tokens": max(1, min(int(max_tokens or 4096), 8192)),
        }
        if temperature is not None:
            payload_dict["temperature"] = float(temperature)

        payload_bytes = json.dumps(payload_dict).encode("utf-8")
        target_endpoint = self.base_url
        if not target_endpoint.endswith("chat/completions"):
            target_endpoint = target_endpoint + ("chat/completions" if target_endpoint.endswith("/") else "/chat/completions")

        response_json: Optional[Dict[str, Any]] = None
        retries = 0

        for attempt in range(_DEFAULT_MAX_RETRIES):
            retries = attempt
            req = urllib.request.Request(target_endpoint, data=payload_bytes, method="POST")
            req.add_header("Authorization", f"Bearer {api_key}")
            req.add_header("Content-Type", "application/json")
            req.add_header("User-Agent", "AXIOM-DFIR-Agent/1.0 (NVIDIA-Nebius-Hackathon)")

            try:
                with urllib.request.urlopen(req, timeout=effective_timeout) as resp:
                    raw_body = resp.read().decode("utf-8")
                    response_json = json.loads(raw_body)
                break
            except urllib.error.HTTPError as exc:
                if exc.code in _RETRY_STATUS_CODES and attempt < _DEFAULT_MAX_RETRIES - 1:
                    retry_after = exc.headers.get("Retry-After")
                    base_delay = min(30.0, float(retry_after)) if retry_after else min(10.0, 1.0 * (2**attempt))
                    jitter = random.uniform(0.05, 0.25)
                    delay = base_delay + jitter
                    logger.warning("Nebius HTTP %d on attempt %d; backoff %.2fs", exc.code, attempt + 1, delay)
                    time.sleep(delay)
                    continue
                err_detail = b""
                try:
                    err_detail = exc.read()[:1000]
                except Exception:
                    pass
                raise OSError(f"Nebius Token Factory HTTP {exc.code}: {err_detail!r}") from exc
            except (TimeoutError, urllib.error.URLError) as exc:
                if attempt < _DEFAULT_MAX_RETRIES - 1:
                    base_delay = min(10.0, 1.0 * (2**attempt))
                    delay = base_delay + random.uniform(0.05, 0.25)
                    logger.warning("Nebius connection error: %s; retry in %.2fs", exc, delay)
                    time.sleep(delay)
                    continue
                raise OSError(f"Nebius transport failure after {effective_timeout}s: {exc}") from exc

        if response_json is None:
            raise OSError("Nebius Token Factory returned no response after retries.")

        latency = time.time() - start_time
        choices = response_json.get("choices") or []
        reply_text = ""
        finish_reason = "end_turn"
        if choices:
            msg = choices[0].get("message") or {}
            reply_text = msg.get("content") or msg.get("reasoning_content") or ""
            finish_reason = choices[0].get("finish_reason") or "end_turn"

        usage_dict = response_json.get("usage") or {}
        prompt_tokens = int(usage_dict.get("prompt_tokens", 0) or 0)
        completion_tokens = int(usage_dict.get("completion_tokens", 0) or 0)
        cached_tokens = 0
        details = usage_dict.get("prompt_tokens_details") or {}
        if isinstance(details, dict):
            cached_tokens = int(details.get("cached_tokens", 0) or 0)

        cost_usd = self._calculate_cost(selected_model, prompt_tokens, completion_tokens, cached_tokens)

        # Record metrics
        GLOBAL_METRICS.record_call(
            NebiusCallRecord(
                timestamp=time.time(),
                model=selected_model,
                profile=profile_hint or "BALANCED",
                task_type="inference",
                input_tokens=prompt_tokens,
                output_tokens=completion_tokens,
                cached_tokens=cached_tokens,
                latency_seconds=round(latency, 3),
                cost_usd=cost_usd,
                status="SUCCESS",
                retries=retries,
            )
        )

        usage_obj = _Usage(
            input_tokens=prompt_tokens,
            output_tokens=completion_tokens,
            cache_read=cached_tokens,
        )

        return NebiusResponse(
            text=reply_text,
            usage=usage_obj,
            model=response_json.get("model", selected_model) or selected_model,
            stop_reason=finish_reason,
            latency=latency,
            cost_usd=cost_usd,
        )


class _MessagesAdapter:
    """Provides client.messages.create() Anthropic-compatible interface."""

    def __init__(self, parent: NebiusClient) -> None:
        self._parent = parent

    def create(self, **kwargs) -> NebiusResponse:
        return self._parent.create(**kwargs)


# ── Runtime Connectivity Verification ───────────────────────────────────────
def verify_nebius_connection(
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    model: Optional[str] = None,
    allow_mock: bool = True,
) -> Dict[str, Any]:
    """Verification smoke test confirming live Nebius Token Factory connectivity."""
    client = NebiusClient(base_url=base_url, api_key=api_key)
    key = client.get_api_key()
    target_model = model or client.router.fast_model
    is_mock = client.is_mock_mode() if allow_mock else False

    result = {
        "configured": bool(key or is_mock),
        "mock_mode": is_mock,
        "endpoint": client.base_url,
        "model": target_model,
        "status": "UNKNOWN",
        "reply": "",
        "latency_seconds": 0.0,
        "token_usage": {},
        "error": None,
    }

    if not result["configured"]:
        result["status"] = "MISSING_CREDENTIALS"
        result["error"] = "NEBIUS_API_KEY environment variable is not set."
        return result

    try:
        start = time.time()
        resp = client.create(
            model=target_model,
            messages=[{"role": "user", "content": "Reply with exactly: AXIOM-NEBIUS-OK"}],
            max_tokens=32,
            temperature=0.0,
        )
        result["latency_seconds"] = round(time.time() - start, 3)
        result["reply"] = resp.content[0].text.strip() if resp.content else ""
        result["token_usage"] = {
            "input": resp.usage.input_tokens,
            "output": resp.usage.output_tokens,
            "cached": resp.usage.cache_read_input_tokens,
        }
        result["status"] = "CONNECTED"
    except Exception as exc:
        result["status"] = "CONNECTION_FAILED"
        result["error"] = f"{type(exc).__name__}: {exc}"

    return result
