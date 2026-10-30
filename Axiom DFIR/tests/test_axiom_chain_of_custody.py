"""Tests for AXIOM DFIR Cryptographic Chain of Custody & Ed25519 Signatures (Phase II)."""

import tempfile
from pathlib import Path
import pytest

from axiom_dfir.chain_of_custody import ChainOfCustodyLedger, GENESIS_HASH
from axiom_dfir.integrity import EvidenceSpoliationError


def test_chain_of_custody_backlinking():
    with tempfile.TemporaryDirectory() as td:
        lp = Path(td) / "coc.json"
        ledger = ChainOfCustodyLedger("CASE-001", lp)

        e0 = ledger.append_event("STAGE_01", "Examiner", "INTAKE", {"file": "mem.raw"})
        assert e0.event_index == 0
        assert e0.previous_event_hash == GENESIS_HASH
        assert len(e0.event_hash) == 64

        e1 = ledger.append_event("STAGE_02", "Orchestrator", "HASH_BASELINE", {"status": "OK"})
        assert e1.event_index == 1
        assert e1.previous_event_hash == e0.event_hash
        assert len(e1.event_hash) == 64

        # Chain verification
        is_valid, err = ledger.verify_chain()
        assert is_valid is True
        assert err is None


def test_chain_tamper_detection():
    with tempfile.TemporaryDirectory() as td:
        lp = Path(td) / "coc.json"
        ledger = ChainOfCustodyLedger("CASE-001", lp)
        ledger.append_event("STAGE_01", "Examiner", "INTAKE")
        ledger.append_event("STAGE_02", "Orchestrator", "HASH_BASELINE")
        ledger.append_event("STAGE_03", "Orchestrator", "TOOL_RUN")

        # Verify initial valid state
        assert ledger.verify_chain()[0] is True

        # Tamper with record #1 action
        ledger.records[1].action = "FABRICATED_UNAUTHORIZED_ACTION"

        is_valid, err = ledger.verify_chain()
        assert is_valid is False
        assert "invalid self-hash" in err

        with pytest.raises(EvidenceSpoliationError):
            ledger.assert_valid_or_halt()


def test_ed25519_digital_signature_seal():
    with tempfile.TemporaryDirectory() as td:
        lp = Path(td) / "coc.json"
        ledger = ChainOfCustodyLedger("CASE-001", lp)
        ledger.append_event("STAGE_01", "Examiner", "INTAKE")
        ledger.append_event("STAGE_15", "Orchestrator", "CASE_COMPLETION")

        priv_raw, pub_raw = ledger.generate_ed25519_keypair()
        assert len(priv_raw) == 32
        assert len(pub_raw) == 32

        sig_hex = ledger.sign(priv_raw)
        assert len(sig_hex) == 128  # 64-byte Ed25519 signature in hex

        # Valid signature verification
        assert ledger.verify_signature(pub_raw, sig_hex) is True

        # Corrupted signature verification fails
        bad_sig = "0" * 128
        assert ledger.verify_signature(pub_raw, bad_sig) is False

