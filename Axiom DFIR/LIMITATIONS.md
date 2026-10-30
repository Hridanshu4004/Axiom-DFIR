# AXIOM DFIR: TECHNICAL LIMITATIONS & BOUNDARY DISCLOSURES

In accordance with rigorous forensic engineering standards, AXIOM DFIR explicitly documents the technical boundaries, assumptions, and limitations of the platform.

---

## 1. Evidence Scope & Static Triage
- **Static Capture Assumption**: AXIOM DFIR analyzes acquired forensic artifacts (memory images, disk captures, event log exports, registry hives). It does not maintain a resident kernel sensor on live production endpoints.
- **Timestamp Fidelity**: Forensic timestamps in event logs and filesystem metadata ($MFT) are subject to timestamp-stomping (timestomping) by sophisticated adversaries. AXIOM flags timestamp inconsistencies between Prefetch, Amcache, and USN journals, but cannot resurrect overwritten timeline records.

## 2. Kernel & Rootkit Boundaries
- **DKOM & SSDT Checks**: The system parses kernel System Service Descriptor Tables (SSDT) and detects unlinked processes (`vol_psscan` vs `vol_pstree`).
- **Hypervisor Rootkits**: Sub-OS or Type-1 hypervisor rootkits operating below Ring 0 are invisible to guest memory analysis.

## 3. Cryptographic Storage & Decryption
- **Encrypted Volumes**: Filesystem analysis on full-disk encrypted partitions (BitLocker, LUKS) requires either mounting with provided recovery keys or extracting volume master keys from a companion memory dump.
- **Encrypted Network Payloads**: Network connection records (`vol_netscan`, pcap) identify source/destination IP pairs, ports, and protocols. Encrypted TLS payloads (e.g. HTTPS C2) are analyzed via behavioral metadata, JA3 fingerprints, and domain anomalies rather than plaintext payload inspection.

## 4. Model Context & Bandwidth Economy
- **No Raw Binary Ingestion to LLMs**: Entire 64GB memory dumps or multi-terabyte disk images are never transmitted to hosted models. This preserves client confidentiality and avoids token exhaustion. Only structured, extracted tool facts and candidate excerpts are provided to the model.

## 5. Airgapped / Offline Operations
- **Hosted Cloud Endpoint**: Default live operations require outbound HTTPS connectivity to Nebius Token Factory (`api.tokenfactory.nebius.com:443`).
- **Airgapped Fallback**: In strictly isolated environments without internet access, operators can redirect `NEBIUS_BASE_URL` to a local on-premises OpenAI-compatible vLLM or Ollama instance serving NVIDIA Nemotron models.

