#!/usr/bin/env python3
"""Nebius Token Factory & NVIDIA Nemotron connectivity smoke test for AXIOM DFIR.

Run this script to verify live inference connectivity to Nebius Token Factory:

    export NEBIUS_API_KEY=your_key_here
    python scripts/nebius_smoke.py

Exit codes:
    0 = Successfully reached Nebius Token Factory and parsed response
    2 = Missing NEBIUS_API_KEY / not configured
    1 = Inference call failed (transport, auth, or model error)
"""
from __future__ import annotations

import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "src"))

from axiom_dfir.nebius import (
    NebiusClient,
    verify_nebius_connection,
    DEFAULT_NEBIUS_BASE_URL,
    DEFAULT_FAST_MODEL,
    DEFAULT_BALANCED_MODEL,
    DEFAULT_DEEP_MODEL,
)


def main() -> int:
    print("=" * 72)
    print("  AXIOM DFIR - Nebius Token Factory Inference Verification")
    print("  Target Track: Best Apps & Agents (Nebius x NVIDIA Hackathon 2026)")
    print("=" * 72)

    api_key = os.environ.get("NEBIUS_API_KEY") or os.environ.get("TOKEN_FACTORY_API_KEY")
    base_url = os.environ.get("NEBIUS_BASE_URL") or DEFAULT_NEBIUS_BASE_URL
    fast_model = os.environ.get("AXIOM_FAST_MODEL") or DEFAULT_FAST_MODEL
    balanced_model = os.environ.get("AXIOM_BALANCED_MODEL") or DEFAULT_BALANCED_MODEL
    deep_model = os.environ.get("AXIOM_DEEP_MODEL") or DEFAULT_DEEP_MODEL

    print(f"Endpoint URL    : {base_url}")
    print(f"FAST Profile    : {fast_model}")
    print(f"BALANCED Profile: {balanced_model}")
    print(f"DEEP Profile    : {deep_model}")

    if not api_key:
        if os.environ.get("AXIOM_MOCK_NEBIUS") == "1":
            print("\n[NOTE] Running in synthetic MOCK verification mode (AXIOM_MOCK_NEBIUS=1).")
        else:
            print("\n[!] ERROR: NEBIUS_API_KEY environment variable is not configured.")
            print("    Please set your Nebius API key:")
            print("        export NEBIUS_API_KEY=your_token_here (Linux/macOS)")
            print("        $env:NEBIUS_API_KEY='your_token_here' (Windows PowerShell)")
            print("\n    To run automated offline tests without spending tokens:")
            print("        export AXIOM_MOCK_NEBIUS=1")
            return 2

    print(f"\nDispatching verification request using {fast_model} ...")
    res = verify_nebius_connection(api_key=api_key, base_url=base_url, model=fast_model)

    if res["status"] in ("CONNECTED", "SUCCESS"):
        print("\n  [PASS] Successfully reached Nebius Token Factory!")
        print(f"  Model Responding : {res['model']}")
        print(f"  Round-trip Latency: {res['latency_seconds']:.3f}s")
        print(f"  Sample Output    : {res['reply']!r}")
        u = res.get("token_usage", {})
        print(f"  Token Accounting : Prompt={u.get('input', 0)}, Completion={u.get('output', 0)}, Cached={u.get('cached', 0)}")
        print("\nAXIOM DFIR is fully wired to Nebius Token Factory inference.")
        return 0
    else:
        print(f"\n  [FAIL] Connectivity failed: {res.get('error')}")
        print("  Please check your network connection, API key, and endpoint URL.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

