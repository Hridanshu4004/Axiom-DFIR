"""AXIOM DFIR - Interactive Investigation Web Console & API (Phase 6).

Provides an enterprise-grade DFIR investigation console:
  - Overview Dashboard
  - Evidence Explorer
  - Investigation Timeline
  - Process Tree & Network Activity
  - Attack Relationship Graph
  - Finding Verification & Hallucination Defense
  - Model Usage & Cost (NVIDIA Nemotron / Nebius Token Factory)
  - System Health & Live REST API
"""

from __future__ import annotations

import http.server
import json
import logging
import os
import socketserver
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import parse_qs, urlparse

from axiom_dfir.nebius import GLOBAL_METRICS
from axiom_dfir.orchestrator import AxiomOrchestrator, InvestigationStage

logger = logging.getLogger("axiom_dfir.web")

# In-memory active case state
CURRENT_ORCHESTRATOR: Optional[AxiomOrchestrator] = None


class AxiomAPIHandler(http.server.SimpleHTTPRequestHandler):
    """Custom HTTP handler serving live REST API endpoints and the single-page dashboard."""

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/" or path == "/index.html":
            self._serve_dashboard_html()
            return
        elif path == "/api/status":
            self._send_json(self._get_status_payload())
            return
        elif path == "/api/evidence":
            self._send_json(self._get_evidence_payload())
            return
        elif path == "/api/findings":
            self._send_json(self._get_findings_payload())
            return
        elif path == "/api/timeline":
            self._send_json(self._get_timeline_payload())
            return
        elif path == "/api/graph":
            self._send_json(self._get_graph_payload())
            return
        elif path == "/api/metrics":
            self._send_json(GLOBAL_METRICS.summary())
            return
        elif path == "/api/report":
            self._send_report_payload()
            return
        elif path == "/api/hypotheses":
            self._send_json(self._get_hypotheses_payload())
            return
        elif path == "/api/atomic_claims":
            self._send_json(self._get_atomic_claims_payload())
            return
        elif path == "/api/chain_of_custody":
            self._send_json(self._get_chain_of_custody_payload())
            return
        elif path == "/api/ocsf":
            self._send_json(self._get_ocsf_payload())
            return
        elif path == "/api/threat_intel":
            self._send_json(self._get_threat_intel_payload())
            return

        super().do_GET()

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/investigate/run_next":
            self._handle_run_next()
            return
        self.send_error(404, "Endpoint not found")

    def _send_json(self, data: Any, status: int = 200) -> None:
        body = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _get_status_payload(self) -> Dict[str, Any]:
        global CURRENT_ORCHESTRATOR
        if not CURRENT_ORCHESTRATOR:
            return {
                "active_case": False,
                "case_id": "N/A",
                "stage": "IDLE",
                "status": "WAITING_FOR_INVESTIGATION",
                "integrity_status": "UNINITIALIZED",
            }
        ctx = CURRENT_ORCHESTRATOR.context
        return {
            "active_case": True,
            "case_id": ctx.case_id,
            "stage": ctx.current_stage.value,
            "status": ctx.status,
            "integrity_status": ctx.integrity_status,
            "total_findings": len(ctx.validated_findings),
            "verified_findings": sum(1 for f in ctx.validated_findings if f.get("validation_status") == "VERIFIED"),
            "contradicted_findings": sum(1 for f in ctx.validated_findings if f.get("validation_status") == "CONTRADICTED"),
            "model_metrics": GLOBAL_METRICS.summary(),
        }

    def _get_evidence_payload(self) -> Dict[str, Any]:
        global CURRENT_ORCHESTRATOR
        if not CURRENT_ORCHESTRATOR or not CURRENT_ORCHESTRATOR.context.manifest:
            # Return sample evidence data for dashboard demonstration
            return {
                "manifest_id": "MAN-SAMPLE-01",
                "item_count": 3,
                "items": [
                    {
                        "evidence_id": "EV-001",
                        "original_filename": "memdump.raw",
                        "artifact_type": "MEMORY_IMAGE",
                        "sha256_hash": "a8f9c4b71234567890abcdef1234567890abcdef1234567890abcdef12345678",
                        "size_bytes": 4294967296,
                        "is_read_only": True,
                        "provenance": "LIVE_MEMORY_ACQUISITION",
                    },
                    {
                        "evidence_id": "EV-002",
                        "original_filename": "Security.evtx",
                        "artifact_type": "WINDOWS_EVENT_LOG",
                        "sha256_hash": "b2c3d4e51234567890abcdef1234567890abcdef1234567890abcdef12345678",
                        "size_bytes": 67108864,
                        "is_read_only": True,
                        "provenance": "TRIAGE_EXTRACT",
                    },
                    {
                        "evidence_id": "EV-003",
                        "original_filename": "Amcache.hve",
                        "artifact_type": "AMCACHE_REGISTRY_HIVE",
                        "sha256_hash": "c3d4e5f61234567890abcdef1234567890abcdef1234567890abcdef12345678",
                        "size_bytes": 16777216,
                        "is_read_only": True,
                        "provenance": "TRIAGE_EXTRACT",
                    },
                ],
            }
        return CURRENT_ORCHESTRATOR.context.manifest

    def _get_findings_payload(self) -> List[Dict[str, Any]]:
        global CURRENT_ORCHESTRATOR
        if not CURRENT_ORCHESTRATOR or not CURRENT_ORCHESTRATOR.context.validated_findings:
            return [
                {
                    "finding_id": "FIND-001",
                    "title": "Reverse Shell Execution via PowerShell",
                    "validation_status": "VERIFIED",
                    "confidence": 0.95,
                    "corroborating_evidence_refs": ["EV-001", "EV-002"],
                    "checks": [
                        {"claim_type": "process_existence", "detail": "PID 4120 verified in process tree", "evidence_ref": "EV-001"},
                        {"claim_type": "network_connection", "detail": "Socket 192.168.1.50:4444 verified", "evidence_ref": "EV-001"},
                    ],
                },
                {
                    "finding_id": "FIND-002",
                    "title": "Hallucinated Mimikatz In-Memory Injection",
                    "validation_status": "CONTRADICTED",
                    "confidence": 0.0,
                    "rejection_reason": "PID 9999 does not exist in evidence; no matching injected memory section.",
                    "checks": [
                        {"claim_type": "process_existence", "detail": "PID 9999 refuted (absent)", "contradicted": True},
                    ],
                },
            ]
        return CURRENT_ORCHESTRATOR.context.validated_findings

    def _get_timeline_payload(self) -> List[Dict[str, Any]]:
        global CURRENT_ORCHESTRATOR
        if not CURRENT_ORCHESTRATOR or not CURRENT_ORCHESTRATOR.context.timeline:
            return [
                {"timestamp": "2026-10-30T04:15:10Z", "event": "powershell.exe spawned with encoded command", "pid": 4120, "status": "VERIFIED"},
                {"timestamp": "2026-10-30T04:15:22Z", "event": "TCP connection initiated to 192.168.1.50:4444", "pid": 4120, "status": "VERIFIED"},
                {"timestamp": "2026-10-30T04:16:05Z", "event": "Discovery command whoami /all executed", "pid": 4188, "status": "VERIFIED"},
            ]
        return CURRENT_ORCHESTRATOR.context.timeline

    def _get_hypotheses_payload(self) -> List[Dict[str, Any]]:
        global CURRENT_ORCHESTRATOR
        if not CURRENT_ORCHESTRATOR or not CURRENT_ORCHESTRATOR.context.hypotheses:
            return [
                {
                    "hypothesis_id": "HYP-001",
                    "title": "Reverse Shell Execution via PowerShell (PID 4120)",
                    "status": "CONFIRMED",
                    "confidence_score": 0.95,
                    "entities": ["PROCESS-4120", "NETWORK-PORT-4444"],
                    "supporting_evidence": [{"evidence_id": "EV-001", "description": "PID 4120 spawned by non-standard parent"}],
                    "contradicting_evidence": [],
                    "resolution_reason": "Corroborated by socket connection and memory injection indicators.",
                },
                {
                    "hypothesis_id": "HYP-002",
                    "title": "Legitimate Dual-Use System Administration (PID 4120)",
                    "status": "REFUTED",
                    "confidence_score": 0.0,
                    "entities": ["PROCESS-4120", "USER-ADMIN"],
                    "supporting_evidence": [],
                    "contradicting_evidence": [{"evidence_id": "EV-001", "description": "Unbacked executable memory detected in process"}],
                    "resolution_reason": "Refuted by competing hypothesis HYP-001 and injected memory detection.",
                },
            ]
        return CURRENT_ORCHESTRATOR.context.hypotheses

    def _get_atomic_claims_payload(self) -> List[Dict[str, Any]]:
        global CURRENT_ORCHESTRATOR
        if not CURRENT_ORCHESTRATOR or not CURRENT_ORCHESTRATOR.context.atomic_claims:
            return [
                {
                    "claim_id": "CLM-001",
                    "claim_type": "PROCESS_SPAWN",
                    "subject": "process:powershell.exe:4120",
                    "predicate": "SPAWNED_BY",
                    "object": "process:explorer.exe:1024",
                    "validation_rule_id": "RULE-PROC-001",
                    "status": "VERIFIED",
                    "explanation": "PID 4120 verified spawned by PPID 1024 in process tree facts.",
                },
                {
                    "claim_id": "CLM-002",
                    "claim_type": "NETWORK_CONNECTION",
                    "subject": "process:powershell.exe:4120",
                    "predicate": "CONNECTED_TO",
                    "object": "socket:192.168.1.50:4444",
                    "validation_rule_id": "RULE-NET-001",
                    "status": "VERIFIED",
                    "explanation": "Active socket connection to 192.168.1.50:4444 confirmed in evidence.",
                },
            ]
        return CURRENT_ORCHESTRATOR.context.atomic_claims

    def _get_chain_of_custody_payload(self) -> Dict[str, Any]:
        global CURRENT_ORCHESTRATOR
        if not CURRENT_ORCHESTRATOR:
            return {
                "total_events": 15,
                "head_hash": "a1b2c3d4e5f67890123456789abcdef0123456789abcdef0123456789abcdef0",
                "verified": True,
                "signature": {"algorithm": "Ed25519", "signed_at": "2026-10-30T04:15:20Z"},
            }
        is_valid, reason = CURRENT_ORCHESTRATOR.chain_of_custody.verify_chain()
        d = CURRENT_ORCHESTRATOR.chain_of_custody.to_dict()
        d["verified"] = is_valid
        d["verification_error"] = reason
        return d

    def _get_ocsf_payload(self) -> List[Dict[str, Any]]:
        global CURRENT_ORCHESTRATOR
        if not CURRENT_ORCHESTRATOR or not CURRENT_ORCHESTRATOR.context.ocsf_events:
            return []
        return CURRENT_ORCHESTRATOR.context.ocsf_events

    def _get_threat_intel_payload(self) -> List[Dict[str, Any]]:
        global CURRENT_ORCHESTRATOR
        if not CURRENT_ORCHESTRATOR or not CURRENT_ORCHESTRATOR.context.threat_intel:
            return []
        return CURRENT_ORCHESTRATOR.context.threat_intel

    def _get_graph_payload(self) -> Dict[str, Any]:
        return {
            "nodes": [
                {"id": "proc_1024", "label": "explorer.exe (PID 1024)", "type": "PROCESS"},
                {"id": "proc_4120", "label": "powershell.exe (PID 4120)", "type": "PROCESS"},
                {"id": "ip_192.168.1.50", "label": "192.168.1.50:4444 (C2)", "type": "IP_ADDRESS"},
            ],
            "edges": [
                {"source": "proc_1024", "target": "proc_4120", "label": "SPAWNED"},
                {"source": "proc_4120", "target": "ip_192.168.1.50", "label": "CONNECTED_TO"},
            ],
        }

    def _handle_run_next(self) -> None:
        global CURRENT_ORCHESTRATOR
        if not CURRENT_ORCHESTRATOR:
            self._send_json({"error": "No active orchestrator initialized"}, status=400)
            return
        # Advance stage
        stages = list(InvestigationStage)
        curr_idx = stages.index(CURRENT_ORCHESTRATOR.context.current_stage)
        if curr_idx < len(stages) - 1:
            next_stage = stages[curr_idx + 1]
            success = CURRENT_ORCHESTRATOR.run_stage(next_stage)
            self._send_json({"advanced_to": next_stage.value, "success": success})
        else:
            self._send_json({"message": "Investigation already at terminal stage", "stage": stages[-1].value})

    def _send_report_payload(self) -> None:
        global CURRENT_ORCHESTRATOR
        if CURRENT_ORCHESTRATOR and CURRENT_ORCHESTRATOR.context.reports.get("html"):
            hp = Path(CURRENT_ORCHESTRATOR.context.reports["html"])
            if hp.is_file():
                content = hp.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
                return
        self._serve_dashboard_html()

    def _serve_dashboard_html(self) -> None:
        html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AXIOM DFIR - Autonomous Digital Forensics Console</title>
    <style>
        :root {
            --bg: #090D14;
            --surface: #101722;
            --surface-hover: #16202E;
            --border: #1E2B3C;
            --text-main: #F0F6FC;
            --text-muted: #8B949E;
            --accent: #00D26A;
            --blue: #38BDF8;
            --red: #F87171;
            --amber: #FBBF24;
            --font-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            --font-mono: 'JetBrains Mono', Consolas, monospace;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            background: var(--bg);
            color: var(--text-main);
            font-family: var(--font-sans);
            display: flex;
            height: 100vh;
            overflow: hidden;
        }
        #sidebar {
            width: 260px;
            background: var(--surface);
            border-right: 1px solid var(--border);
            display: flex;
            flex-direction: column;
        }
        .logo-box {
            padding: 20px;
            border-bottom: 1px solid var(--border);
        }
        .logo-title {
            font-size: 1.25rem;
            font-weight: 800;
            letter-spacing: 1px;
            color: var(--blue);
        }
        .logo-sub {
            font-size: 0.72rem;
            color: var(--text-muted);
            margin-top: 4px;
        }
        .nav-links {
            list-style: none;
            padding: 15px 0;
            flex: 1;
        }
        .nav-item {
            padding: 12px 20px;
            cursor: pointer;
            font-size: 0.9rem;
            display: flex;
            align-items: center;
            gap: 12px;
            color: var(--text-muted);
            transition: all 0.15s ease;
        }
        .nav-item:hover, .nav-item.active {
            color: var(--text-main);
            background: var(--surface-hover);
            border-left: 3px solid var(--blue);
        }
        #main-content {
            flex: 1;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        header {
            height: 64px;
            border-bottom: 1px solid var(--border);
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 30px;
            background: var(--surface);
        }
        .header-meta {
            display: flex;
            align-items: center;
            gap: 20px;
        }
        .badge {
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
        }
        .badge-verified { background: rgba(0, 210, 106, 0.15); color: var(--accent); border: 1px solid var(--accent); }
        .badge-contradicted { background: rgba(248, 113, 113, 0.15); color: var(--red); border: 1px solid var(--red); }
        .badge-amber { background: rgba(251, 191, 36, 0.15); color: var(--amber); border: 1px solid var(--amber); }
        .viewport {
            flex: 1;
            padding: 30px;
            overflow-y: auto;
        }
        .tab-panel { display: none; }
        .tab-panel.active { display: block; }
        .stat-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 20px;
        }
        .stat-label {
            font-size: 0.8rem;
            text-transform: uppercase;
            color: var(--text-muted);
            font-weight: 600;
        }
        .stat-val {
            font-size: 1.8rem;
            font-weight: 800;
            margin-top: 8px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            background: var(--surface);
            border-radius: 8px;
            overflow: hidden;
            border: 1px solid var(--border);
            margin-top: 15px;
        }
        th, td {
            padding: 14px 18px;
            text-align: left;
            border-bottom: 1px solid var(--border);
            font-size: 0.88rem;
        }
        th {
            background: #141D2B;
            color: var(--text-muted);
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.75rem;
        }
        code {
            font-family: var(--font-mono);
            background: rgba(56, 189, 248, 0.1);
            color: var(--blue);
            padding: 2px 6px;
            border-radius: 4px;
        }
        .principle-banner {
            background: rgba(56, 189, 248, 0.08);
            border: 1px solid rgba(56, 189, 248, 0.25);
            border-radius: 8px;
            padding: 16px 20px;
            margin-bottom: 25px;
            display: flex;
            align-items: center;
            gap: 12px;
            font-size: 0.95rem;
        }
        .btn {
            background: var(--blue);
            color: #000;
            font-weight: 700;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.85rem;
        }
        .btn:hover { opacity: 0.9; }
    </style>
</head>
<body>
    <div id="sidebar">
        <div class="logo-box">
            <div class="logo-title">AXIOM DFIR</div>
            <div class="logo-sub">Autonomous Evidence-Verified DFIR</div>
        </div>
        <ul class="nav-links">
            <li class="nav-item active" onclick="switchTab('overview')">📊 Overview Dashboard</li>
            <li class="nav-item" onclick="switchTab('evidence')">🗂️ Evidence Explorer</li>
            <li class="nav-item" onclick="switchTab('findings')">🛡️ Finding Verification</li>
            <li class="nav-item" onclick="switchTab('hypotheses')">🔬 Hypothesis Ledger</li>
            <li class="nav-item" onclick="switchTab('claims')">⚛️ Atomic Claims</li>
            <li class="nav-item" onclick="switchTab('timeline')">⏱️ Reconstructed Timeline</li>
            <li class="nav-item" onclick="switchTab('graph')">🕸️ Attack Relationship Graph</li>
            <li class="nav-item" onclick="switchTab('custody')">⛓️ Chain of Custody & Seal</li>
            <li class="nav-item" onclick="switchTab('models')">⚡ Model Usage & Cost</li>
        </ul>
    </div>

    <div id="main-content">
        <header>
            <div class="header-meta">
                <span>Case: <strong id="hdr-case">CASE-001</strong></span>
                <span class="badge badge-verified" id="hdr-integrity">SHA256 INTACT</span>
                <span class="badge badge-amber" id="hdr-stage">STAGE_10: CLAIM_VALIDATION</span>
            </div>
            <div>
                <button class="btn" onclick="fetchData()">🔄 Refresh State</button>
            </div>
        </header>

        <div class="viewport">
            <div class="principle-banner">
                <span>⚖️</span>
                <span><strong>AXIOM Core Invariant:</strong> The AI may propose a finding, but only verified forensic evidence can confirm it.</span>
            </div>

            <!-- Tab 1: Overview -->
            <div id="tab-overview" class="tab-panel active">
                <div class="stat-grid">
                    <div class="stat-card">
                        <div class="stat-label">Verified Findings</div>
                        <div class="stat-val" style="color: var(--accent)" id="val-verified">1</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Contradicted Claims</div>
                        <div class="stat-val" style="color: var(--red)" id="val-contradicted">1</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Inference Model Profile</div>
                        <div class="stat-val" style="color: var(--blue)">Nemotron 3.5</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Inference Provider</div>
                        <div class="stat-val">Nebius Cloud</div>
                    </div>
                </div>

                <h3>Active Incident Overview</h3>
                <table id="overview-table">
                    <thead>
                        <tr><th>Finding ID</th><th>Title</th><th>Validation Status</th><th>Confidence</th></tr>
                    </thead>
                    <tbody id="overview-findings-body"></tbody>
                </table>
            </div>

            <!-- Tab 2: Evidence Explorer -->
            <div id="tab-evidence" class="tab-panel">
                <h3>Forensic Evidence Manifest</h3>
                <p style="color: var(--text-muted); margin: 6px 0 15px 0;">All evidence is mounted strictly read-only with cryptographic SHA256 seals.</p>
                <table>
                    <thead>
                        <tr><th>Evidence ID</th><th>Filename</th><th>Artifact Type</th><th>SHA256 Fingerprint</th><th>Size</th><th>Read-Only</th></tr>
                    </thead>
                    <tbody id="evidence-tbody"></tbody>
                </table>
            </div>

            <!-- Tab 3: Finding Verification -->
            <div id="tab-findings" class="tab-panel">
                <h3>Deterministic Claim Validation Ledger</h3>
                <p style="color: var(--text-muted); margin: 6px 0 15px 0;">Deterministic code rules verify or reject every factual assertion proposed by AI.</p>
                <div id="findings-container"></div>
            </div>

            <!-- Tab 4: Timeline -->
            <div id="tab-timeline" class="tab-panel">
                <h3>Reconstructed Incident Timeline</h3>
                <table>
                    <thead>
                        <tr><th>Timestamp (UTC)</th><th>Event Description</th><th>Attribution</th><th>Verification</th></tr>
                    </thead>
                    <tbody id="timeline-tbody"></tbody>
                </table>
            </div>

            <!-- Tab 5: Graph -->
            <div id="tab-graph" class="tab-panel">
                <h3>Attack Entity Relationship Graph</h3>
                <div id="graph-container" style="background: var(--surface); padding: 30px; border-radius: 8px; border: 1px solid var(--border);">
                    <div style="font-family: var(--font-mono); font-size: 0.9rem; line-height: 2;">
                        <div>[PROCESS: explorer.exe (PID 1024)]</div>
                        <div style="color: var(--blue);">  └── SPAWNED ──> [PROCESS: powershell.exe (PID 4120)]</div>
                        <div style="color: var(--accent);">                    └── CONNECTED_TO ──> [IP: 192.168.1.50:4444] (C2 Server)</div>
                    </div>
                </div>
            </div>

            <!-- Tab 6: Model Usage & Cost -->
            <div id="tab-models" class="tab-panel">
                <h3>Nebius Token Factory & NVIDIA Nemotron Telemetry</h3>
                <div class="stat-grid" style="margin-top: 15px;">
                    <div class="stat-card">
                        <div class="stat-label">Total Requests</div>
                        <div class="stat-val" id="metric-requests">0</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Tokens Processed</div>
                        <div class="stat-val" id="metric-tokens">0</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Estimated Cost</div>
                        <div class="stat-val" style="color: var(--accent)" id="metric-cost">$0.000000</div>
                    </div>
                </div>
            </div>

            <!-- Tab: Hypothesis Ledger -->
            <div id="tab-hypotheses" class="tab-panel">
                <h3>Adaptive Investigation Hypothesis Ledger</h3>
                <p style="color: var(--text-muted); font-size: 0.88rem; margin-bottom: 15px;">Falsification-first hypothesis tracking. Only deterministic forensic evidence can confirm or refute an investigative proposition.</p>
                <div id="hypotheses-container"></div>
            </div>

            <!-- Tab: Atomic Claims -->
            <div id="tab-claims" class="tab-panel">
                <h3>Deterministic Atomic Claim Verification</h3>
                <p style="color: var(--text-muted); font-size: 0.88rem; margin-bottom: 15px;">Decomposed (Subject, Predicate, Object) tuples evaluated against explicit mathematical rule engines.</p>
                <table>
                    <thead>
                        <tr><th>Claim ID</th><th>Type</th><th>Subject</th><th>Predicate</th><th>Object</th><th>Rule ID</th><th>Verdict</th></tr>
                    </thead>
                    <tbody id="claims-tbody"></tbody>
                </table>
            </div>

            <!-- Tab: Chain of Custody & Seal -->
            <div id="tab-custody" class="tab-panel">
                <h3>Cryptographic Chain of Custody & Ed25519 Digital Seal</h3>
                <div class="stat-grid" style="margin-top: 15px;">
                    <div class="stat-card">
                        <div class="stat-label">Chain Integrity</div>
                        <div class="stat-val" style="color: var(--accent);" id="coc-status">VERIFIED INTACT</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Audit Events</div>
                        <div class="stat-val" id="coc-events">0</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Ed25519 Seal</div>
                        <div class="stat-val" style="font-size: 1.1rem; word-break: break-all; color: var(--blue);" id="coc-seal">ACTIVE</div>
                    </div>
                </div>
                <div style="background: var(--surface); padding: 20px; border-radius: 8px; border: 1px solid var(--border);">
                    <h4>Latest Chain Head SHA-256 Digest</h4>
                    <code id="coc-head" style="font-size: 1rem; display: block; margin-top: 10px; padding: 10px;"></code>
                </div>
            </div>
        </div>
    </div>

    <!-- Drill-Down Modal -->
    <div id="finding-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.75); z-index:1000; align-items:center; justify-content:center;">
        <div style="background: var(--surface); border: 1px solid var(--border); border-radius: 8px; width: 680px; max-width: 90%; max-height: 85vh; overflow-y: auto; padding: 25px; box-shadow: 0 10px 40px rgba(0,0,0,0.8);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                <h3 id="modal-title" style="margin: 0;">Finding Drill-Down</h3>
                <button onclick="closeModal()" style="background: transparent; border: none; color: var(--text-muted); font-size: 1.5rem; cursor: pointer;">&times;</button>
            </div>
            <div id="modal-content"></div>
        </div>
    </div>

    <script>
        function switchTab(name) {
            document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.tab-panel').forEach(el => el.classList.remove('active'));
            event.currentTarget.classList.add('active');
            document.getElementById('tab-' + name).classList.add('active');
        }

        let CACHED_FINDINGS = [];

        function closeModal() {
            document.getElementById('finding-modal').style.display = 'none';
        }

        function openFindingModal(findingId) {
            const f = CACHED_FINDINGS.find(x => x.finding_id === findingId);
            if (!f) return;
            document.getElementById('modal-title').innerText = `${f.title} (${f.finding_id})`;
            let checksHtml = (f.checks || []).map(c => `
                <div style="background: rgba(255,255,255,0.03); padding: 10px; border-radius: 4px; margin-bottom: 8px;">
                    <div><strong>Claim Type:</strong> <code>${c.claim_type}</code></div>
                    <div><strong>Detail:</strong> ${c.detail}</div>
                    <div><strong>Matched:</strong> <span class="badge ${c.contradicted ? 'badge-contradicted' : 'badge-verified'}">${c.contradicted ? 'CONTRADICTED' : 'MATCHED'}</span></div>
                </div>
            `).join('');
            document.getElementById('modal-content').innerHTML = `
                <div style="margin-bottom: 15px;">
                    <span class="badge ${f.validation_status === 'VERIFIED' ? 'badge-verified' : 'badge-contradicted'}">${f.validation_status}</span>
                    <span style="margin-left: 10px; color: var(--text-muted);">Confidence: ${(f.confidence * 100).toFixed(0)}%</span>
                </div>
                <div style="margin-bottom: 15px;">
                    <h4>Deterministic Verification Checks</h4>
                    ${checksHtml || '<p style="color:var(--text-muted);">No atomic check breakdown available.</p>'}
                </div>
                <div>
                    <h4>Evidence Provenance References</h4>
                    <code>${(f.corroborating_evidence_refs || []).join(', ') || 'N/A'}</code>
                </div>
            `;
            document.getElementById('finding-modal').style.display = 'flex';
        }

        async function fetchData() {
            try {
                const s = await (await fetch('/api/status')).json();
                document.getElementById('hdr-case').innerText = s.case_id || 'CASE-001';
                document.getElementById('hdr-stage').innerText = s.stage || 'STAGE_10';
                document.getElementById('val-verified').innerText = s.verified_findings || 0;
                document.getElementById('val-contradicted').innerText = s.contradicted_findings || 0;

                // Evidence
                const ev = await (await fetch('/api/evidence')).json();
                const evBody = document.getElementById('evidence-tbody');
                evBody.innerHTML = (ev.items || []).map(it => `
                    <tr>
                        <td><code>${it.evidence_id}</code></td>
                        <td>${it.original_filename}</td>
                        <td><span class="badge badge-amber">${it.artifact_type}</span></td>
                        <td><code>${it.sha256_hash.substring(0, 16)}...</code></td>
                        <td>${(it.size_bytes / (1024*1024)).toFixed(2)} MB</td>
                        <td><span class="badge badge-verified">YES</span></td>
                    </tr>
                `).join('');

                // Findings
                const findings = await (await fetch('/api/findings')).json();
                CACHED_FINDINGS = findings;
                document.getElementById('overview-findings-body').innerHTML = findings.map(f => `
                    <tr style="cursor: pointer;" onclick="openFindingModal('${f.finding_id}')">
                        <td><code>${f.finding_id}</code></td>
                        <td>${f.title}</td>
                        <td><span class="badge ${f.validation_status === 'VERIFIED' ? 'badge-verified' : 'badge-contradicted'}">${f.validation_status}</span></td>
                        <td>${(f.confidence * 100).toFixed(0)}%</td>
                    </tr>
                `).join('');

                document.getElementById('findings-container').innerHTML = findings.map(f => `
                    <div style="background: var(--surface); border: 1px solid var(--border); padding: 20px; border-radius: 8px; margin-bottom: 15px; border-left: 4px solid ${f.validation_status === 'VERIFIED' ? 'var(--accent)' : 'var(--red)'}; cursor: pointer;" onclick="openFindingModal('${f.finding_id}')">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                            <h4>${f.title} (<code>${f.finding_id}</code>)</h4>
                            <span class="badge ${f.validation_status === 'VERIFIED' ? 'badge-verified' : 'badge-contradicted'}">${f.validation_status}</span>
                        </div>
                        <p style="color: var(--text-muted); font-size: 0.88rem;">${f.rejection_reason ? '<strong>Rejection:</strong> ' + f.rejection_reason : 'Corroborating Evidence: <code>' + (f.corroborating_evidence_refs || []).join(', ') + '</code>'}</p>
                    </div>
                `).join('');

                // Hypotheses
                const hyp = await (await fetch('/api/hypotheses')).json();
                document.getElementById('hypotheses-container').innerHTML = hyp.map(h => `
                    <div style="background: var(--surface); border: 1px solid var(--border); padding: 20px; border-radius: 8px; margin-bottom: 15px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <h4>[${h.hypothesis_id}] ${h.title}</h4>
                            <span class="badge ${h.status === 'CONFIRMED' ? 'badge-verified' : (h.status === 'REFUTED' ? 'badge-contradicted' : 'badge-amber')}">${h.status}</span>
                        </div>
                        <p style="font-size: 0.9rem; margin-bottom: 8px;">${h.description}</p>
                        <div style="font-size: 0.8rem; color: var(--text-muted);">
                            <strong>Confidence:</strong> ${(h.confidence_score * 100).toFixed(0)}% | 
                            <strong>Entities:</strong> <code>${(h.entities || []).join(', ')}</code>
                        </div>
                        ${h.resolution_reason ? `<div style="margin-top: 8px; font-size: 0.85rem; color: var(--accent);"><strong>Resolution:</strong> ${h.resolution_reason}</div>` : ''}
                    </div>
                `).join('');

                // Atomic Claims
                const claims = await (await fetch('/api/atomic_claims')).json();
                document.getElementById('claims-tbody').innerHTML = claims.map(c => `
                    <tr>
                        <td><code>${c.claim_id}</code></td>
                        <td>${c.claim_type}</td>
                        <td><code>${c.subject}</code></td>
                        <td><strong>${c.predicate}</strong></td>
                        <td><code>${c.object}</code></td>
                        <td><code>${c.validation_rule_id || 'N/A'}</code></td>
                        <td><span class="badge ${c.status === 'VERIFIED' ? 'badge-verified' : 'badge-contradicted'}">${c.status}</span></td>
                    </tr>
                `).join('');

                // Chain of Custody
                const coc = await (await fetch('/api/chain_of_custody')).json();
                document.getElementById('coc-status').innerText = coc.verified ? 'VERIFIED INTACT' : 'COMPROMISED';
                document.getElementById('coc-status').style.color = coc.verified ? 'var(--accent)' : 'var(--red)';
                document.getElementById('coc-events').innerText = coc.total_events || 0;
                document.getElementById('coc-seal').innerText = coc.signature ? `${coc.signature.algorithm} VALID` : 'PENDING FINAL STAGE';
                document.getElementById('coc-head').innerText = coc.head_hash || 'N/A';

                // Timeline
                const tl = await (await fetch('/api/timeline')).json();
                document.getElementById('timeline-tbody').innerHTML = tl.map(t => `
                    <tr>
                        <td><code>${t.timestamp}</code></td>
                        <td>${t.event}</td>
                        <td><code>PID ${t.pid || 'N/A'}</code></td>
                        <td><span class="badge badge-verified">${t.status}</span></td>
                    </tr>
                `).join('');

                // Metrics
                const m = await (await fetch('/api/metrics')).json();
                document.getElementById('metric-requests').innerText = m.total_requests || 0;
                document.getElementById('metric-tokens').innerText = (m.total_tokens || 0).toLocaleString();
                document.getElementById('metric-cost').innerText = '$' + (m.estimated_cost_usd || 0).toFixed(6);

            } catch (e) {
                console.error("Failed to fetch API data", e);
            }
        }

        window.onload = fetchData;
        setInterval(fetchData, 5000);
    </script>
</body>
</html>
"""
        body = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def start_web_console(
    orchestrator: Optional[AxiomOrchestrator] = None,
    host: str = "0.0.0.0",
    port: int = 8080,
    blocking: bool = True,
) -> Any:
    """Launches the AXIOM DFIR web console HTTP server."""
    global CURRENT_ORCHESTRATOR
    CURRENT_ORCHESTRATOR = orchestrator

    handler = AxiomAPIHandler
    server = socketserver.TCPServer((host, port), handler)
    server.allow_reuse_address = True

    logger.info("AXIOM DFIR Web Console listening on http://%s:%d", host, port)
    print(f"\n========================================================")
    print(f"  AXIOM DFIR Web Console active at: http://localhost:{port}")
    print(f"  Target: Nebius x NVIDIA Global AI Hackathon 2026")
    print(f"========================================================\n", flush=True)

    if blocking:
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            server.server_close()
    else:
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        return server

