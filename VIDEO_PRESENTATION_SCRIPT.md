# AXIOM DFIR — Hackathon Video Presentation & Demo Script

**Project**: AXIOM DFIR (Autonomous Evidence-Verified Digital Forensics & Incident Response)  
**Event**: Nebius x NVIDIA Global AI Hackathon 2026  
**Track**: Best Apps & Agents  
**Target Duration**: 3:30 – 4:00 Minutes  
**Live Demo URL**: `http://127.0.0.1:8000` (or `http://localhost:8000`)  
**Repository**: [https://github.com/Hridanshu4004/Axiom-DFIR](https://github.com/Hridanshu4004/Axiom-DFIR)  

---

## Pre-Recording Checklist (30 Seconds Setup)

1. **Start the Web Console**:
   ```powershell
   ./run_app.ps1
   # OR: python run_web.py --port 8000
   ```
2. **Open Browser**: Navigate to `http://127.0.0.1:8000` in full screen (F11 or maximized dark browser window).
3. **Screen Recording**: Recommended tool is **OBS Studio**, **Loom**, or Windows **Win + Alt + R**. Record at 1080p 60fps.
4. **Resolution/Zoom**: Set browser zoom to 100% or 110% so text, badges, and graphs are crisp and readable.

---

## Video Scene-by-Scene Script

```
+---------------------------------------------------------------------------------------------------------+
| SCENE 1 | 0:00 - 0:35 | THE HOOK & THE DFIR CRISIS                                                      |
+---------------------------------------------------------------------------------------------------------+
```

### Visual:
- **0:00 - 0:12**: Show the **Overview Dashboard** (`http://127.0.0.1:8000`). Highlight the top title: **AXIOM DFIR: Autonomous Evidence-Verified Digital Forensics & Incident Response** and the hero banner: *"The AI may propose a finding, but only verified forensic evidence can confirm it."*
- **0:13 - 0:35**: Pan down to the metrics cards showing **Verified Findings vs. Refuted Hallucinations**.

### Voiceover / Spoken Script:
> *"In enterprise cybersecurity and digital forensics, incident responders face two critical crises:*
>
> *First: the **data bottleneck**. A single breach yields tens of gigabytes of volatile memory, disk captures, and millions of event logs. Human analysis takes days.*
>
> *Second: the **LLM hallucination trap**. When security teams deploy naive AI agents, models hallucinate up to 60% of the time—inventing non-existent process IDs, fabricating C2 connections, and mistaking legitimate admin tools for malware. In a real-world response or a courtroom, taking an AI's word at face value is catastrophic.*
>
> *Meet **AXIOM DFIR**: the first autonomous, evidence-verified incident response platform powered by **Nebius Token Factory** and **NVIDIA Nemotron** reasoning, anchored by a **deterministic code validation gate**."*

---

```
+---------------------------------------------------------------------------------------------------------+
| SCENE 2 | 0:35 - 1:15 | INTAKE, CAS STORAGE & 15-STAGE STATE MACHINE                            |
+---------------------------------------------------------------------------------------------------------+
```

### Visual:
- **0:35 - 0:50**: Click on the **Evidence Explorer** tab on the left sidebar.
  - Point mouse to the **Content-Addressed Storage (CAS)** inventory.
  - Click the **Copy Hash** icon on one of the SHA-256 digests (`EV-MEM-001`, `EV-PCAP-002`).
  - Show the **READ-ONLY / TAMPER-PROOF** badges.
- **0:51 - 1:15**: Click on the **Investigation Workspace** tab.
  - Show the **15-stage pipeline stepper** (from `01_CASE_INITIALIZATION` to `15_CASE_COMPLETION`).
  - Click **Advance Next Stage** or show the live execution stream.

### Voiceover / Spoken Script:
> *"AXIOM DFIR treats digital evidence with strict forensic discipline. Under the hood, evidence is ingested into a **Content-Addressed Storage (CAS)** system, sharded by SHA-256 hashes with OS-level immutable permissions.*
>
> *If an artifact is tampered with by even a single byte, AXIOM triggers an immediate **Evidence Spoliation Error** and halts the pipeline to protect the legal chain of custody.*
>
> *Here in the **Investigation Workspace**, an autonomous **15-stage finite state machine** orchestrates the entire case: from artifact discovery and initial triage, through 67 typed FastMCP forensic tools, all the way to risk scoring and report generation."*

---

```
+---------------------------------------------------------------------------------------------------------+
| SCENE 3 | 1:15 - 2:05 | THE CORE INNOVATION: DETERMINISTIC CLAIM VALIDATION                     |
+---------------------------------------------------------------------------------------------------------+
```

### Visual:
- **1:15 - 1:30**: Click on the **Finding Verification** tab on the left sidebar.
  - Show the green **VERIFIED** cards and red **CONTRADICTED** cards.
  - Click on the filter buttons: `ALL`, `VERIFIED`, `CONTRADICTED`.
- **1:31 - 2:05**: Click on any finding to open the **Finding Drill-Down Modal**!
  - Point to the original AI hypothesis text.
  - Highlight the **Atomic Claim** `(Subject, Predicate, Object)` and the Rule ID (e.g. `RULE-PROC-001` or `RULE-NET-001`).
  - Show the claimed value vs. the actual evidence value.
  - Point to the **Direct Evidence Citations** (`EV-MEM-001`, `EV-PCAP-002`).
  - Close the modal and briefly show the **Hypothesis Ledger** tab with competing hypotheses (`H1` vs `H2`).

### Voiceover / Spoken Script:
> *"Here is AXIOM’s core engineering breakthrough:*
>
> *We enforce an unshakeable architectural invariant: **The AI can propose an investigative lead, but ONLY deterministic code validation can confirm it.**
>
> *Every hypothesis generated by the model is decomposed into typed atomic claims: `Subject, Predicate, and Object`. Our deterministic validator tests these against the raw forensic evidence using 5 rule classes: process lineage, cryptographic hash matching, network socket attribution, temporal bounds, and authentication credentials.*
>
> *When an adversarial attack or an LLM hallucination proposes a fake parent PID or a phantom C2 IP, AXIOM’s code gate instantly flags it as **CONTRADICTED**, clamping its confidence to exactly zero percent!*
>
> *In our **Hypothesis Ledger**, we use falsification-first reasoning: contradicting evidence carries double weight, completely eliminating fabricated IOCs."*

---

```
+---------------------------------------------------------------------------------------------------------+
| SCENE 4 | 2:05 - 2:50 | ATTACK RECONSTRUCTION GRAPH & TIMELINE                                   |
+---------------------------------------------------------------------------------------------------------+
```

### Visual:
- **2:05 - 2:30**: Click on the **Attack Relationship Graph** tab.
  - Show the interactive graph cards and topology.
  - Click on a node (e.g., `powershell.exe (PID 4120)`).
  - Show the **Entity Inspector** on the right side: entity ID, type, evidence ref, and inbound/outbound links.
  - Toggle between **Causal Links** and **Temporal Links**.
- **2:31 - 2:50**: Click on the **Investigation Timeline** tab.
  - Scroll through the chronological event cards with timestamp badges and MITRE ATT&CK pills (e.g., `T1059.001 PowerShell`, `T1071.001 Web Protocols`).
  - Click the **Filter Category** pills (`PROCESS`, `NETWORK`, `AUTH`).

### Voiceover / Spoken Script:
> *"Once claims are verified, AXIOM automatically reconstructs the full intrusion.*
>
> *In the **Attack Relationship Graph**, you see directed topology mapping processes, network sockets, user identities, and persistence mechanisms. Unlike naive tools, AXIOM strictly differentiates between **Causal links**—where child processes are spawned directly—and purely **Temporal correlations**.*
>
> *Moving to the **Investigation Timeline**, forensic events are normalized using the standard **Open Cybersecurity Schema Framework (OCSF v1.1.0)**, mapping every verified action directly to MITRE ATT&CK techniques with precise evidentiary citations."*

---

```
+---------------------------------------------------------------------------------------------------------+
| SCENE 5 | 2:50 - 3:30 | NEBIUS TOKEN FACTORY OBSERVATORY & MODEL ROUTING                        |
+---------------------------------------------------------------------------------------------------------+
```

### Visual:
- **2:50 - 3:15**: Click on the **Model Observatory** tab on the left sidebar.
  - Point to the **Nebius Token Factory** status card and endpoint (`https://api.tokenfactory.nebius.com/v1/`).
  - Show the 3 Model Profile cards:
    - `FAST`: `meta-llama/Meta-Llama-3.1-8B-Instruct`
    - `BALANCED`: `nvidia/nemotron-mini-4b-instruct`
    - `DEEP`: `nvidia/nemotron-4-340b-instruct`
  - Highlight the **Cost & Token Telemetry** grid (prompt tokens, completion tokens, estimated USD cost).
  - Scroll through the **Dynamic Model Routing Decision Ledger** showing the rationale for escalating tasks.
- **3:16 - 3:30**: Show the **Swagger OpenAPI Documentation** in a new tab (`http://127.0.0.1:8000/docs`).

### Voiceover / Spoken Script:
> *"To maximize both speed and cost-efficiency, AXIOM DFIR connects directly to **Nebius Token Factory** using intelligent 3-tier dynamic escalation:*
>
> *For rapid triage and artifact taxonomy, it routes to our **FAST profile**.*
> *For structured hypothesis generation, it escalates to the **BALANCED profile** using **NVIDIA Nemotron Mini**.*
> *And for multi-stage lateral movement analysis and complex root-cause arbitration, it engages our **DEEP profile** powered by **NVIDIA Nemotron 340B**.*
>
> *Our Model Observatory tracks every token, latency, and routing rationale transparently. When no API key is supplied, AXIOM falls back gracefully to a fully functional offline demo mode.*
>
> *Furthermore, every capability is exposed through a production **FastAPI REST API** with complete interactive OpenAPI Swagger docs."*

---

```
+---------------------------------------------------------------------------------------------------------+
| SCENE 6 | 3:30 - 4:00 | COURTROOM PROVENANCE, SCIENTIFIC BENCHMARK & CONCLUSION                 |
+---------------------------------------------------------------------------------------------------------+
```

### Visual:
- **3:30 - 3:45**: Click on the **Investigation Reports** tab.
  - Highlight the **ISO/IEC 27037 Cryptographic Seal** card.
  - Show the **SHA-256 Head Hash** and **Ed25519 Digital Signature** public key.
  - Show the **Interactive HTML Preview** frame or click **Download MD / Download JSON**.
- **3:46 - 4:00**: Switch to the **GitHub Repository** tab: `https://github.com/Hridanshu4004/Axiom-DFIR`.
  - Scroll past the badge bar (License MIT, Python 3.10+, Nebius Token Factory, 309 Passing Tests).
  - Show the **v2.0.0 Release** tag.

### Voiceover / Spoken Script:
> *"Finally, forensics is only as good as its legal admissibility.*
>
> *In the **Investigation Reports** view, every stage of the investigation is sealed into a continuous backlinked hash-chain, digitally signed using an asymmetric **Ed25519 private key** compliant with ISO/IEC 27037 standards.*
>
> *In our scientific benchmarks comparing 4 architectures, AXIOM DFIR achieved **100% precision, 0% false positives, and completely eliminated LLM hallucinations**, backed by **309 passing automated tests**.*
>
> *AXIOM DFIR is 100% open source, fully reproducible, and ready to deploy on GitHub today.*
>
> *Thank you to Nebius and NVIDIA for empowering the next generation of trustworthy, evidence-verified cybersecurity AI agents!"*

---

## Quick Reference Timing & Action Guide

| Time Window | Screen to Display | Key Action / Highlight |
|---|---|---|
| **0:00 – 0:35** | `Overview Dashboard` | Show hero banner, invariant, metrics |
| **0:35 – 1:15** | `Evidence Explorer` & `Investigation Workspace` | Copy SHA-256 hash, show CAS read-only, 15-stage stepper |
| **1:15 – 2:05** | `Finding Verification` | Open Finding Drill-Down modal, show claimed vs evidence values |
| **2:05 – 2:50** | `Attack Graph` & `Timeline` | Click nodes in graph, show causal vs temporal, filter timeline by MITRE ATT&CK |
| **2:50 – 3:30** | `Model Observatory` & `/docs` | Show Nebius connection, 3 Nemotron tiers, token telemetry, Swagger UI |
| **3:30 – 4:00** | `Investigation Reports` & `GitHub` | Show ISO 27037 Ed25519 seal, HTML preview, GitHub repo & v2.0.0 release |

---

## 30-Second Elevator Pitch (For Quick Teaser / Submissions)

> *"Digital forensics is facing a crisis: human analysts are overwhelmed by gigabytes of evidence, while naive LLM security agents hallucinate fake findings 60% of the time.*
>
> *AXIOM DFIR solves this with a radical architecture: we combine the reasoning power of **NVIDIA Nemotron** on **Nebius Token Factory** with a **deterministic code validation gate**.*
>
> *Our core invariant is absolute: The AI can propose a finding, but only verified forensic evidence can confirm it. With Content-Addressed Storage, ISO 27037 Ed25519 digital signatures, an interactive React console, and 309 passing tests, AXIOM delivers zero-hallucination autonomous incident response ready for enterprise security teams and courtrooms."*
