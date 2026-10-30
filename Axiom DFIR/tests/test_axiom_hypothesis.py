"""Tests for AXIOM DFIR Adaptive Hypothesis Engine (Phase II)."""

import tempfile
from pathlib import Path
from axiom_dfir.hypothesis import (
    EvidenceCitation,
    Hypothesis,
    HypothesisStatus,
    InvestigationLedger,
)


def test_hypothesis_initialization():
    h = Hypothesis(
        hypothesis_id="HYP-100",
        title="CobaltStrike Beaconing",
        description="Beaconing observed over port 4444",
        entities=["PROCESS-4120", "IP-192.168.1.50"],
    )
    assert h.status == HypothesisStatus.OPEN
    assert h.confidence_score == 0.5
    assert len(h.supporting_evidence) == 0
    assert len(h.contradicting_evidence) == 0


def test_hypothesis_supporting_evidence_and_confirmation():
    h = Hypothesis(hypothesis_id="HYP-101", title="Reverse Shell Execution", description="Test")
    c1 = EvidenceCitation(evidence_id="EV-1", artifact_type="PROCESS", source_path="/path/proc.raw")
    c2 = EvidenceCitation(evidence_id="EV-2", artifact_type="NETWORK", source_path="/path/net.raw")

    h.add_supporting(c1)
    assert h.status == HypothesisStatus.OPEN
    h.evaluate_status(min_supporting_for_confirmation=2)
    assert h.status == HypothesisStatus.TESTING

    h.add_supporting(c2)
    h.evaluate_status(min_supporting_for_confirmation=2)
    assert h.status == HypothesisStatus.CONFIRMED
    assert "Confirmed" in (h.resolution_reason or "")


def test_hypothesis_falsification_first_refutation():
    h = Hypothesis(hypothesis_id="HYP-102", title="Admin Execution", description="Test")
    sup = EvidenceCitation(evidence_id="EV-1", artifact_type="USER", source_path="/path/user.raw")
    contra = EvidenceCitation(
        evidence_id="EV-2",
        artifact_type="MALFIND",
        source_path="/path/mem.raw",
        description="Injected unbacked shellcode detected",
    )

    h.add_supporting(sup)
    assert len(h.supporting_evidence) == 1

    # Contradicting evidence should immediately refute under falsification-first rule
    h.add_contradicting(contra)
    h.evaluate_status()
    assert h.status == HypothesisStatus.REFUTED
    assert "Refuted by 1 contradicting" in (h.resolution_reason or "")


def test_investigation_ledger_competing_resolution():
    with tempfile.TemporaryDirectory() as td:
        lp = Path(td) / "ledger.json"
        ledger = InvestigationLedger(case_id="CASE-TEST", state_path=lp, max_turns=3)

        h1 = Hypothesis(
            hypothesis_id="HYP-A",
            title="Malicious",
            description="A",
            competing_hypotheses=["HYP-B"],
        )
        h2 = Hypothesis(
            hypothesis_id="HYP-B",
            title="Benign Admin",
            description="B",
            competing_hypotheses=["HYP-A"],
        )

        ledger.register_hypothesis(h1)
        ledger.register_hypothesis(h2)

        assert len(ledger.get_open_hypotheses()) == 2

        # Record a turn
        ledger.record_turn(
            turn_number=1,
            targeted_hypothesis_id="HYP-A",
            tool_selected="vol_pstree",
            investigative_inquiry="Verify parent process",
            observations=[{"pid": 4120, "ppid": 1024}],
        )

        # Resolve competing
        ledger.resolve_competing("HYP-A", "HYP-B", reason="Unbacked memory confirmed malice")

        assert h2.status == HypothesisStatus.REFUTED
        assert "Refuted by competing hypothesis HYP-A" in h2.resolution_reason

        # Reload from disk
        reloaded = InvestigationLedger.load(lp)
        assert len(reloaded.hypotheses) == 2
        assert reloaded.get_hypothesis("HYP-B").status == HypothesisStatus.REFUTED

