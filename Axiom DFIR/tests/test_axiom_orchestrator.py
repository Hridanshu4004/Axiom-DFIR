"""Unit tests for AXIOM DFIR Autonomous Investigation Orchestrator (Phase 2.3).

Validates:
  - 15-stage state machine transitions.
  - State persistence to disk.
  - Multi-format report generation (JSON, Markdown, HTML).
  - Provenance and evidence traceability.
"""

from __future__ import annotations

import os
import pytest
from pathlib import Path
from axiom_dfir.orchestrator import AxiomOrchestrator, InvestigationStage


def test_orchestrator_stage_progression(tmp_path: Path):
    """Test executing the 15-stage pipeline on sample test evidence."""
    os.environ["AXIOM_MOCK_NEBIUS"] = "1"
    evidence_dir = tmp_path / "case_evidence"
    evidence_dir.mkdir()
    sample_file = evidence_dir / "sample_artifact.json"
    sample_file.write_text('{"event": "test"}', encoding="utf-8")

    state_dir = tmp_path / "state"

    orch = AxiomOrchestrator(
        case_id="CASE-TEST-ORCH",
        evidence_path=evidence_dir,
        state_dir=state_dir,
    )

    success = orch.execute_all_stages()
    assert success is True
    assert orch.context.status == "COMPLETED"
    assert orch.context.current_stage == InvestigationStage.STAGE_15_CASE_COMPLETION

    # Verify generated report files exist
    assert (state_dir / "investigation_report.json").is_file()
    assert (state_dir / "investigation_report.md").is_file()
    assert (state_dir / "investigation_report.html").is_file()
    assert (state_dir / "investigation_state.json").is_file()
    assert (state_dir / "evidence_manifest.json").is_file()


def test_orchestrator_resumable_state(tmp_path: Path):
    """Test that an interrupted investigation can resume from its last completed stage."""
    os.environ["AXIOM_MOCK_NEBIUS"] = "1"
    evidence_dir = tmp_path / "resume_evidence"
    evidence_dir.mkdir()
    (evidence_dir / "artifact.log").write_text("log data", encoding="utf-8")
    state_dir = tmp_path / "state_resume"

    # Run first 2 stages only
    orch1 = AxiomOrchestrator(
        case_id="CASE-RESUME",
        evidence_path=evidence_dir,
        state_dir=state_dir,
    )
    orch1.run_stage(InvestigationStage.STAGE_01_CASE_INITIALIZATION)
    orch1.run_stage(InvestigationStage.STAGE_02_EVIDENCE_INGESTION)

    # Instantiate new orchestrator pointing to same state_dir
    orch2 = AxiomOrchestrator(
        case_id="CASE-RESUME",
        evidence_path=evidence_dir,
        state_dir=state_dir,
    )
    assert orch2.context.current_stage == InvestigationStage.STAGE_02_EVIDENCE_INGESTION
    assert orch2.context.stage_history["CASE_INITIALIZATION"].status == "COMPLETED"
    assert orch2.context.stage_history["EVIDENCE_INGESTION"].status == "COMPLETED"

