"""AXIOM DFIR - Deterministic Claim Validation Engine (Phase 2.5).

The central differentiator of AXIOM DFIR:
  "The AI may propose a finding, but only verified forensic evidence can confirm it."

Enforces strict, code-driven mathematical and relational checks against actual forensic tool outputs.
Eliminates hallucinated PIDs, fabricated file hashes, fake network connections, and uncorroborated MITRE mappings.

Canonical Validation Statuses:
  - VERIFIED: All claims deterministically match actual evidence records.
  - PARTIALLY_VERIFIED: Primary claim verified; secondary contextual claim unverified.
  - UNVERIFIED: No corresponding tool record or fact exists in evidence.
  - CONTRADICTED: Tool output directly refutes the claim (e.g., claimed PID exists with different binary/PPID).
  - BLOCKED: Security or integrity gate rejection (e.g. anti-forensics violation or unapproved tool).
"""

from __future__ import annotations

import enum
import hashlib
import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger("axiom_dfir.validation")


class ValidationStatus(str, enum.Enum):
    VERIFIED = "VERIFIED"
    PARTIALLY_VERIFIED = "PARTIALLY_VERIFIED"
    UNVERIFIED = "UNVERIFIED"
    CONTRADICTED = "CONTRADICTED"
    BLOCKED = "BLOCKED"


@dataclass
class ValidationCheckItem:
    claim_type: str
    field_name: str
    claimed_value: Any
    evidence_value: Any
    matched: bool
    contradicted: bool
    evidence_ref: str
    detail: str


@dataclass
class FindingValidationResult:
    finding_id: str
    title: str
    validation_status: ValidationStatus
    confidence: float
    checks: List[ValidationCheckItem] = field(default_factory=list)
    corroborating_evidence_refs: List[str] = field(default_factory=list)
    contradicting_evidence_refs: List[str] = field(default_factory=list)
    rejection_reason: Optional[str] = None
    validated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["validation_status"] = self.validation_status.value
        return d


class ClaimValidationEngine:
    """Deterministic validator comparing AI proposals against compiled EvidenceDB and ReferenceSet."""

    def __init__(self, evidence_db: Optional[Dict[str, Any]] = None, reference_set: Optional[Dict[str, Any]] = None) -> None:
        self.evidence_db = evidence_db or {}
        self.reference_set = reference_set or {}
        self._index_evidence()

    def _index_evidence(self) -> None:
        """Indexes known forensic ground truths for rapid deterministic lookup."""
        self.known_pids: Dict[int, Dict[str, Any]] = {}
        self.known_hashes: Set[str] = set()
        self.known_connections: List[Dict[str, Any]] = []
        self.known_files: Set[str] = set()
        self.known_users: Set[str] = set()

        # Extract from reference_set
        for pid_val, pinfo in self.reference_set.get("pids", {}).items():
            try:
                pid_int = int(pid_val)
                self.known_pids[pid_int] = pinfo if isinstance(pinfo, dict) else {"name": str(pinfo)}
            except Exception:
                pass

        for h in self.reference_set.get("hashes", []):
            if isinstance(h, str):
                self.known_hashes.add(h.lower().strip())

        for conn in self.reference_set.get("connections", []):
            if isinstance(conn, dict):
                self.known_connections.append(conn)

        for f in self.reference_set.get("files", []):
            if isinstance(f, str):
                self.known_files.add(f.lower().strip())

        # Extract from evidence_db if available
        for fact in self.evidence_db.get("facts", []):
            ftype = fact.get("fact_type", "")
            data = fact.get("data", {})
            if ftype == "process" and "pid" in data:
                try:
                    self.known_pids[int(data["pid"])] = data
                except Exception:
                    pass
            elif ftype == "hash" and "hash" in data:
                self.known_hashes.add(str(data["hash"]).lower().strip())
            elif ftype == "connection":
                self.known_connections.append(data)
            elif ftype == "file" and "path" in data:
                self.known_files.add(str(data["path"]).lower().strip())
            elif ftype == "user" and "username" in data:
                self.known_users.add(str(data["username"]).lower().strip())

    def validate_finding(self, finding: Dict[str, Any]) -> FindingValidationResult:
        """Deterministically validates a single AI finding against indexed evidence ground truth."""
        finding_id = str(finding.get("finding_id") or finding.get("id") or "FIND-000")
        title = str(finding.get("title") or finding.get("name") or "Untitled Proposal")
        claims = finding.get("claims") or finding.get("claimed_value") or {}
        if not isinstance(claims, dict):
            claims = {"raw_claim": claims}

        evidence_refs = finding.get("evidence_refs") or finding.get("source_artifacts") or []
        if isinstance(evidence_refs, str):
            evidence_refs = [evidence_refs]

        checks: List[ValidationCheckItem] = []
        corroborating_refs: List[str] = []
        contradicting_refs: List[str] = []

        has_checks = False
        all_passed = True
        has_contradiction = False
        has_at_least_one_match = False

        # 1. Validate File Hash Claims
        hash_claim = claims.get("hash") or claims.get("sha256") or claims.get("sha1") or claims.get("md5")
        if hash_claim:
            has_checks = True
            norm_hash = str(hash_claim).lower().strip()
            if norm_hash in self.known_hashes:
                has_at_least_one_match = True
                checks.append(ValidationCheckItem(
                    claim_type="hash",
                    field_name="hash",
                    claimed_value=norm_hash,
                    evidence_value=norm_hash,
                    matched=True,
                    contradicted=False,
                    evidence_ref=evidence_refs[0] if evidence_refs else "REF-HASH",
                    detail="Cryptographic hash found in verified forensic evidence",
                ))
                if evidence_refs:
                    corroborating_refs.extend(evidence_refs)
            else:
                all_passed = False
                checks.append(ValidationCheckItem(
                    claim_type="hash",
                    field_name="hash",
                    claimed_value=norm_hash,
                    evidence_value=None,
                    matched=False,
                    contradicted=False,
                    evidence_ref="",
                    detail=f"Hash {norm_hash} not found in any extracted tool artifact",
                ))

        # 2. Validate Process Existence & Name
        pid_claim = claims.get("pid")
        proc_name_claim = claims.get("process") or claims.get("process_name")
        if pid_claim is not None:
            has_checks = True
            try:
                pid_int = int(pid_claim)
                if pid_int in self.known_pids:
                    known_info = self.known_pids[pid_int]
                    actual_name = known_info.get("name", "")
                    if proc_name_claim and actual_name and proc_name_claim.lower() not in actual_name.lower():
                        # PID exists but binary name is completely different -> CONTRADICTION
                        has_contradiction = True
                        all_passed = False
                        checks.append(ValidationCheckItem(
                            claim_type="process_existence",
                            field_name="process_name",
                            claimed_value=f"PID {pid_int} as {proc_name_claim}",
                            evidence_value=f"PID {pid_int} actual binary {actual_name}",
                            matched=False,
                            contradicted=True,
                            evidence_ref=evidence_refs[0] if evidence_refs else "REF-PSTREE",
                            detail=f"PID {pid_int} exists but corresponds to '{actual_name}', contradicting claim '{proc_name_claim}'",
                        ))
                        contradicting_refs.append(evidence_refs[0] if evidence_refs else "REF-PSTREE")
                    else:
                        has_at_least_one_match = True
                        checks.append(ValidationCheckItem(
                            claim_type="process_existence",
                            field_name="pid",
                            claimed_value=pid_int,
                            evidence_value=pid_int,
                            matched=True,
                            contradicted=False,
                            evidence_ref=evidence_refs[0] if evidence_refs else "REF-PSTREE",
                            detail=f"PID {pid_int} verified in process table",
                        ))
                        if evidence_refs:
                            corroborating_refs.extend(evidence_refs)
                else:
                    all_passed = False
                    checks.append(ValidationCheckItem(
                        claim_type="process_existence",
                        field_name="pid",
                        claimed_value=pid_int,
                        evidence_value=None,
                        matched=False,
                        contradicted=False,
                        evidence_ref="",
                        detail=f"PID {pid_int} not found in active or terminated process lists",
                    ))
            except Exception:
                all_passed = False

        # 3. Validate Parent-Child Relationship
        parent_pid = claims.get("parent_pid") or claims.get("ppid")
        child_pid = claims.get("child_pid") or claims.get("pid")
        if parent_pid is not None and child_pid is not None:
            has_checks = True
            try:
                c_pid = int(child_pid)
                p_pid = int(parent_pid)
                if c_pid in self.known_pids:
                    actual_ppid = self.known_pids[c_pid].get("ppid")
                    if actual_ppid is not None:
                        actual_ppid_int = int(actual_ppid)
                        if actual_ppid_int == p_pid:
                            has_at_least_one_match = True
                            checks.append(ValidationCheckItem(
                                claim_type="child_process",
                                field_name="ppid",
                                claimed_value=p_pid,
                                evidence_value=actual_ppid_int,
                                matched=True,
                                contradicted=False,
                                evidence_ref=evidence_refs[0] if evidence_refs else "REF-PSTREE",
                                detail=f"Parent-child link PPID {p_pid} -> PID {c_pid} confirmed",
                            ))
                        else:
                            has_contradiction = True
                            all_passed = False
                            checks.append(ValidationCheckItem(
                                claim_type="child_process",
                                field_name="ppid",
                                claimed_value=p_pid,
                                evidence_value=actual_ppid_int,
                                matched=False,
                                contradicted=True,
                                evidence_ref=evidence_refs[0] if evidence_refs else "REF-PSTREE",
                                detail=f"PID {c_pid} actually spawned by PPID {actual_ppid_int}, contradicting claimed PPID {p_pid}",
                            ))
                            contradicting_refs.append(evidence_refs[0] if evidence_refs else "REF-PSTREE")
            except Exception:
                pass

        # 4. Validate Network Connections
        dest_ip = claims.get("destination_ip") or claims.get("remote_ip") or claims.get("ip")
        dest_port = claims.get("destination_port") or claims.get("remote_port") or claims.get("port")
        if dest_ip:
            has_checks = True
            dest_ip_str = str(dest_ip).strip()
            conn_match = False
            for kconn in self.known_connections:
                kip = str(kconn.get("remote_ip") or kconn.get("dst_ip") or kconn.get("ip") or "")
                if dest_ip_str == kip:
                    if dest_port is None:
                        conn_match = True
                        break
                    kport = str(kconn.get("remote_port") or kconn.get("dst_port") or kconn.get("port") or "")
                    if str(dest_port) == kport:
                        conn_match = True
                        break
            if conn_match:
                has_at_least_one_match = True
                checks.append(ValidationCheckItem(
                    claim_type="network_connection",
                    field_name="remote_ip",
                    claimed_value=dest_ip_str,
                    evidence_value=dest_ip_str,
                    matched=True,
                    contradicted=False,
                    evidence_ref=evidence_refs[0] if evidence_refs else "REF-NETSCAN",
                    detail=f"Network socket connection to {dest_ip_str} confirmed in netscan/pcap",
                ))
                if evidence_refs:
                    corroborating_refs.extend(evidence_refs)
            else:
                all_passed = False
                checks.append(ValidationCheckItem(
                    claim_type="network_connection",
                    field_name="remote_ip",
                    claimed_value=dest_ip_str,
                    evidence_value=None,
                    matched=False,
                    contradicted=False,
                    evidence_ref="",
                    detail=f"Connection to IP {dest_ip_str} not observed in network artifacts",
                ))

        # Determine Final Canonical Status
        if has_contradiction:
            status = ValidationStatus.CONTRADICTED
            confidence = 0.0
            rejection_reason = "Forensic evidence directly refutes one or more claimed relationships"
        elif not has_checks:
            # Finding has no factual verifiable claims
            status = ValidationStatus.UNVERIFIED
            confidence = 0.2
            rejection_reason = "Finding contains no testable factual forensic claims"
        elif all_passed and has_at_least_one_match:
            status = ValidationStatus.VERIFIED
            confidence = 0.95
            rejection_reason = None
        elif has_at_least_one_match and not all_passed:
            status = ValidationStatus.PARTIALLY_VERIFIED
            confidence = 0.60
            rejection_reason = "Some claims verified, but supporting claims lack tool corroboration"
        else:
            status = ValidationStatus.UNVERIFIED
            confidence = 0.10
            rejection_reason = "No claimed values found in verified tool output"

        # Deduplicate refs
        unique_corr = list(dict.fromkeys(corroborating_refs))
        unique_contra = list(dict.fromkeys(contradicting_refs))

        return FindingValidationResult(
            finding_id=finding_id,
            title=title,
            validation_status=status,
            confidence=confidence,
            checks=checks,
            corroborating_evidence_refs=unique_corr,
            contradicting_evidence_refs=unique_contra,
            rejection_reason=rejection_reason,
        )

    def validate_findings_batch(self, findings: List[Dict[str, Any]]) -> List[FindingValidationResult]:
        """Validates an entire batch of candidate findings and returns structured validation records."""
        return [self.validate_finding(f) for f in findings]

    def validate_atomic_claims(self, claims: List[Any]) -> List[Any]:
        """Validates a batch of AtomicClaim objects using the Phase II atomic validation engine."""
        from axiom_dfir.atomic_claims import AtomicClaimValidator
        validator = AtomicClaimValidator()
        ctx = {
            "pids": self.known_pids,
            "hashes": list(self.known_hashes),
            "connections": self.known_connections,
            "files": {f: {} for f in self.known_files},
            "users": list(self.known_users),
        }
        return validator.validate_claims_batch(claims, ctx)


