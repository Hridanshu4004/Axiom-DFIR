# AXIOM DFIR: CHANGELOG & RELEASE HISTORY

All notable changes to the AXIOM DFIR platform are documented in this file.

---

## [1.0.0] - 2026-10-30 — Nebius x NVIDIA Global AI Hackathon Release

### Added
- **Nebius Token Factory & NVIDIA Nemotron Integration** (`axiom_dfir.nebius`):
  - High-performance OpenAI-compatible client interfacing with Nebius Token Factory endpoints (`https://api.tokenfactory.nebius.com/v1/`).
  - 3-tier intelligent model routing:
    - `FAST`: `nvidia/Nemotron-3.5-Lightning` (Log parsing, catalog proposals, initial triage).
    - `BALANCED`: `nvidia/Nemotron-3-Super` (ReAct cross-checks, correlation, self-correction).
    - `DEEP`: `nvidia/Nemotron-3-Ultra-550B` (Root-cause lateral movement analysis, conflicting evidence).
  - Bounded exponential backoff retry on HTTP 429 and 5xx errors.
  - Cumulative thread-safe telemetry and cost accounting ledger (`NebiusMetricsTracker`).
  - Live runtime connectivity smoke test (`scripts/nebius_smoke.py`, `axiom verify-nebius`).
- **15-Stage Finite State Machine Orchestrator** (`axiom_dfir.orchestrator`):
  - Deterministic progression through 15 formal stages.
  - Resumable state persistence via atomic JSON checkpointing (`investigation_state.json`).
  - Complete execution audit trail recording stage durations and inputs/outputs.
- **Evidence Intake Engine & Cryptographic Manifest** (`axiom_dfir.intake`):
  - Automatic discovery, sizing, and classification of forensic artifacts (EVTX, memory dumps, disk images, registry hives).
  - Generates immutable `evidence_manifest.json` with initial SHA256 hashes and tamper-evident seal.
- **Evidence Integrity Engine & Spoliation Circuit Breaker** (`axiom_dfir.integrity`):
  - Dual-point SHA256 cryptographic verification comparing intake hashes against final post-investigation hashes.
  - Immediate `EvidenceSpoliationError` halt if any evidence item is modified or deleted.
- **Deterministic Claim Validation Engine** (`axiom_dfir.validation`):
  - Canonical validation statuses: `VERIFIED`, `PARTIALLY_VERIFIED`, `UNVERIFIED`, `CONTRADICTED`, `BLOCKED`.
  - Deterministic evaluation of process PIDs, PPID relationships, socket connections, and file hashes against compiled ground truth.
  - Elimination of hallucinated AI claims.
- **Directed Incident Reconstruction Graph & Timeline** (`axiom_dfir.correlation`):
  - Directed graph linking processes, sockets, files, and users.
  - Chronologically sorted attack timeline with timezone-aware timestamp normalization.
  - Direct evidence attribution for MITRE ATT&CK techniques.
- **Multi-Format Investigative Reporting Engine** (`axiom_dfir.reporting`):
  - Emits JSON, Markdown, and rich interactive standalone HTML reports.
  - Strict visual and structural separation between verified facts and unverified AI hypotheses.
- **Interactive DFIR Web Console & REST API** (`axiom_dfir.web`):
  - Single-page application and HTTP server providing live dashboard, evidence explorer, timeline, process trees, and model cost telemetry.
  - Launchable via `python run_web.py` or `axiom web`.
- **Security Hardening & Threat Defense** (`axiom_dfir.security`):
  - Untrusted evidence XML container wrapping with prompt injection keyword detection.
  - Subprocess execution strictly using `shell=False` and `SAFE_EXECUTABLE_ALLOWLIST`.
  - Canonical path resolution guarding against directory traversal.
- **Unified Command-Line Interface** (`axiom.py`):
  - Branded entrypoint with subcommands: `verify-nebius`, `triage`, `run`, `demo`, `web`.
- **Scientific Evaluation & Benchmark Suite** (`scripts/evaluate_axiom.py`):
  - Measures precision, recall, FPR, FNR, latency, and hallucination rejection across ground-truth scenarios.

### Changed
- Complete product rebranding from legacy Sentinel-Ensemble-Qwen to **AXIOM DFIR: Autonomous Evidence-Verified Digital Forensics & Incident Response**.
- Default inference provider switched from Alibaba Cloud DashScope to **Nebius Token Factory**.
- Model pricing ledger updated with NVIDIA Nemotron rates.
- Packaged as first-class `axiom_dfir` Python distribution.

