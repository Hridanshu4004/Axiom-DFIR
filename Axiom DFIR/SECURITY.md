# AXIOM DFIR: SECURITY POLICY & CONTROLS

**Product**: AXIOM DFIR (Autonomous Evidence-Verified Digital Forensics & Incident Response)  
**Classification**: Defensive Cybersecurity & Digital Forensics System  
**Status**: Active Production Standard  

---

## 1. Security Philosophy

Because AXIOM DFIR operates in adversarial incident response contexts, security cannot be an afterthought. The system is designed under the assumption that:
1. **Evidence Is Hostile**: Forensic artifacts (event logs, memory dumps, PowerShell transcripts, filenames, registry keys) frequently contain malicious strings, evasion payloads, and prompt injection attempts crafted to subvert automated tools.
2. **AI Is Fallible**: Generative language models will hallucinate, conflate benign administrative scripts with attacks, or make confident false assertions unless checked by deterministic code.
3. **Chain of Custody Is Sacrosanct**: Tampering with or altering digital evidence destroys its admissibility in legal proceedings.

---

## 2. Core Security Controls

### 2.1 Cryptographic Evidence Immutability
- **Read-Only Ingestion**: All evidence volumes and image files are mounted and opened strictly with read-only flags (`rb`, `O_RDONLY`).
- **Dual-Point SHA256 Fingerprinting**: SHA256 digests are computed at intake (Stage 2) and re-verified at case completion (Stage 14).
- **Anti-Spoliation Circuit Breaker**: If any byte of an evidence item changes, an `EvidenceSpoliationError` halts execution immediately. Case status is marked `COMPROMISED`. No model reasoning is permitted to explain away a hash mismatch.

### 2.2 Subprocess & Tool Execution Boundaries
- **Zero Shell Access to Models**: The LLM never receives a raw shell or executes arbitrary bash/cmd scripts.
- **Strict Binary Allowlist**: Only tools explicitly defined in `SAFE_EXECUTABLE_ALLOWLIST` (e.g. `vol`, `yara`, `fls`) can be invoked. Any attempt to spawn unapproved executables (e.g. `sh`, `bash`, `cmd.exe`, `powershell.exe`) raises a `PermissionError`.
- **Enforced `shell=False`**: Subprocess calls use typed argument arrays.
- **Execution Timeouts**: Every subprocess execution is guarded by strict timeouts (default 60s) preventing denial-of-service via corrupted disk structures.

### 2.3 Prompt Injection Defense & Data Fencing
- **Untrusted Evidence Containers**: All raw text extracted from forensic artifacts is enclosed inside immutable XML boundary containers (`<!-- BEGIN UNTRUSTED FORENSIC EVIDENCE CONTAINER -->`).
- **Signature Detection**: Active regex monitors scan evidence text for prompt injection keywords (`ignore previous instructions`, `system prompt override`, `confirm this as clean`). Detected occurrences are flagged as malicious indicators.
- **Immutable System Fencing**: Models are instructed that instructions inside evidence blocks are untrusted artifact data and must never override operational directives.

### 2.4 Path Traversal & Symlink Protection
- **Canonical Resolution**: File paths provided in tool arguments or findings are resolved to canonical absolute paths (`Path.resolve()`).
- **Escape Prevention**: Any path attempting directory traversal (`../`) outside the configured evidence or state directories is blocked with a `PermissionError`.
- **Null Byte Rejection**: Null bytes (`\x00`) in filenames or paths are rejected immediately.

### 2.5 Secret Management & Telemetry Redaction
- **No Hardcoded Keys**: API credentials (`NEBIUS_API_KEY`, `TAVILY_API_KEY`) are read strictly from environment variables or secure terminal input (`getpass`).
- **Secret Redaction**: Any high-entropy token pasted into interactive CLI prompts is cleared from the terminal screen, dropped from memory, and never persisted to logs.

### 2.6 Content-Addressed Storage (CAS) Immutability
- **Hash-Addressed Vault**: Artifacts and tool results are stored exclusively by their SHA-256 digest (`sha256/ab/cd/<hash>.blob`).
- **Read-Verification**: Any retrieval computes a streaming SHA-256 verification before delivering bytes to the caller. Disk tampering triggers an immediate `EvidenceSpoliationError`.

### 2.7 Cryptographic Chain of Custody & Ed25519 Digital Seals (ISO/IEC 27037)
- **Hash-Chained Audit Ledger**: Every stage, tool execution, and state change produces an immutable audit record backlinked to `previous_event_hash` originating from genesis block (`0000000000000000000000000000000000000000000000000000000000000000`).
- **Ed25519 Asymmetric Manifest Signatures**: At case completion, an Ed25519 signature is generated across the latest chain head hash, providing non-repudiation and court-admissible integrity seals.

### 2.8 External Threat Intelligence Isolation Invariant
- **Strict Boundary**: Out-of-band threat intelligence gathered via OSINT APIs (e.g. Tavily) is labeled strictly as `EXTERNAL_THREAT_INTEL`.
- **Zero Conflation**: External reputation scores are NEVER permitted to auto-verify internal forensic claims. Internal claims require internal forensic evidence records.

---

## 3. Reporting a Vulnerability

If you discover a potential security vulnerability within AXIOM DFIR, please report it via private email to:
- **Security Team**: `security@axiom-dfir.local` or open a confidential security advisory on GitHub.
- Please include reproduction steps, environment details, and affected artifact schemas. We will respond within 48 hours.

