"""AXIOM DFIR - Cryptographic Chain of Custody & Digital Signatures (Phase II).

Implements:
  - Cryptographically chained audit ledger (each record binds to previous event hash).
  - Tamper detection that catches deletion, insertion, or retroactive alteration.
  - Ed25519 asymmetric manifest digital signatures for forensic authenticity.
  - Strict compliance with forensic chain-of-custody standards (ISO/IEC 27037).
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

from axiom_dfir.integrity import EvidenceSpoliationError

logger = logging.getLogger("axiom_dfir.chain_of_custody")

GENESIS_HASH = "0" * 64


@dataclass
class ChainRecord:
    event_index: int
    timestamp: str
    stage: str
    actor: str
    action: str
    evidence_id: Optional[str] = None
    artifact_sha256: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    previous_event_hash: str = GENESIS_HASH
    event_hash: str = ""

    def canonical_payload(self) -> bytes:
        """Serializes all fields except event_hash into canonical deterministic JSON bytes."""
        d = {
            "event_index": self.event_index,
            "timestamp": self.timestamp,
            "stage": self.stage,
            "actor": self.actor,
            "action": self.action,
            "evidence_id": self.evidence_id,
            "artifact_sha256": self.artifact_sha256,
            "details": self.details,
            "previous_event_hash": self.previous_event_hash,
        }
        return json.dumps(d, sort_keys=True, separators=(",", ":")).encode("utf-8")

    def compute_hash(self) -> str:
        return hashlib.sha256(self.canonical_payload()).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ChainRecord:
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


class ChainOfCustodyLedger:
    """Tamper-evident, hash-chained ledger for forensic audit events."""

    def __init__(self, case_id: str, ledger_path: Optional[Path | str] = None) -> None:
        self.case_id = case_id
        self.ledger_path = Path(ledger_path) if ledger_path else None
        self.records: List[ChainRecord] = []
        self.signature_info: Optional[Dict[str, str]] = None

    def append_event(
        self,
        stage: str,
        actor: str,
        action: str,
        details: Optional[Dict[str, Any]] = None,
        evidence_id: Optional[str] = None,
        artifact_sha256: Optional[str] = None,
    ) -> ChainRecord:
        idx = len(self.records)
        prev_hash = self.records[-1].event_hash if self.records else GENESIS_HASH
        ts = datetime.now(timezone.utc).isoformat()

        rec = ChainRecord(
            event_index=idx,
            timestamp=ts,
            stage=stage,
            actor=actor,
            action=action,
            evidence_id=evidence_id,
            artifact_sha256=artifact_sha256,
            details=details or {},
            previous_event_hash=prev_hash,
        )
        rec.event_hash = rec.compute_hash()
        self.records.append(rec)
        logger.debug("Appended chain event #%d [%s:%s] -> %s", idx, stage, action, rec.event_hash[:12])

        if self.ledger_path:
            self.save(self.ledger_path)
        return rec

    def verify_chain(self) -> Tuple[bool, Optional[str]]:
        """Verifies the complete integrity of the cryptographic chain.

        Returns (True, None) if completely valid, or (False, reason) if broken.
        """
        if not self.records:
            return True, None

        for i, rec in enumerate(self.records):
            # Check genesis or backlink
            if i == 0:
                if rec.previous_event_hash != GENESIS_HASH:
                    return False, f"Event #0 does not point to GENESIS_HASH. Found: {rec.previous_event_hash}"
            else:
                prev_rec = self.records[i - 1]
                if rec.previous_event_hash != prev_rec.event_hash:
                    return False, (
                        f"Chain broken at event #{i}: previous_event_hash {rec.previous_event_hash} "
                        f"!= prior event_hash {prev_rec.event_hash}"
                    )

            # Recompute event_hash
            expected_hash = rec.compute_hash()
            if rec.event_hash != expected_hash:
                return False, f"Event #{i} has invalid self-hash: {rec.event_hash} != {expected_hash}"

        return True, None

    def assert_valid_or_halt(self) -> None:
        """Enforces anti-spoliation circuit breaker: raises EvidenceSpoliationError if tampered."""
        is_valid, reason = self.verify_chain()
        if not is_valid:
            logger.critical("CHAIN OF CUSTODY INTEGRITY VIOLATION: %s", reason)
            raise EvidenceSpoliationError(f"Chain-of-Custody Spoliation Detected: {reason}")

    # ── Ed25519 Digital Signature Support ─────────────────────────────────────

    @staticmethod
    def generate_ed25519_keypair() -> Tuple[bytes, bytes]:
        """Generates a raw Ed25519 private key (32 bytes) and public key (32 bytes)."""
        priv = ed25519.Ed25519PrivateKey.generate()
        priv_bytes = priv.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption(),
        )
        pub_bytes = priv.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
        return priv_bytes, pub_bytes

    def sign(self, private_key_raw: bytes) -> str:
        """Cryptographically signs the latest chain head using Ed25519."""
        if not self.records:
            raise ValueError("Cannot sign empty chain of custody")

        self.assert_valid_or_halt()
        head_hash = self.records[-1].event_hash
        payload = f"AXIOM_DFIR_SEAL:{self.case_id}:{len(self.records)}:{head_hash}".encode("utf-8")

        priv = ed25519.Ed25519PrivateKey.from_private_bytes(private_key_raw)
        sig = priv.sign(payload)
        sig_hex = sig.hex()

        pub_bytes = priv.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )

        self.signature_info = {
            "algorithm": "Ed25519",
            "signed_head_hash": head_hash,
            "events_count": str(len(self.records)),
            "public_key_hex": pub_bytes.hex(),
            "signature_hex": sig_hex,
            "signed_at": datetime.now(timezone.utc).isoformat(),
        }
        if self.ledger_path:
            self.save(self.ledger_path)
        return sig_hex

    def verify_signature(self, public_key_raw: bytes, signature_hex: str) -> bool:
        """Verifies Ed25519 digital signature against the chain head."""
        if not self.records:
            return False
        head_hash = self.records[-1].event_hash
        payload = f"AXIOM_DFIR_SEAL:{self.case_id}:{len(self.records)}:{head_hash}".encode("utf-8")

        try:
            pub = ed25519.Ed25519PublicKey.from_public_bytes(public_key_raw)
            sig_bytes = bytes.fromhex(signature_hex)
            pub.verify(sig_bytes, payload)
            return True
        except Exception as exc:
            logger.warning("Ed25519 signature verification failed: %s", exc)
            return False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "case_id": self.case_id,
            "total_events": len(self.records),
            "head_hash": self.records[-1].event_hash if self.records else GENESIS_HASH,
            "signature": self.signature_info,
            "records": [r.to_dict() for r in self.records],
        }

    def save(self, path: Path | str) -> None:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        tmp = p.with_suffix(".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)
        tmp.replace(p)

    @classmethod
    def load(cls, path: Path | str) -> ChainOfCustodyLedger:
        p = Path(path)
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
        ledger = cls(case_id=data["case_id"], ledger_path=p)
        ledger.signature_info = data.get("signature")
        for rec_dict in data.get("records", []):
            ledger.records.append(ChainRecord.from_dict(rec_dict))
        return ledger

