# AXIOM DFIR: IMPLEMENTATION AUDIT & GAP ANALYSIS (PHASE II)

**Audit Date**: October 2026  
**Auditor**: Principal Software Architect & Lead Security Engineer  
**Scope**: Full Repository Audit (Source code, adapters, model clients, schemas, tests, UI, documentation)  
**Status Standard**:
- `IMPLEMENTED_AND_TESTED`
- `IMPLEMENTED_NOT_FULLY_TESTED`
- `PARTIALLY_IMPLEMENTED`
- `DOCUMENTATION_ONLY`
- `NOT_IMPLEMENTED`
- `BLOCKED`

---

## 1. Executive Summary

This audit evaluates the current state of AXIOM DFIR across its core subsystems. The repository has successfully established the primary architectural foundation: the 15-stage orchestrator, the Nebius Token Factory client, the FastMCP forensic server, cryptographic SHA256 intake/verification, and initial claim validation.

However, moving from a hackathon prototype to an **enterprise-grade, scientifically validated autonomous DFIR platform** requires addressing several architectural gaps:
1. **Dynamic Investigation**: The current orchestrator executes a linear tool pipeline rather than dynamically posing hypotheses, inspecting intermediate tool outputs, and generating follow-up investigation queries.
2. **Atomic Claim Representation**: Findings are currently validated as semi-structured dictionary blobs rather than formal (Subject, Predicate, Object) atomic claims with temporal scopes.
3. **Evidence Storage & Chain of Custody**: SHA256 digests are verified, but evidence is not yet managed through a content-addressed storage (CAS) abstraction with hash-chained tamper-evident event blocks.
4. **Scientific Benchmarking**: The initial benchmark demonstrated 100% precision on synthetic scenarios, but needs multi-baseline comparisons (Rules Only, Single Model, Multi-Model, Full AXIOM) and holdout evaluation against external APT datasets (e.g. Windows-APT 2025).
5. **Security Event Normalization**: Normalization does not yet conform to the industry-standard Open Cybersecurity Schema Framework (OCSF).
6. **Frontend Finding Drill-Down**: The dashboard displays live backend state, but needs deep interactive finding inspection exposing raw evidence citations, hypothesis lineage, and validation rule traces.

---

## 2. Granular Feature Implementation Matrix

| Feature / Subsystem | Relevant Source Files | Implementation Status | Associated Tests | Genuinely Exercised? | Works End-to-End? | Remaining Limitations | Recommended Phase II Improvement |
|---|---|---|---|---|---|---|---|
| **15-Stage State Machine Orchestrator** | `src/axiom_dfir/orchestrator.py` | `IMPLEMENTED_AND_TESTED` | `tests/test_axiom_orchestrator.py` | Yes | Yes | Linear progression; lacks dynamic re-planning based on open hypotheses. | Introduce adaptive investigation loop in Stages 6–9 with bounded iterations. |
| **Evidence Intake & Manifest** | `src/axiom_dfir/intake.py` | `IMPLEMENTED_AND_TESTED` | `tests/test_axiom_orchestrator.py` | Yes | Yes | Directly hashes input directory; lacks content-addressed storage (CAS) snapshots. | Implement CAS abstraction and Ed25519 manifest signing. |
| **Evidence Integrity & Spoliation Halt** | `src/axiom_dfir/integrity.py` | `IMPLEMENTED_AND_TESTED` | `tests/test_axiom_integrity.py` | Yes | Yes | Validates pre/post SHA256; audit trail is in-memory list rather than hash-chained ledger. | Implement Merkle/hash-chained chain-of-custody log. |
| **Deterministic Claim Validator** | `src/axiom_dfir/validation.py` | `IMPLEMENTED_AND_TESTED` | `tests/test_axiom_validation.py` | Yes | Yes | Evaluates basic PIDs, parent PIDs, sockets, hashes; lacks atomic (Subject, Predicate, Object) semantics. | Upgrade to atomic claim schema with explicit rule IDs and explainability outputs. |
| **Nebius Token Factory Client** | `src/axiom_dfir/nebius.py`, `src/sift_sentinel/llm_provider.py` | `IMPLEMENTED_AND_TESTED` | `tests/test_axiom_nebius.py`, `scripts/nebius_smoke.py` | Yes | Yes | Basic 3-tier routing; lacks escalation logic (FAST -> BALANCED -> DEEP) based on open conflicts. | Add dynamic escalation rules and live Token Factory catalog validation. |
| **Forensic Tool Registry (FastMCP)** | `src/server.py`, `src/sift_sentinel/tools/*` | `IMPLEMENTED_AND_TESTED` | `tests/test_server.py`, `tests/test_tool_catalog.py` | Yes | Yes | Requires `vol` binary on host to discover plugins at import time; fails when `vol` is absent on Windows. | Add static alias fallback when `vol` CLI is not present on host. |
| **Incident Graph & Timeline** | `src/axiom_dfir/correlation.py` | `IMPLEMENTED_NOT_FULLY_TESTED` | `tests/test_axiom_orchestrator.py` | Partially | Yes | Simple graph structure; does not formally separate temporal order from causal links. | Implement typed graph entities, provenance-carrying edges, and causality flags. |
| **OCSF Event Normalization** | N/A (None) | `NOT_IMPLEMENTED` | None | No | No | Raw tool records are mapped directly without OCSF schema standard. | Build `axiom_dfir.ocsf` mapping process, network, and auth events to OCSF classes. |
| **Scientific Benchmark Harness** | `scripts/evaluate_axiom.py` | `IMPLEMENTED_AND_TESTED` | Evaluates synthetic benchmark | Yes | Yes | Evaluates single synthetic scenario set; lacks multi-baseline comparisons A/B/C/D and APT datasets. | Build 4-system comparative benchmark and adversarial holdout evaluation. |
| **Interactive Web Console & REST API** | `src/axiom_dfir/web.py`, `run_web.py` | `IMPLEMENTED_AND_TESTED` | Manual inspection / HTTP polling | Yes | Yes | Displays overview and cards; lacks deep finding drill-down and node-click evidence inspector. | Add modal finding drill-down showing raw evidence excerpts and rule explanations. |
| **Security Hardening (Fencing & Allowlist)** | `src/axiom_dfir/security.py` | `IMPLEMENTED_AND_TESTED` | `tests/test_axiom_security.py` | Yes | Yes | Fences untrusted text and validates allowlist; lacks rate-limiting and memory allocation caps. | Add resource limit enforcement and robust symlink canonicalization. |
| **Tavily Threat Intelligence Enrichment** | N/A (None) | `NOT_IMPLEMENTED` | None | No | No | No public IOC enrichment layer currently exists. | Implement optional Tavily threat intelligence client for public IPs/hashes. |

---

## 3. Detailed Subsystem Audit Findings

### 3.1 Orchestration & Autonomy
- **Current State**: The 15 stages in `AxiomOrchestrator` execute sequentially. Stage 5 does initial triage, Stage 6 selects tools, Stage 7 runs tools, and Stage 9 generates hypotheses.
- **Limitation**: If Stage 9 generates a hypothesis that requires investigating an artifact not previously collected (e.g., suspicious PowerShell command references a scheduled task), the system cannot loop back to run `parse_scheduled_tasks_disk` to confirm or refute it.
- **Remedy**: Introduce an **Adaptive Investigation Loop** inside Stages 6–9 driven by an explicit `HypothesisLedger`.

### 3.2 Evidence Provenance & Cryptography
- **Current State**: `EvidenceIntegrityEngine` computes SHA256 hashes at Stage 2 and re-computes them at Stage 14.
- **Limitation**: Evidence files are accessed directly from their original location without an isolated working snapshot or content-addressed storage (CAS) abstraction. The audit log is a basic list of events.
- **Remedy**: Implement a Content-Addressed Storage (`CAS`) manager and a hash-chained (`previous_event_hash` -> `event_hash`) audit ledger.

### 3.3 Claim Validation & Explainability
- **Current State**: `ClaimValidationEngine` parses finding dictionaries and inspects known PIDs, parent PIDs, hashes, and sockets.
- **Limitation**: Validation verdicts are returned as coarse strings without detailed rule identifiers or structured explanations of why an assertion was accepted or refuted.
- **Remedy**: Refactor findings into atomic `(Subject, Predicate, Object)` claims with explicit rule attribution (`RULE-PID-EXISTS`, `RULE-PPID-RELATION`, `RULE-HASH-MATCH`).

### 3.4 Scientific Benchmarking
- **Current State**: `evaluate_axiom.py` evaluates 5 scenarios and compares raw LLM output against the AXIOM hybrid validator.
- **Limitation**: Lacks multi-baseline comparisons against deterministic-only rules, single-model agents, and multi-model agents without claim verification.
- **Remedy**: Expand the benchmark into a comprehensive harness with baseline comparisons A, B, C, D and adversarial stress tests.

---

## 4. Conclusion & Audit Sign-Off

The baseline system is stable, well-architected, and fully functional. The implementation audit is **COMPLETE**. The findings here directly inform the **Phase II Implementation Plan**.

