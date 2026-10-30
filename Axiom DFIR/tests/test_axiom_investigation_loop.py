"""Tests for AXIOM DFIR Adaptive Investigation Loop (Phase II)."""

import tempfile
from pathlib import Path
from axiom_dfir.hypothesis import HypothesisStatus
from axiom_dfir.investigation_loop import AdaptiveInvestigationEngine


def test_investigation_engine_generates_hypotheses():
    with tempfile.TemporaryDirectory() as td:
        engine = AdaptiveInvestigationEngine("CASE-LOOP-01", td, max_turns=3)
        triage_facts = [{"pid": 4120, "process": "powershell.exe"}]
        hypotheses = engine.generate_initial_hypotheses(triage_facts)

        assert len(hypotheses) == 2
        # One malicious, one benign admin
        ids = [h.hypothesis_id for h in hypotheses]
        assert "HYP-001" in ids
        assert "HYP-002" in ids
        assert len(engine.ledger.hypotheses) == 2


def test_investigation_engine_executes_bounded_loop():
    with tempfile.TemporaryDirectory() as td:
        engine = AdaptiveInvestigationEngine("CASE-LOOP-02", td, max_turns=3)
        triage_facts = [{"pid": 4120, "process": "powershell.exe"}]
        engine.generate_initial_hypotheses(triage_facts)

        ledger = engine.execute_bounded_loop()
        assert len(ledger.turns) > 0
        assert len(ledger.turns) <= 3

        # Ledger state saved
        state_file = Path(td) / "investigation_ledger.json"
        assert state_file.is_file()

