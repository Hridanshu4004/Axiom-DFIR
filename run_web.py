#!/usr/bin/env python3
"""Launcher for the AXIOM DFIR Interactive Web Console & REST API.

Usage:
    python run_web.py [--port 8080] [--host 127.0.0.1]
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

# Safe Windows UTF-8 reconfigure
if os.name == "nt":
    for _stream in (sys.stdout, sys.stderr):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError, OSError):
            pass

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "src"))
sys.path.insert(0, str(HERE / "Axiom DFIR" / "src"))

from axiom_dfir.orchestrator import AxiomOrchestrator


def main() -> int:
    parser = argparse.ArgumentParser(description="AXIOM DFIR Web Console & API Server")
    parser.add_argument("--port", type=int, default=8000, help="Port to listen on (default 8000)")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host interface (default 127.0.0.1)")
    parser.add_argument("--evidence", type=str, default="", help="Path to evidence for live demo")
    args = parser.parse_args()

    evidence_path = Path(args.evidence) if args.evidence else None
    if not evidence_path or not evidence_path.exists():
        fallback = HERE / "Axiom DFIR" / "yara_rules"
        evidence_path = fallback if fallback.exists() else HERE / "yara_rules"

    if not os.environ.get("NEBIUS_API_KEY"):
        os.environ["AXIOM_MOCK_NEBIUS"] = "1"

    demo_state_dir = Path(os.environ.get("TEMP", "/tmp")) / "axiom-web-demo"
    demo_state_dir.mkdir(parents=True, exist_ok=True)

    orch = AxiomOrchestrator(
        case_id="CASE-DEMO-2026",
        evidence_path=evidence_path,
        state_dir=demo_state_dir,
    )
    print("\n[*] Pre-populating AXIOM DFIR 15-stage state machine for live console...")
    orch.execute_all_stages()
    print("[+] State machine pre-population complete!\n")

    try:
        import uvicorn
        from axiom_dfir.api import app, CASE_REGISTRY
        CASE_REGISTRY["CASE-DEMO-2026"] = orch

        print(f"============================================================")
        print(f"  AXIOM DFIR Production Web Console & REST API Active")
        print(f"  Web Interface : http://{args.host}:{args.port}")
        print(f"  Swagger Docs  : http://{args.host}:{args.port}/docs")
        print(f"  ReDoc Docs    : http://{args.host}:{args.port}/redoc")
        print(f"============================================================\n")
        uvicorn.run(app, host=args.host, port=args.port, log_level="info")
        return 0
    except Exception as exc:
        print(f"[!] Falling back to standalone console: {exc}")
        from axiom_dfir.web import start_web_console
        start_web_console(orchestrator=orch, host=args.host, port=args.port, blocking=True)
        return 0


if __name__ == "__main__":
    sys.exit(main())
