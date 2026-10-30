# AXIOM DFIR: CODE PROVENANCE & ATTRIBUTION RECORD

**Product Identity**: AXIOM DFIR (Autonomous Evidence-Verified Digital Forensics & Incident Response)  
**Hackathon**: Nebius x NVIDIA Global AI Hackathon 2026  
**Track**: Best Apps & Agents  
**Date**: October 2026  

---

## 1. Upstream Base Provenance

AXIOM DFIR builds upon and evolves the open-source forensic foundation established in the **Sentinel-Ensemble-Qwen** project:
- **Upstream Project**: Sentinel-Ensemble-Qwen (originally entered in the Qwen Global AI Hackathon 2026 and recognized with a Top 10 Honorable Mention among 8,465 participants).
- **Original Author & Copyright**: Copyright (c) 2026 Adil Eskintan / Solvent CyberSecurity LLC.
- **License**: MIT License (Permissive open-source license authorizing use, modification, distribution, and commercial sublicensing, subject to license notice preservation).
- **Upstream Repository**: `https://github.com/3sk1nt4n/Sentinel-Ensemble-Qwen`

---

## 2. Integrity & Preservation Compliance

In accordance with strict ethical engineering and open-source provenance standards:
1. **No Concealment**: Upstream authorship, commit traditions, and original copyright notices are fully honored and preserved in the repository root and `LICENSE`.
2. **Clear Boundaries**: There is zero fabrication of authorship or misrepresentation of external work as solely our own.
3. **Legitimate Evolution**: AXIOM DFIR represents a major, production-grade re-architecture replacing obsolete Alibaba Cloud/DashScope inference dependencies with a high-throughput **Nebius Token Factory** and **NVIDIA Nemotron** multi-tier reasoning pipeline, accompanied by a 15-stage deterministic state machine, an interactive web console, and enhanced anti-hallucination claim gates.

---

## 3. Subsystem Lineage Breakdown

| Subsystem / Module | Origin | Current Status in AXIOM DFIR |
|---|---|---|
| **Forensic Tool Registry (`src/server.py`, `src/sift_sentinel/tools/*`)** | Upstream Base (Solvent CyberSecurity LLC) | **Preserved & Hardened**: 67 typed forensic tools and FastMCP server preserved with safe subprocess boundaries (`shell=False`). |
| **Evidence DB & Fact Compilation (`src/sift_sentinel/analysis/*`)** | Upstream Base (Solvent CyberSecurity LLC) | **Preserved & Integrated**: Core memory and disk extractors retained for backward-compatible fact indexing. |
| **Nebius Token Factory Integration (`src/axiom_dfir/nebius.py`)** | **New Hackathon Work** | **Newly Engineered**: OpenAI-compatible client connecting to `api.tokenfactory.nebius.com/v1`, 3-tier Nemotron routing, retry logic, token ledger. |
| **Investigation Orchestrator (`src/axiom_dfir/orchestrator.py`)** | **New Hackathon Work** | **Newly Engineered**: Deterministic 15-stage finite state machine with resumable JSON checkpoints and explicit input/output contracts. |
| **Evidence Intake & Manifest (`src/axiom_dfir/intake.py`)** | **New Hackathon Work** | **Newly Engineered**: Automatic discovery, categorization, SHA256 pre-hashing, and immutable `evidence_manifest.json` generation. |
| **Cryptographic Integrity Engine (`src/axiom_dfir/integrity.py`)** | **New Hackathon Work** | **Newly Engineered**: Dual-point SHA256 integrity verification, tamper detection, and unbypassable `EvidenceSpoliationError` halt. |
| **Claim Validation Engine (`src/axiom_dfir/validation.py`)** | **New Hackathon Work** | **Newly Engineered**: Canonical validation statuses (`VERIFIED`, `PARTIALLY_VERIFIED`, `UNVERIFIED`, `CONTRADICTED`, `BLOCKED`), refuting hallucinations. |
| **Attack Correlation & Graph (`src/axiom_dfir/correlation.py`)** | **New Hackathon Work** | **Newly Engineered**: Directed evidence graph linking processes, sockets, files, and users to MITRE ATT&CK techniques. |
| **Multi-Format Report Generator (`src/axiom_dfir/reporting.py`)** | **New Hackathon Work** | **Newly Engineered**: Structured JSON, Markdown, and rich interactive HTML reporting separating verified facts from AI hypotheses. |
| **Security & Prompt Fencing (`src/axiom_dfir/security.py`)** | **New Hackathon Work** | **Newly Engineered**: Prompt injection defense fencing untrusted log texts, executable allowlists, traversal prevention. |
| **Interactive Web Console & API (`src/axiom_dfir/web.py`)** | **New Hackathon Work** | **Newly Engineered**: Real-time HTTP dashboard and REST API displaying case progress, evidence explorer, timeline, and cost metrics. |
| **Unified CLI Entrypoint (`axiom.py`)** | **New Hackathon Work** | **Newly Engineered**: Branded CLI command center (`verify-nebius`, `triage`, `run`, `demo`, `web`). |
| **Benchmark Evaluation Suite (`scripts/evaluate_axiom.py`)** | **New Hackathon Work** | **Newly Engineered**: Scientific validation measuring precision, recall, FPR, FNR, and latency across ground-truth scenarios. |

