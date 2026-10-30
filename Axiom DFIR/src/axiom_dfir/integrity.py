"""AXIOM DFIR - Evidence Integrity Engine (Phase 2.2).

Enforces non-bypassable cryptographic integrity checks across the investigation lifecycle.
Calculates initial SHA256 fingerprints before forensic processing and re-verifies them upon completion.
If evidence is modified, halts the pipeline immediately with an EvidenceSpoliationError.
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("axiom_dfir.integrity")


class EvidenceSpoliationError(RuntimeError):
    """Raised immediately when cryptographic verification proves evidence has been tampered with or modified."""


@dataclass
class IntegrityCheckResult:
    item_id: str
    path: str
    pre_sha256: str
    post_sha256: str
    status: str  # MATCH, MISMATCH, MISSING
    verified_at: str
    file_size_bytes: int
    error_detail: Optional[str] = None


@dataclass
class EvidenceIntegrityLedger:
    case_id: str
    initialization_timestamp: str
    final_verification_timestamp: Optional[str] = None
    overall_status: str = "PENDING"  # INTACT, COMPROMISED, PENDING
    records: Dict[str, IntegrityCheckResult] = field(default_factory=dict)
    audit_events: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "case_id": self.case_id,
            "initialization_timestamp": self.initialization_timestamp,
            "final_verification_timestamp": self.final_verification_timestamp,
            "overall_status": self.overall_status,
            "records": {k: asdict(v) for k, v in self.records.items()},
            "audit_events": self.audit_events,
        }

    def record_event(self, event_type: str, details: Dict[str, Any]) -> None:
        self.audit_events.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            "details": details,
        })


class EvidenceIntegrityEngine:
    """Deterministic cryptographic validator guaranteeing evidence immutability."""

    def __init__(self, case_id: str = "CASE-AUTO-001") -> None:
        self.case_id = case_id
        self.ledger = EvidenceIntegrityLedger(
            case_id=case_id,
            initialization_timestamp=datetime.now(timezone.utc).isoformat(),
        )

    def compute_sha256(self, file_path: Path) -> str:
        """Stream SHA256 computation in 1MB chunks to safely handle 64GB+ images."""
        p = Path(file_path)
        if not p.is_file():
            raise FileNotFoundError(f"Evidence file not found: {p}")
        hasher = hashlib.sha256()
        with open(p, "rb") as f:
            while True:
                chunk = f.read(1024 * 1024)
                if not chunk:
                    break
                hasher.update(chunk)
        return hasher.hexdigest()

    def register_initial_fingerprint(self, item_id: str, file_path: str | Path) -> str:
        """Calculates and registers pre-investigation baseline hash."""
        p = Path(file_path).resolve()
        hash_val = self.compute_sha256(p)
        size_bytes = p.stat().st_size
        now_iso = datetime.now(timezone.utc).isoformat()

        self.ledger.records[item_id] = IntegrityCheckResult(
            item_id=item_id,
            path=str(p),
            pre_sha256=hash_val,
            post_sha256="",
            status="REGISTERED",
            verified_at=now_iso,
            file_size_bytes=size_bytes,
        )

        self.ledger.record_event("BASELINE_REGISTERED", {
            "item_id": item_id,
            "path": str(p),
            "sha256": hash_val,
            "size_bytes": size_bytes,
        })
        logger.info("Registered cryptographic baseline for %s: %s (%s)", item_id, p.name, hash_val[:12])
        return hash_val

    def verify_final_integrity(self, halt_on_violation: bool = True) -> bool:
        """Recalculates SHA256 hashes and compares against registered baselines.

        Raises EvidenceSpoliationError if any evidence file was modified.
        """
        now_iso = datetime.now(timezone.utc).isoformat()
        self.ledger.final_verification_timestamp = now_iso
        all_match = True
        compromised_items: List[Dict[str, str]] = []

        for item_id, record in self.ledger.records.items():
            p = Path(record.path)
            if not p.exists():
                record.status = "MISSING"
                record.error_detail = "Evidence file was deleted during investigation"
                all_match = False
                compromised_items.append({"item_id": item_id, "reason": "FILE_DELETED"})
                continue

            try:
                current_hash = self.compute_sha256(p)
                record.post_sha256 = current_hash
                if current_hash == record.pre_sha256:
                    record.status = "MATCH"
                else:
                    record.status = "MISMATCH"
                    record.error_detail = f"Cryptographic mismatch: pre={record.pre_sha256} vs post={current_hash}"
                    all_match = False
                    compromised_items.append({
                        "item_id": item_id,
                        "path": str(p),
                        "pre_sha256": record.pre_sha256,
                        "post_sha256": current_hash,
                    })
            except Exception as exc:
                record.status = "ERROR"
                record.error_detail = str(exc)
                all_match = False
                compromised_items.append({"item_id": item_id, "reason": f"EXCEPTION: {exc}"})

        if all_match:
            self.ledger.overall_status = "INTACT"
            self.ledger.record_event("INTEGRITY_VERIFICATION_PASSED", {
                "verified_items": len(self.ledger.records),
                "timestamp": now_iso,
            })
            logger.info("All %d evidence items cryptographic integrity verified MATCH.", len(self.ledger.records))
            return True
        else:
            self.ledger.overall_status = "COMPROMISED"
            self.ledger.record_event("SPOLIATION_VIOLATION_DETECTED", {
                "compromised_items": compromised_items,
                "timestamp": now_iso,
            })
            err_msg = (
                f"EVIDENCE SPOLIATION DETECTED! {len(compromised_items)} evidence items modified during analysis. "
                f"Case {self.case_id} marked COMPROMISED. Investigation halted to protect legal chain of custody."
            )
            logger.critical(err_msg)
            if halt_on_violation:
                raise EvidenceSpoliationError(err_msg)
            return False

    def save_audit_log(self, path: Path) -> Path:
        """Persists the complete cryptographic integrity ledger to disk."""
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            json.dump(self.ledger.to_dict(), f, indent=2)
        return p

