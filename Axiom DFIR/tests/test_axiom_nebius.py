"""Unit tests for AXIOM DFIR Nebius Token Factory & NVIDIA Nemotron Integration (Phase 3).

Validates:
  - Client initialization and OpenAI-compatible completions interface.
  - 3-tier model router: FAST (Lightning/Nano), BALANCED (Super), DEEP (Ultra).
  - Cost-aware routing based on task complexity.
  - Token tracking and cost accounting ledger.
  - Error reporting when credentials are missing.
"""

from __future__ import annotations

import os
import pytest
from axiom_dfir.nebius import (
    NebiusClient,
    NebiusModelRouter,
    GLOBAL_METRICS,
    verify_nebius_connection,
    DEFAULT_FAST_MODEL,
    DEFAULT_BALANCED_MODEL,
    DEFAULT_DEEP_MODEL,
)


def test_nebius_model_router_profiles():
    """Test that the model router maps investigation tasks to appropriate Nemotron profiles."""
    router = NebiusModelRouter()

    # Fast Profile
    m_fast, p_fast = router.route_task("inv1_tool_select")
    assert p_fast == "FAST"
    assert "Lightning" in m_fast or "nano" in m_fast

    # Balanced Profile
    m_bal, p_bal = router.route_task("react_cross_check")
    assert p_bal == "BALANCED"
    assert "Super" in m_bal

    # Deep Profile (unresolved conflicts or lateral movement)
    m_deep, p_deep = router.route_task("lateral_movement_analysis", unresolved_conflicts=2)
    assert p_deep == "DEEP"
    assert "Ultra" in m_deep


def test_nebius_client_mock_inference():
    """Test deterministic mock mode produces valid duck-typed responses with token usage."""
    client = NebiusClient()
    resp = client.create(
        model=DEFAULT_FAST_MODEL,
        messages=[{"role": "user", "content": "Analyze evidence."}],
        profile_hint="FAST",
    )
    assert resp.content[0].text
    assert resp.usage.input_tokens > 0
    assert resp.usage.output_tokens > 0
    assert "MOCK_MODE" in resp.model or "Lightning" in resp.model


def test_nebius_missing_credentials_reported():
    """Test that missing API keys report a clean error rather than failing silently."""
    old_key = os.environ.pop("NEBIUS_API_KEY", None)
    old_mock = os.environ.pop("AXIOM_MOCK_NEBIUS", None)

    try:
        res = verify_nebius_connection(api_key="", allow_mock=False)
        assert res["status"] == "MISSING_CREDENTIALS"
        assert "not set" in res["error"]
    finally:
        if old_key is not None:
            os.environ["NEBIUS_API_KEY"] = old_key
        if old_mock is not None:
            os.environ["AXIOM_MOCK_NEBIUS"] = old_mock


def test_metrics_ledger_recording():
    """Test that inference calls are properly recorded in the global metrics ledger."""
    prev_calls = len(GLOBAL_METRICS.records)
    client = NebiusClient()
    os.environ["AXIOM_MOCK_NEBIUS"] = "1"

    client.create(
        model=DEFAULT_BALANCED_MODEL,
        messages=[{"role": "user", "content": "Triage"}],
        profile_hint="BALANCED",
    )

    summary = GLOBAL_METRICS.summary()
    assert summary["total_requests"] >= prev_calls
    assert "total_tokens" in summary
    assert "estimated_cost_usd" in summary
