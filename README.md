<p align="center">
  <h1 align="center">🛡️ AXIOM DFIR</h1>
  <p align="center"><strong>Autonomous Evidence-Verified Digital Forensics & Incident Response</strong></p>
  <p align="center"><em>Target Track: Best Apps & Agents · Nebius x NVIDIA Global AI Hackathon 2026</em></p>
</p>

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge&labelColor=0A0F16)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20Windows%20%7C%20macOS%20%7C%20Docker-2496ED?style=for-the-badge&labelColor=0A0F16)](#-quick-start)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white&labelColor=0A0F16)](pyproject.toml)
[![Inference](https://img.shields.io/badge/Nebius_Token_Factory-NVIDIA_Nemotron-76B900?style=for-the-badge&logo=nvidia&logoColor=white&labelColor=0A0F16)](#-nebius-token-factory--nvidia-nemotron-integration)
[![Validation](https://img.shields.io/badge/Validation-Deterministic_Code_Gate-critical?style=for-the-badge&labelColor=0A0F16)](#-deterministic-claim-validation-engine)

</div>

---

> ### ⚖️ Core Engineering Invariant:
> **"The AI may propose an investigative finding, but only verified forensic evidence can confirm it."**

---

## 1. Project Introduction

**AXIOM DFIR** is an enterprise-grade autonomous digital forensics and incident response (DFIR) investigation platform. Designed for high-stakes cybersecurity operations, it ingests volatile memory images, disk captures, Windows event logs (EVTX), and filesystem artifacts to reconstruct complete intrusion timelines without human fatigue and without model hallucinations.

By combining the reasoning power of **NVIDIA Nemotron models** served via **Nebius Token Factory** with a **deterministic code validation gate**, AXIOM DFIR eliminates the single biggest risk of AI in cybersecurity: ungrounded assumptions, false positives, and fabricated indicators of compromise (IOCs).

---

## 2. Problem Statement: The Crisis in Modern DFIR

Digital forensics and incident response face two compounding crises:
1. **The Investigation Bottleneck**: Modern intrusion cases yield tens of gigabytes of disk and memory data, millions of event log records, and thousands of process threads. Triaging an enterprise breach manually takes experienced forensic analysts days or weeks.
2. **The LLM Hallucination Trap**: Naive AI security agents frequently hallucinate benign processes as malicious, invent non-existent process IDs (PIDs), forge cryptographic hashes, and mistake system noise for command-and-control (C2) activity. In forensic investigations and legal proceedings, taking an AI's word at face value is catastrophic.

---

## 3. The AXIOM DFIR Solution & Core Differentiators

| Capability | Legacy Manual DFIR | Naive LLM Agent | AXIOM DFIR (Phase II) |
|---|---|---|---|
| **Investigation Speed** | Days to weeks | Minutes (Unreliable) | **Minutes (Cryptographically Verified)** |
| **Hallucination Rate** | N/A (Manual) | High (~30–62.5% false alarms) | **0.0% (Deterministic Code Gate Rejects All Mismatches)** |
| **Reasoning Engine** | Static rules | Unconstrained generation | **Adaptive Hypothesis Testing (Falsification-First)** |
| **Model Shell Access** | N/A | Dangerous (Direct shell execution) | **Zero Shell Access (Strict Typed MCP Subprocess Boundaries)** |
| **Evidence Tampering Defense** | Manual hash logs | None | **Content-Addressed Storage (CAS) + Spoliation Halt** |
| **Chain of Custody** | Paper records | None | **Hash-Chained Audit Ledger + Ed25519 Digital Seal (ISO 27037)** |
| **Event Normalization** | Proprietary formats | Raw text strings | **Standardized OCSF v1.1.0 (Classes 1007, 4001, 3002)** |
| **Inference Efficiency** | N/A | Monolithic large model | **Cost-Aware Dynamic Escalation (Nemotron Lightning/Super/Ultra)** |
| **External Threat Intel** | Disjoint lookups | Hallucinated reputations | **Tavily OSINT API strictly isolated as `EXTERNAL_THREAT_INTEL`** |
| **Audit Traceability** | Disjoint notes | Hallucinated quotes | **Every Finding Linked to Raw Byte/Tool Proof + Explainability** |

---

## 4. System Architecture

AXIOM DFIR operates across a decoupled, multi-tiered architecture:

```
[ Forensic Evidence: Memory Dumps, Disk Images, EVTX, Registry Hives ]
                                 │
                                 ▼
   [ 1. Content-Addressed Storage (CAS) & SHA-256 Pre-Hash Manifest ]
                                 │
                                 ▼
   [ 2. FastMCP Typed Forensic Tool Server (67 Tools, shell=False) ]
                                 │
                                 ▼
   [ 3. Nebius Token Factory & NVIDIA Nemotron Dynamic Router ]
        ├── FAST:     nvidia/Nemotron-3.5-Lightning (Triage & proposals)
        ├── BALANCED: nvidia/Nemotron-3-Super       (Adaptive hypothesis loop)
        └── DEEP:     nvidia/Nemotron-3-Ultra-550B  (Root-cause & conflict arbitration)
                                 │
                                 ▼
   [ 4. Adaptive Hypothesis Engine & Falsification-First Loop ]
        ├── Competing Hypotheses Arbitration (Malicious vs Benign Admin)
        └── Persistent Investigation Ledger (Turns, inquiries, citations)
                                 │
                                 ▼
   [ 5. Deterministic Atomic Claim Validation Gate (RULE-PROC, RULE-NET, etc.) ]
        ├── VERIFIED          (Deterministically confirmed by evidence facts)
        ├── PARTIALLY_VERIFIED(Primary match, secondary pending)
        ├── UNVERIFIED        (Missing evidence proof)
        ├── CONTRADICTED      (Forensic facts directly refute model claim)
        └── BLOCKED           (Integrity or security policy rejection)
                                 │
                                 ▼
   [ 6. Attack Reconstruction Graph (Causal vs Temporal) & OCSF Normalization ]
                                 │
                                 ▼
   [ 7. Final CAS Verification & Ed25519 Digital Seal on Chain-of-Custody ]
                                 │
                                 ▼
   [ 8. Multi-Format Reporting (JSON, Markdown, Interactive Web Console) ]
```

---

## 5. The 15-Stage Autonomous Investigation Lifecycle

Managed deterministically by `AxiomOrchestrator` (`src/axiom_dfir/orchestrator.py`), each stage enforces explicit inputs, outputs, and resumable state persistence:

1. `CASE_INITIALIZATION`: Sets up workspace context, validates paths, and loads configuration.
2. `EVIDENCE_INGESTION`: Discovers, categorizes, sizes, and catalogs artifacts into `evidence_manifest.json`.
3. `INTEGRITY_VALIDATION`: Registers baseline SHA256 cryptographic fingerprints before any tool executes.
4. `ARTIFACT_DISCOVERY`: Identifies available forensic surfaces (memory, MFT, Prefetch, EVTX, Amcache).
5. `INITIAL_TRIAGE`: Fast profile reasoning proposing primary investigation leads.
6. `INVESTIGATION_PLANNING`: Selects optimal tools from the 67-tool FastMCP catalog.
7. `FORENSIC_TOOL_EXECUTION`: Executes tools in parallel via safe Python adapters (`shell=False`, strict allowlist).
8. `EVIDENCE_CORRELATION`: Extracts facts into indexed `TypedEvidenceDB`.
9. `AI_HYPOTHESIS_ANALYSIS`: Dispatches deep correlation to **Nemotron 3 Ultra 550B**.
10. `CLAIM_VALIDATION`: **Central Invariant.** Mathematically checks every claimed PID, PPID, IP, and hash.
11. `ATTACK_TIMELINE_CONSTRUCTION`: Normalizes timestamps into a chronological incident timeline.
12. `RISK_ASSESSMENT`: Calculates objective severity and blast radius based solely on verified facts.
13. `REPORT_GENERATION`: Generates comprehensive reports in JSON, Markdown, and standalone HTML.
14. `FINAL_INTEGRITY_CHECK`: Re-computes SHA256 hashes of all evidence. Halts immediately on mismatch.
15. `CASE_COMPLETION`: Packages artifacts, logs cryptographic audit seal, and marks case complete.

---

## 6. Nebius Token Factory & NVIDIA Nemotron Integration

AXIOM DFIR interfaces with **Nebius Token Factory** (`https://api.tokenfactory.nebius.com/v1/`) via its OpenAI-compatible endpoint.

### Intelligent 3-Tier Model Router
```python
from axiom_dfir.nebius import NebiusModelRouter

router = NebiusModelRouter()
# Automatically selects model based on task complexity:
model_id, profile = router.route_task("inv1_triage")           # -> nvidia/Nemotron-3.5-Lightning (FAST)
model_id, profile = router.route_task("react_cross_check")     # -> nvidia/Nemotron-3-Super (BALANCED)
model_id, profile = router.route_task("root_cause_analysis")   # -> nvidia/Nemotron-3-Ultra-550B (DEEP)
```

### Telemetry & Cost Accounting
Every request tracks prompt tokens, completion tokens, cached tokens, request latency, and estimated USD cost based on official published rates.

---

## 7. Deterministic Claim Validation Engine

AI models are never allowed to confirm security findings directly. A dedicated validator decomposes findings into testable claims:

```json
{
  "finding_id": "FIND-001",
  "title": "Reverse Shell Execution via PowerShell",
  "claims": {
    "pid": 4120,
    "process": "powershell.exe",
    "parent_pid": 1024,
    "destination_ip": "192.168.1.50",
    "destination_port": 4444
  },
  "evidence_refs": ["EV-001", "EV-002"],
  "validation_status": "VERIFIED",
  "confidence": 0.95
}
```

If the model claims an incorrect parent PID (e.g. PPID 999 instead of 1024), the finding is tagged **`CONTRADICTED`** and confidence is clamped to **0.0%**. Missing evidence results in an **`UNVERIFIED`** status.

---

## 8. Empirical Benchmark Evaluation

Scientific evaluation performed via `scripts/evaluate_axiom.py` across labeled ground-truth scenarios:

| Metric | Unvalidated LLM Baseline | AXIOM DFIR (Hybrid System) | Improvement |
|---|---|---|---|
| **Finding Precision** | 40.0% | **100.0%** | **+60.0%** |
| **Finding Recall** | 100.0% | **100.0%** | Maintained |
| **False Positive Rate (FPR)** | 100.0% | **0.0%** | **-100.0% (Zero False Alarms)** |
| **Hallucination Rejection** | 0.0% (Unchecked) | **100.0% (Blocked)** | Complete Elimination |
| **Avg. Claim Check Latency** | N/A | **< 0.1 ms** | Real-time |

---

## 9. Quick Start & Execution

### Step 1: Clone & Configure Environment
```bash
git clone https://github.com/your-org/axiom-dfir.git
cd axiom-dfir

# Copy environment template
cp .env.example .env
```

Edit `.env` and configure your Nebius credentials:
```env
NEBIUS_API_KEY=your_token_factory_api_key_here
NEBIUS_BASE_URL=https://api.tokenfactory.nebius.com/v1/
AXIOM_FAST_MODEL=nvidia/Nemotron-3.5-Lightning
AXIOM_BALANCED_MODEL=nvidia/Nemotron-3-Super
AXIOM_DEEP_MODEL=nvidia/Nemotron-3-Ultra-550B
```

### Step 2: Install Dependencies
```bash
python -m pip install -r requirements.txt
python -m pip install -e .
```

### Step 3: Verify Nebius Connectivity Smoke Test
```bash
python axiom.py verify-nebius
```
Expected output:
```
Testing Nebius Token Factory & NVIDIA Nemotron Connectivity...
[PASS] Successfully connected to Nebius Token Factory!
  Model  : nvidia/Nemotron-3.5-Lightning
  Latency: 0.245s
  Reply  : 'AXIOM-NEBIUS-OK'
```

### Step 4: Run an Autonomous Investigation
```bash
# Point AXIOM DFIR at an evidence directory or forensic image:
python axiom.py run /path/to/evidence --case-id INCIDENT-2026-001
```

### Step 5: Launch the Interactive Web Console & REST API
You can launch the complete React/Vite web console and FastAPI REST backend using either:

**One-Click Launch (Windows PowerShell)**:
```powershell
./run_app.ps1
```

**Standard Python Command**:
```bash
python run_web.py --port 8000
```
Then open:
- **Web Console**: `http://127.0.0.1:8000` (10 dedicated forensic investigation views)
- **Interactive Swagger Docs**: `http://127.0.0.1:8000/docs`
- **ReDoc Documentation**: `http://127.0.0.1:8000/redoc`

The 10 integrated views in the dark cybersecurity console include:
1. **Overview Dashboard**: Real-time KPI metrics, active case snapshot, verification stats, invariant hero banner.
2. **Case Management**: Create case form, multi-case switcher, stage progression indicators.
3. **Evidence Explorer**: Content-Addressed Storage inventory, SHA-256 digests with copy button, read-only proof badges.
4. **Investigation Workspace**: 15-stage pipeline stepper, stage advance and full execution controls, live log stream.
5. **Hypothesis Ledger**: Falsification-first tracking, confidence meters, competing resolution audits.
6. **Finding Verification**: Canonical status filters (`VERIFIED`, `CONTRADICTED`, etc.), atomic claims tab, Finding Drill-Down modal.
7. **Attack Relationship Graph**: Directed entity relationship topology (Processes, Network Sockets, Identities, Files), visual distinction between `CAUSAL` and `TEMPORAL` edges, interactive entity inspector panel, JSON export.
8. **Investigation Timeline**: Chronological event stream, timestamp sorting, category filters, MITRE ATT&CK technique tags, CSV export.
9. **Model Observatory**: Nebius Token Factory connection status, active model profiles (`FAST`, `BALANCED`, `DEEP`), routing decisions log, token telemetry.
10. **Investigation Reports**: Multi-format downloads (HTML, Markdown, JSON), live in-browser previews, ISO/IEC 27037 Ed25519 digital seal details.

### Step 6: Run Automated Tests
```bash
pytest tests/test_axiom_*.py tests/test_tools/test_*.py -v
```
*(309 tests passing, 0 failing, 7 skipped)*

### Step 7: Run Multi-Baseline Scientific Benchmark
```bash
python scripts/evaluate_axiom.py
```

---

## 9. Scientific Evaluation & Multi-Baseline Benchmark

AXIOM DFIR was empirically benchmarked against three baseline architectures across Canonical, Holdout (Dual-Use Administration), and Adversarial (PPID Spoofing, Ghost PIDs, Fabricated C2) intrusion scenarios. Full details are recorded in [`BENCHMARK_REPORT.md`](BENCHMARK_REPORT.md).

| Architecture / System | Finding Precision | Finding Recall | False Positive Rate | Security F1 Score | Hallucination Rate | Avg Verification Latency | Case Cost |
|---|---|---|---|---|---|---|---|
| **Baseline A: Rules-Only** (Static Heuristics) | 66.7% | 66.7% | 20.0% | 0.667 | N/A | **1.2 ms** | **\$0.00** |
| **Baseline B: Single Nemotron** (Prompt-Only) | 37.5% | **100.0%** | 100.0% | 0.545 | 62.5% | 145.0 ms | \$0.00180 |
| **Baseline C: Multi-Model Unverified** | 37.5% | **100.0%** | 100.0% | 0.545 | 62.5% | 210.0 ms | \$0.00240 |
| **System D: AXIOM DFIR (Full Platform)** | **100.0%** | **100.0%** | **0.0%** | **1.000** | **0.0% (ELIMINATED)** | **< 1.0 ms** | **\$0.00120** |

### Key Scientific Conclusions:
1. **Zero Hallucination Tolerance**: Unvalidated LLMs generated a 62.5% hallucination rate on forensic questions. AXIOM DFIR's deterministic claim validation gate reduced the hallucination rate to exactly **0.0%**.
2. **Adversarial Resilience**: In adversarial PPID spoofing tests, AXIOM DFIR caught contradictory evidence in memory tables and marked the claim `CONTRADICTED`.
3. **Dual-Use Disambiguation**: In administrative LOLBin tests, AXIOM DFIR's adaptive hypothesis engine evaluated competing hypotheses, preventing false positive incident alerts.

---

## 10. Repository Structure

```
Axiom DFIR/
├── axiom.py                   # Primary CLI Command Center
├── run_web.py                 # Interactive Web Console & REST API Server
├── pyproject.toml             # Python build configuration and dependencies
├── requirements.txt           # Frozen environment dependencies
├── .env.example               # Configuration template for Nebius Token Factory
├── BENCHMARK_REPORT.md        # Complete empirical multi-baseline evaluation report
├── benchmark_results.json     # Machine-readable scientific benchmark metrics
├── benchmark_comparison.csv   # Metric comparison spreadsheet
├── PHASE_II_CHANGELOG.md      # Comprehensive Phase II release log
├── ARCHITECTURE.md            # In-depth system design & Mermaid diagrams
├── SECURITY.md                # Security policy, boundaries, and controls
├── THREAT_MODEL.md            # STRIDE threat model & attack surface analysis
├── LIMITATIONS.md             # Technical boundaries & honest disclosures
├── PROVENANCE.md              # Code lineage and upstream attribution record
├── THIRD_PARTY_NOTICES.md     # Third-party licenses and notices
├── HACKATHON_UPDATE.md        # Detailed record of hackathon engineering
├── src/
│   ├── axiom_dfir/            # Core AXIOM Python distribution
│   │   ├── cas.py             # Content-Addressed Storage (streaming 64KB SHA-256)
│   │   ├── chain_of_custody.py# Hash-chained audit ledger & Ed25519 digital seal
│   │   ├── hypothesis.py      # Structured hypotheses & falsification-first ledger
│   │   ├── investigation_loop.py # Bounded adaptive investigative engine
│   │   ├── atomic_claims.py   # Atomic claim models & deterministic rule registry
│   │   ├── ocsf.py            # OCSF v1.1.0 security event normalization layer
│   │   ├── threat_intel.py    # Optional Tavily threat intelligence enrichment
│   │   ├── intake.py          # Evidence Intake Engine & Manifest generator
│   │   ├── integrity.py       # Dual-point SHA256 integrity validator & circuit breaker
│   │   ├── nebius.py          # Nebius Token Factory client & dynamic model router
│   │   ├── orchestrator.py    # 15-stage autonomous investigation state machine
│   │   ├── validation.py      # Deterministic claim validation engine
│   │   ├── correlation.py     # Directed attack relationship graph & timeline
│   │   ├── reporting.py       # Multi-format report generator (JSON, MD, HTML)
│   │   ├── security.py        # Untrusted evidence fencer & safe subprocess runner
│   │   └── web.py             # HTTP dashboard server & REST API
│   ├── server.py              # FastMCP forensic server (67 typed tools)
│   └── sift_sentinel/         # Preserved upstream forensic analysis libraries
├── scripts/
│   ├── nebius_smoke.py        # Nebius Token Factory connectivity smoke test
│   └── evaluate_axiom.py      # Scientific benchmark evaluation suite
└── tests/
    ├── test_axiom_cas.py              # Content-addressed storage unit tests
    ├── test_axiom_chain_of_custody.py # Hash-chained ledger & Ed25519 tests
    ├── test_axiom_hypothesis.py       # Adaptive hypothesis engine tests
    ├── test_axiom_investigation_loop.py # Bounded investigation cycle tests
    ├── test_axiom_atomic_claims.py    # Atomic claim validation tests
    ├── test_axiom_ocsf.py             # OCSF event normalization tests
    ├── test_axiom_threat_intel.py     # External threat intelligence isolation tests
    ├── test_axiom_integrity.py        # Evidence integrity & spoliation tests
    ├── test_axiom_validation.py       # Claim validation & anti-hallucination tests
    ├── test_axiom_security.py         # Subprocess allowlist & prompt injection tests
    ├── test_axiom_nebius.py           # Nebius client & model router tests
    └── test_axiom_orchestrator.py     # 15-stage state machine tests
```

---

## 11. Provenance, Licensing & Attribution

- **Base Project Origin**: AXIOM DFIR evolves and modernizes the open-source architecture originally developed in `Sentinel-Ensemble-Qwen` by **Adil Eskintan / Solvent CyberSecurity LLC**.
- **License**: Released under the permissive **MIT License** (`LICENSE`).
- **Third-Party Notices**: See [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) and [`PROVENANCE.md`](PROVENANCE.md) for full attribution.
- **Hackathon Update**: Detailed breakdown of new components engineered specifically for the Nebius x NVIDIA Hackathon 2026 is documented in [`HACKATHON_UPDATE.md`](HACKATHON_UPDATE.md).

