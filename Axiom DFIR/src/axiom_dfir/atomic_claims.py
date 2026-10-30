"""AXIOM DFIR - Atomic Claim Validation & Explainability Engine (Phase II).

Decomposes complex forensic propositions into verifiable atomic tuples:
    (Subject, Predicate, Object, TimeScope)

Evaluates each atomic claim using dedicated, deterministic rule classes:
    - RuleProcessRelationship (RULE-PROC-001)
    - RuleHashMatch (RULE-HASH-001)
    - RuleSocketAttribution (RULE-NET-001)
    - RuleTimestampConsistency (RULE-TIME-001)
    - RuleUserLogon (RULE-AUTH-001)

Provides human-readable and machine-verifiable explanation traces.
"""

from __future__ import annotations

import abc
import enum
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set

from axiom_dfir.validation import ValidationStatus

logger = logging.getLogger("axiom_dfir.atomic_claims")


@dataclass
class AtomicClaim:
    """Atomic representation of a single forensic proposition."""
    claim_id: str
    claim_type: str  # PROCESS_SPAWN, NETWORK_CONNECTION, FILE_HASH, TIMESTAMP_ORDER, USER_AUTHENTICATION
    subject: str
    predicate: str
    object: str
    time_scope: Optional[str] = None
    evidence_refs: List[str] = field(default_factory=list)
    validation_rule_id: Optional[str] = None
    status: ValidationStatus = ValidationStatus.UNVERIFIED
    confidence: float = 0.0
    explanation: str = ""
    evaluated_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["status"] = self.status.value
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> AtomicClaim:
        d = dict(data)
        if "status" in d and isinstance(d["status"], str):
            d["status"] = ValidationStatus(d["status"])
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


class BaseValidationRule(abc.ABC):
    """Abstract base class for deterministic validation rules."""
    rule_id: str = "RULE-BASE"
    description: str = ""

    @abc.abstractmethod
    def evaluate(self, claim: AtomicClaim, context: Dict[str, Any]) -> Tuple[ValidationStatus, float, str]:
        """Evaluates claim against evidence context.

        Returns:
            Tuple of (ValidationStatus, confidence, explanation_string)
        """
        pass


class RuleProcessRelationship(BaseValidationRule):
    """RULE-PROC-001: Deterministically validates process spawn relationships (PID -> PPID)."""
    rule_id = "RULE-PROC-001"
    description = "Validates process execution and parent-child hierarchy in evidence process tree."

    def evaluate(self, claim: AtomicClaim, context: Dict[str, Any]) -> Tuple[ValidationStatus, float, str]:
        pids = context.get("pids", {})
        # Subject format expected: process:name:PID or PID as string/int
        try:
            # Extract child PID
            child_pid = int(claim.subject.split(":")[-1])
        except Exception:
            return ValidationStatus.UNVERIFIED, 0.0, f"Cannot parse subject PID from {claim.subject}"

        if child_pid not in pids:
            return (
                ValidationStatus.UNVERIFIED,
                0.0,
                f"Child PID {child_pid} not found in verified process tree facts.",
            )

        child_info = pids[child_pid]
        actual_ppid = child_info.get("ppid")
        actual_name = child_info.get("name", "").lower()

        # Check predicate
        if claim.predicate.upper() in ("SPAWNED_BY", "CHILD_OF"):
            try:
                claimed_ppid = int(claim.object.split(":")[-1])
            except Exception:
                return ValidationStatus.UNVERIFIED, 0.0, f"Cannot parse parent PPID from {claim.object}"

            if actual_ppid is not None and int(actual_ppid) != claimed_ppid:
                return (
                    ValidationStatus.CONTRADICTED,
                    0.0,
                    f"Contradicted: Evidence shows PID {child_pid} ({actual_name}) was spawned by PPID {actual_ppid}, not claimed PPID {claimed_ppid}.",
                )

            return (
                ValidationStatus.VERIFIED,
                1.0,
                f"Verified: PID {child_pid} ({actual_name}) confirmed spawned by PPID {actual_ppid} in process facts.",
            )

        return ValidationStatus.UNVERIFIED, 0.0, f"Unsupported predicate '{claim.predicate}' for process rule."


class RuleHashMatch(BaseValidationRule):
    """RULE-HASH-001: Deterministically validates cryptographic file digests."""
    rule_id = "RULE-HASH-001"
    description = "Validates file hashes against verified forensic artifact catalogs."

    def evaluate(self, claim: AtomicClaim, context: Dict[str, Any]) -> Tuple[ValidationStatus, float, str]:
        known_hashes = {h.lower().strip() for h in context.get("hashes", [])}
        claimed_hash = claim.object.split(":")[-1].lower().strip()

        if claimed_hash in known_hashes:
            return (
                ValidationStatus.VERIFIED,
                1.0,
                f"Verified: Hash {claimed_hash} matches evidence catalog entry for {claim.subject}.",
            )

        # Check if contradicted (file exists but hash differs)
        files = context.get("files", {})
        if claim.subject in files and files[claim.subject].get("hash") != claimed_hash:
            actual = files[claim.subject].get("hash")
            return (
                ValidationStatus.CONTRADICTED,
                0.0,
                f"Contradicted: File {claim.subject} exists but actual hash is {actual}, not {claimed_hash}.",
            )

        return (
            ValidationStatus.UNVERIFIED,
            0.0,
            f"Unverified: Hash {claimed_hash} not present in current forensic facts.",
        )


class RuleSocketAttribution(BaseValidationRule):
    """RULE-NET-001: Deterministically validates network connection endpoint and PID attribution."""
    rule_id = "RULE-NET-001"
    description = "Validates network socket connection endpoints against memory/netscan facts."

    def evaluate(self, claim: AtomicClaim, context: Dict[str, Any]) -> Tuple[ValidationStatus, float, str]:
        conns = context.get("connections", [])
        claimed_endpoint = claim.object.replace("socket:", "").strip()

        matched = False
        contradicting = False

        for c in conns:
            remote = f"{c.get('remote_ip')}:{c.get('remote_port')}"
            if remote == claimed_endpoint:
                matched = True
                # If claim subject specifies PID or process:name:pid, check PID match
                try:
                    parts = claim.subject.split(":")
                    pid_candidate = None
                    for p in reversed(parts):
                        if p.isdigit():
                            pid_candidate = int(p)
                            break
                        elif p.upper().startswith("PID_") and p[4:].isdigit():
                            pid_candidate = int(p[4:])
                            break

                    if pid_candidate is not None:
                        actual_pid = c.get("pid")
                        if actual_pid is not None and int(actual_pid) != pid_candidate:
                            contradicting = True
                            return (
                                ValidationStatus.CONTRADICTED,
                                0.0,
                                f"Contradicted: Connection to {claimed_endpoint} was owned by PID {actual_pid}, not claimed PID {pid_candidate}.",
                            )
                except Exception:
                    pass
                break

        if matched:
            return (
                ValidationStatus.VERIFIED,
                1.0,
                f"Verified: Active socket connection to {claimed_endpoint} confirmed in evidence.",
            )

        return (
            ValidationStatus.UNVERIFIED,
            0.0,
            f"Unverified: No socket connection to {claimed_endpoint} found in connection records.",
        )


class RuleTimestampConsistency(BaseValidationRule):
    """RULE-TIME-001: Deterministically validates chronological ordering and causality."""
    rule_id = "RULE-TIME-001"
    description = "Validates chronological order to ensure parent creation precedes child creation."

    def evaluate(self, claim: AtomicClaim, context: Dict[str, Any]) -> Tuple[ValidationStatus, float, str]:
        timestamps = context.get("timestamps", {})
        ts_subject = timestamps.get(claim.subject)
        ts_object = timestamps.get(claim.object)

        if not ts_subject or not ts_object:
            return (
                ValidationStatus.UNVERIFIED,
                0.0,
                f"Unverified: Missing verified timestamp baseline for {claim.subject} or {claim.object}.",
            )

        if claim.predicate.upper() in ("PRECEDED_BY", "OBSERVED_AFTER"):
            if ts_subject < ts_object:
                return (
                    ValidationStatus.CONTRADICTED,
                    0.0,
                    f"Contradicted: Causality violation! {claim.subject} ({ts_subject}) preceded {claim.object} ({ts_object}).",
                )
            return (
                ValidationStatus.VERIFIED,
                1.0,
                f"Verified: Temporal order confirmed ({claim.object} at {ts_object} preceded {claim.subject} at {ts_subject}).",
            )

        return ValidationStatus.UNVERIFIED, 0.0, f"Unsupported predicate '{claim.predicate}' for temporal rule."


class RuleUserLogon(BaseValidationRule):
    """RULE-AUTH-001: Deterministically validates user authentication sessions."""
    rule_id = "RULE-AUTH-001"
    description = "Validates user account logons against Windows Security Event log (4624/4672)."

    def evaluate(self, claim: AtomicClaim, context: Dict[str, Any]) -> Tuple[ValidationStatus, float, str]:
        logons = context.get("logons", [])
        claimed_user = claim.subject.replace("user:", "").strip().lower()

        for lgn in logons:
            ev_user = str(lgn.get("target_username", "")).lower()
            if ev_user == claimed_user:
                return (
                    ValidationStatus.VERIFIED,
                    1.0,
                    f"Verified: Successful logon event for user '{claimed_user}' identified in authentication log.",
                )

        return (
            ValidationStatus.UNVERIFIED,
            0.0,
            f"Unverified: No authentication record found for user '{claimed_user}'.",
        )


class AtomicClaimValidator:
    """Orchestrator for atomic claim validation with explicit rule routing."""

    def __init__(self) -> None:
        self.rules: Dict[str, BaseValidationRule] = {
            "RULE-PROC-001": RuleProcessRelationship(),
            "RULE-HASH-001": RuleHashMatch(),
            "RULE-NET-001": RuleSocketAttribution(),
            "RULE-TIME-001": RuleTimestampConsistency(),
            "RULE-AUTH-001": RuleUserLogon(),
        }

    def register_rule(self, rule: BaseValidationRule) -> None:
        self.rules[rule.rule_id] = rule

    def validate_claim(self, claim: AtomicClaim, context: Dict[str, Any]) -> AtomicClaim:
        """Dispatches an atomic claim to its corresponding validation rule."""
        rule: Optional[BaseValidationRule] = None

        if claim.validation_rule_id and claim.validation_rule_id in self.rules:
            rule = self.rules[claim.validation_rule_id]
        else:
            # Auto-route by claim type
            type_mapping = {
                "PROCESS_SPAWN": "RULE-PROC-001",
                "FILE_HASH": "RULE-HASH-001",
                "NETWORK_CONNECTION": "RULE-NET-001",
                "TIMESTAMP_ORDER": "RULE-TIME-001",
                "USER_AUTHENTICATION": "RULE-AUTH-001",
            }
            rule_id = type_mapping.get(claim.claim_type, "RULE-PROC-001")
            rule = self.rules.get(rule_id)

        if not rule:
            claim.status = ValidationStatus.UNVERIFIED
            claim.confidence = 0.0
            claim.explanation = f"No applicable validation rule for claim type {claim.claim_type}."
            claim.evaluated_at = datetime.now(timezone.utc).isoformat()
            return claim

        claim.validation_rule_id = rule.rule_id
        status, conf, explanation = rule.evaluate(claim, context)
        claim.status = status
        claim.confidence = conf
        claim.explanation = explanation
        claim.evaluated_at = datetime.now(timezone.utc).isoformat()
        return claim

    def validate_claims_batch(self, claims: List[AtomicClaim], context: Dict[str, Any]) -> List[AtomicClaim]:
        return [self.validate_claim(c, context) for c in claims]
