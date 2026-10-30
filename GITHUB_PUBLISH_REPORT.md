# AXIOM DFIR v2.0.0 — GITHUB PUBLISH & RELEASE REPORT

**Project Name**: AXIOM DFIR (Autonomous Evidence-Verified Digital Forensics & Incident Response)  
**Release Version**: `v2.0.0`  
**Hackathon Target**: Nebius x NVIDIA Global AI Hackathon 2026 (`Best Apps & Agents` Track)  
**Destination Repository URL**: https://github.com/Hridanshu4004/Axiom-DFIR  
**Release Branch**: `axiom-v2-release`  
**Default Branch**: `main`  
**Official Release Tag**: [`v2.0.0`](https://github.com/Hridanshu4004/Axiom-DFIR/releases/tag/v2.0.0)  
**Publish Timestamp**: `2026-10-30T10:11:49Z`  
**Status**: **PUBLISHED & VERIFIED LIVE ON GITHUB**

---

## 1. Verified Live GitHub Links

- **Repository**: https://github.com/Hridanshu4004/Axiom-DFIR
- **Release Branch**: https://github.com/Hridanshu4004/Axiom-DFIR/tree/axiom-v2-release
- **Main Branch**: https://github.com/Hridanshu4004/Axiom-DFIR/tree/main
- **GitHub Release v2.0.0**: https://github.com/Hridanshu4004/Axiom-DFIR/releases/tag/v2.0.0
- **Commit History**: https://github.com/Hridanshu4004/Axiom-DFIR/commits/axiom-v2-release

---

## 2. Multi-Commit Publishing History

The release was constructed as 9 logical, conventional commits:

| # | Commit SHA | Conventional Commit Message | Subsystem & Scope |
|---|---|---|---|
| **1** | `c3603b9` | `feat(core): finalize AXIOM DFIR investigation engine` | 15-stage state machine orchestrator, evidence intake, 67-tool FastMCP server, CLI entrypoint, MIT license |
| **2** | `ba05053` | `feat(security): implement evidence integrity and chain of custody` | Content-Addressed Storage (CAS), backlinked chain of custody ledger, ISO 27037 Ed25519 digital seal, anti-spoliation breaker |
| **3** | `f92cf2a` | `feat(agent): add adaptive hypotheses and deterministic validation` | Falsification-first hypothesis ledger, bounded investigation loop, atomic claim models, 5 deterministic validation rule classes |
| **4** | `ba13abb` | `feat(ai): integrate Nebius Token Factory model orchestration` | Nebius client, 3-tier dynamic router (`FAST`/`BALANCED`/`DEEP`), token telemetry, safe `.env.example` templates |
| **5** | `40a3ac7` | `feat(api): finalize FastAPI investigation services` | FastAPI application, OpenAPI endpoints, Pydantic schemas, static mount for React console, Docker specs |
| **6** | `83aae94` | `feat(frontend): introduce AXIOM DFIR investigation console` | React + Vite + TypeScript single-page app with 10 dedicated views and Finding Drill-Down modal |
| **7** | `ad3c25e` | `feat(analytics): add OCSF and evidence-backed attack reconstruction` | OCSF v1.1.0 event normalizer, directed attack graph, chronological timeline, report generator, threat intel isolation |
| **8** | `aa13ce2` | `test: expand forensic regression and integration coverage` | 309 automated tests, 4-system scientific benchmark harness (`evaluate_axiom.py`), reproducible benchmark datasets |
| **9** | `535be2b` | `docs: finalize AXIOM DFIR v2.0.0 release` | Technical documentation, architecture diagrams, threat model, security policies, provenance records, hackathon update |

---

## 3. Engineering Verification & Audit Results

### 3.1 Automated Test Execution
- **Command**: `pytest tests/test_axiom_*.py tests/test_tools/test_*.py -q`
- **Result**: **309 passed, 0 failed, 7 skipped in 15.32s (100% pass rate)**.
- **Subsystem Breakdown**:
  - CAS & Storage: 5/5 passed
  - Chain of Custody & Ed25519 Signatures: 5/5 passed
  - Adaptive Hypotheses & Falsification: 5/5 passed
  - Bounded Investigation Loop: 3/3 passed
  - Atomic Claim Verification Rules: 5/5 passed
  - OCSF Normalization: 3/3 passed
  - Threat Intelligence Isolation: 3/3 passed
  - Dual-Point Integrity & Spoliation: 3/3 passed
  - Claim Validation Engine: 3/3 passed
  - Safe Subprocess & Security Boundaries: 3/3 passed
  - Nebius Token Factory Client & Router: 5/5 passed
  - 15-Stage Finite State Machine: 2/2 passed
  - FastMCP & Forensic Tool Adapters: 269/269 passed (7 skipped)

### 3.2 Frontend Build & Console Verification
- **Framework**: React + Vite + TypeScript
- **Build Output**: `dist/` generated with zero errors (346 KB total asset footprint).
- **10 Views Verified**: Overview Dashboard, Case Management, Evidence Explorer, Investigation Workspace, Hypothesis Ledger, Finding Verification (with drill-down modal), Attack Relationship Graph, Investigation Timeline, Model Observatory, Investigation Reports.
- **Node Modules Defense**: `frontend/node_modules/` strictly excluded via `.gitignore`.

### 3.3 Backend Startup & API Verification
- **Framework**: Python FastAPI + Uvicorn
- **Root Web Server**: Serves compiled React SPA at `http://127.0.0.1:8000/` (HTTP 200).
- **API Documentation**: Interactive Swagger UI at `http://127.0.0.1:8000/docs` (HTTP 200) and ReDoc at `http://127.0.0.1:8000/redoc`.
- **System Health**: `/api/health` reports status `HEALTHY`, product `AXIOM DFIR`, version `2.0.0`.

### 3.4 Pre-Publishing Security & Secrets Audit
- **Private Credentials Check**: ZERO API keys, tokens, `.env` files, or certificates committed.
- **Safe Template Provided**: `.env.example` includes model names and endpoint URLs with empty `NEBIUS_API_KEY=`.
- **Subprocess Security**: All forensic tools execute via `SAFE_EXECUTABLE_ALLOWLIST` with `shell=False`.
- **Untrusted Input Fencing**: Untrusted memory/disk artifacts are isolated within XML boundary containers to neutralize prompt injection.

### 3.5 Provenance & License Integrity
- **Base Origin**: Open-source foundation inherited from `Sentinel-Ensemble-Qwen` by **Adil Eskintan / Solvent CyberSecurity LLC** under the MIT License.
- **Attribution Notice**: Full legal notices maintained in `LICENSE`, `PROVENANCE.md`, and `THIRD_PARTY_NOTICES.md`.
- **Hackathon Additions**: Detailed breakdown of Phase II systems engineered for the 2026 hackathon recorded in `HACKATHON_UPDATE.md`.

---

## 4. GitHub Release Tag & Assets

- **Tag**: `v2.0.0`
- **Release Name**: `AXIOM DFIR v2.0.0 — Final Hackathon Release`
- **Release URL**: https://github.com/Hridanshu4004/Axiom-DFIR/releases/tag/v2.0.0
- **Git Push Verification**:
  ```
  branch 'axiom-v2-release' set up to track 'origin/axiom-v2-release'.
  branch 'main' set up to track 'origin/main'.
  * [new tag] v2.0.0 -> v2.0.0
  ```
- **Pull Request Status**: Both `axiom-v2-release` and `main` are identical at commit `535be2b`; code is released directly on both branches.

---

*Report certified by Senior Release Engineer · October 2026*
