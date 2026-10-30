"""Unit tests for AXIOM DFIR Evidence Integrity Engine (Phase 2.2).

Validates:
  - Baseline SHA256 fingerprinting.
  - Verification pass when files remain untouched.
  - Spoliation detection and immediate halt when evidence is altered.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
import pytest

from axiom_dfir.integrity import EvidenceIntegrityEngine, EvidenceSpoliationError


def test_integrity_baseline_and_match(tmp_path: Path):
    """Test that unmodified evidence passes cryptographic integrity checks."""
    test_file = tmp_path / "memory.raw"
    test_file.write_bytes(b"INITIAL_VOLATILE_MEMORY_DUMP_BYTES_1234567890")

    engine = EvidenceIntegrityEngine(case_id="TEST-INTEGRITY-001")
    initial_hash = engine.register_initial_fingerprint("EV-001", test_file)

    assert len(initial_hash) == 64
    assert engine.ledger.records["EV-001"].status == "REGISTERED"

    # Re-verify without modifications
    is_intact = engine.verify_final_integrity(halt_on_violation=True)
    assert is_intact is True
    assert engine.ledger.records["EV-001"].status == "MATCH"
    assert engine.ledger.overall_status == "INTACT"


def test_spoliation_detected_when_evidence_modified(tmp_path: Path):
    """Test that tampering with evidence raises EvidenceSpoliationError and halts."""
    test_file = tmp_path / "disk.img"
    test_file.write_bytes(b"AUTHENTIC_ORIGINAL_DISK_EVIDENCE_BYTES")

    engine = EvidenceIntegrityEngine(case_id="TEST-SPOLIATION-002")
    engine.register_initial_fingerprint("EV-DISK", test_file)

    # TAMPER: In-place evidence modification simulation
    test_file.write_bytes(b"TAMPERED_COMPROMISED_EVIDENCE_BYTES_ATTACKER")

    with pytest.raises(EvidenceSpoliationError) as exc_info:
        engine.verify_final_integrity(halt_on_violation=True)

    assert "EVIDENCE SPOLIATION DETECTED" in str(exc_info.value)
    assert engine.ledger.overall_status == "COMPROMISED"
    assert engine.ledger.records["EV-DISK"].status == "MISMATCH"


def test_spoliation_detected_when_evidence_deleted(tmp_path: Path):
    """Test that accidental evidence deletion raises EvidenceSpoliationError."""
    test_file = tmp_path / "evtx_log.evtx"
    test_file.write_bytes(b"ElfFile\x00\x00\x00")

    engine = EvidenceIntegrityEngine(case_id="TEST-DELETION-003")
    engine.register_initial_fingerprint("EV-LOG", test_file)

    # Delete the evidence file
    test_file.unlink()

    with pytest.raises(EvidenceSpoliationError):
        engine.verify_final_integrity(halt_on_violation=True)

    assert engine.ledger.records["EV-LOG"].status == "MISSING"

