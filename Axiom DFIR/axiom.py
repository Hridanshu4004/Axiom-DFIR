#!/usr/bin/env python3
"""AXIOM DFIR: Autonomous Evidence-Verified Digital Forensics & Incident Response.

Target Event: Nebius x NVIDIA Global AI Hackathon 2026 (Best Apps & Agents Track).
Primary Command-Line Interface.
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

# ANSI styling
_TTY = sys.stdout.isatty() or os.environ.get("SIFT_FORCE_COLOR") == "1"
CYAN = "\033[96m" if _TTY else ""
GREEN = "\033[92m" if _TTY else ""
AMBER = "\033[93m" if _TTY else ""
RED = "\033[91m" if _TTY else ""
BOLD = "\033[1m" if _TTY else ""
RESET = "\033[0m" if _TTY else ""


def print_banner() -> None:
    banner = f"""
{CYAN}{BOLD}█████╗ ██╗  ██╗██╗ ██████╗ ███╗   ███╗    ██████╗ ███████╗██╗██████╗ 
██╔══██╗╚██╗██╔╝██║██╔═══██╗████╗ ████║    ██╔══██╗██╔════╝██║██╔══██╗
███████║ ╚███╔╝ ██║██║   ██║██╔████╔██║    ██║  ██║█████╗  ██║██████╔╝
██╔══██║ ██╔██╗ ██║██║   ██║██║╚██╔╝██║    ██║  ██║██╔══╝  ██║██╔══██╗
██║  ██║██╔╝ ██╗██║╚██████╔╝██║ ╚═╝ ██║    ██████╔╝██║     ██║██║  ██║
╚═╝  ╚═╝╚═╝  ╚═╝╚═╝ ╚═════╝ ╚═╝     ╚═╝    ╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═╝{RESET}
  {BOLD}Autonomous Evidence-Verified Digital Forensics & Incident Response{RESET}
  {AMBER}Powered by Nebius Token Factory & NVIDIA Nemotron Reasoning{RESET}
  {GREEN}Invariant: The AI may propose a finding, but only verified evidence can confirm it.{RESET}
"""
    print(banner, flush=True)


def cmd_verify_nebius(args: argparse.Namespace) -> int:
    from axiom_dfir.nebius import verify_nebius_connection
    print(f"\n{CYAN}Testing Nebius Token Factory & NVIDIA Nemotron Connectivity...{RESET}")
    res = verify_nebius_connection(
        api_key=args.api_key,
        base_url=args.base_url,
        model=args.model,
    )
    if res["status"] in ("CONNECTED", "SUCCESS"):
        print(f"{GREEN}[PASS] Successfully connected to Nebius Token Factory!{RESET}")
        print(f"  Model  : {res['model']}")
        print(f"  Latency: {res['latency_seconds']:.3f}s")
        print(f"  Reply  : {res['reply']!r}")
        return 0
    else:
        print(f"{RED}[FAIL] Connection failed: {res.get('error')}{RESET}")
        return 1


def cmd_triage(args: argparse.Namespace) -> int:
    import step0_onboard
    return step0_onboard.main([args.evidence] if args.evidence else [])


def cmd_run(args: argparse.Namespace) -> int:
    from axiom_dfir.orchestrator import AxiomOrchestrator
    case_id = args.case_id or f"CASE-{Path(args.evidence).stem.upper()}"
    print(f"\n{CYAN}Launching AXIOM DFIR Investigation State Machine for {case_id}...{RESET}")
    orch = AxiomOrchestrator(
        case_id=case_id,
        evidence_path=args.evidence,
        state_dir=args.state_dir,
    )
    success = orch.execute_all_stages()
    if success:
        print(f"\n{GREEN}[+] Investigation complete. Reports generated in {orch.state_dir}{RESET}")
        return 0
    else:
        print(f"\n{RED}[!] Investigation encountered an error. Check logs in {orch.state_dir}{RESET}")
        return 1


def cmd_demo(args: argparse.Namespace) -> int:
    print(f"\n{CYAN}Running AXIOM DFIR Synthetic Demonstration Mode...{RESET}")
    import findevil
    return findevil.main(["--demo"])


def cmd_web(args: argparse.Namespace) -> int:
    try:
        import uvicorn
        from axiom_dfir.api import app
        print(f"\n{CYAN}Starting AXIOM DFIR Production Web Console & REST API at http://{args.host}:{args.port}{RESET}")
        print(f"{GREEN}OpenAPI Swagger Documentation: http://{args.host}:{args.port}/docs{RESET}\n")
        uvicorn.run(app, host=args.host, port=args.port, log_level="info")
        return 0
    except Exception as e:
        print(f"{AMBER}Falling back to built-in HTTP server: {e}{RESET}")
        from axiom_dfir.web import start_web_console
        from axiom_dfir.orchestrator import AxiomOrchestrator
        orch = AxiomOrchestrator(
            case_id="CASE-DEMO-2026",
            evidence_path="sample_evidence",
            state_dir=Path(os.environ.get("TEMP", "/tmp")) / "axiom-web-demo",
        )
        start_web_console(orchestrator=orch, host=args.host, port=args.port, blocking=True)
        return 0


def main(argv=None) -> int:
    print_banner()
    parser = argparse.ArgumentParser(
        description="AXIOM DFIR: Autonomous Evidence-Verified Digital Forensics & Incident Response",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="subcommand", help="Available Commands")

    # verify-nebius
    p_verify = subparsers.add_parser("verify-nebius", help="Test live Nebius Token Factory inference")
    p_verify.add_argument("--api-key", type=str, default=None, help="Nebius API key override")
    p_verify.add_argument("--base-url", type=str, default=None, help="Nebius endpoint URL override")
    p_verify.add_argument("--model", type=str, default=None, help="Model ID override")
    p_verify.set_defaults(func=cmd_verify_nebius)

    # triage
    p_triage = subparsers.add_parser("triage", help="Interactive evidence onboarding and triage")
    p_triage.add_argument("evidence", nargs="?", default="", help="Path to evidence file or directory")
    p_triage.set_defaults(func=cmd_triage)

    # run
    p_run = subparsers.add_parser("run", help="Run the full 15-stage autonomous DFIR pipeline")
    p_run.add_argument("evidence", help="Path to evidence file or directory")
    p_run.add_argument("--case-id", type=str, default=None, help="Unique Case ID")
    p_run.add_argument("--state-dir", type=str, default=None, help="Custom state output directory")
    p_run.set_defaults(func=cmd_run)

    # demo
    p_demo = subparsers.add_parser("demo", help="Run interactive synthetic demonstration")
    p_demo.set_defaults(func=cmd_demo)

    # web
    p_web = subparsers.add_parser("web", help="Start the interactive DFIR Web Console & REST API")
    p_web.add_argument("--port", type=int, default=8080, help="Port to listen on (default 8080)")
    p_web.add_argument("--host", type=str, default="127.0.0.1", help="Host interface (default 127.0.0.1)")
    p_web.set_defaults(func=cmd_web)

    args = parser.parse_args(argv)
    if not args.subcommand:
        parser.print_help()
        return 0

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
