"""Unit tests for AXIOM DFIR Deterministic Claim Validation Engine (Phase 2.5).

Proves that:
  - Correct claims are VERIFIED with high confidence.
  - Fabricated PIDs and missing evidence are UNVERIFIED.
  - Incorrect hashes are rejected.
  - Conflicting parent-child process relationships are CONTRADICTED.
  - LLM hallucinations cannot manufacture confirmed security findings.
"""

from __future__ import annotations

import pytest
from axiom_dfir.validation import ClaimValidationEngine, ValidationStatus


@pytest.fixture
def indexed_ground_truth():
    """Synthetic forensic evidence ground truth for test verification."""
    ref_set = {
        "pids": {
            1024: {"name": "explorer.exe", "ppid": 800},
            4120: {"name": "powershell.exe", "ppid": 1024},
            5000: {"name": "cmd.exe", "ppid": 4120},
        },
        "hashes": [
            "a1b2c3d4e5f678901234567890abcdef1234567890abcdef1234567890abcdef",
        ],
        "connections": [
            {"remote_ip": "192.168.1.50", "remote_port": 4444},
            {"remote_ip": "10.0.0.1", "remote_port": 80},
        ],
        "files": [
            "c:\\windows\\system32\\windowspowershell\\v1.0\\powershell.exe",
        ],
    }
    return ClaimValidationEngine(reference_set=ref_set)


def test_valid_claim_is_verified(indexed_ground_truth: ClaimValidationEngine):
    """Test that a finding matching authentic evidence records is marked VERIFIED."""
    finding = {
        "finding_id": "FIND-TRUE-01",
        "title": "Legitimate PowerShell Launch",
        "claims": {
            "pid": 4120,
            "process": "powershell.exe",
            "parent_pid": 1024,
            "destination_ip": "192.168.1.50",
            "destination_port": 4444,
        },
        "evidence_refs": ["EV-MEM-01", "EV-NET-01"],
    }
    result = indexed_ground_truth.validate_finding(finding)
    assert result.validation_status == ValidationStatus.VERIFIED
    assert result.confidence >= 0.90
    assert len(result.corroborating_evidence_refs) > 0
    assert len(result.contradicting_evidence_refs) == 0


def test_hallucinated_pid_is_unverified(indexed_ground_truth: ClaimValidationEngine):
    """Test that an AI claim citing a non-existent PID is rejected as UNVERIFIED."""
    finding = {
        "finding_id": "FIND-HALLUC-01",
        "title": "Hallucinated Trojan Execution",
        "claims": {
            "pid": 9999,  # Does not exist
            "process": "evil_trojan.exe",
        },
        "evidence_refs": ["EV-MEM-01"],
    }
    result = indexed_ground_truth.validate_finding(finding)
    assert result.validation_status == ValidationStatus.UNVERIFIED
    assert result.confidence <= 0.20
    assert "not found in active or terminated process lists" in result.checks[0].detail


def test_wrong_parent_pid_is_contradicted(indexed_ground_truth: ClaimValidationEngine):
    """Test that claiming an incorrect parent process is caught and CONTRADICTED."""
    finding = {
        "finding_id": "FIND-CONTRADICT-01",
        "title": "Spoofed Parent-Child Relationship",
        "claims": {
            "pid": 4120,
            "parent_pid": 999,  # In reality, PPID is 1024!
        },
        "evidence_refs": ["EV-MEM-01"],
    }
    result = indexed_ground_truth.validate_finding(finding)
    assert result.validation_status == ValidationStatus.CONTRADICTED
    assert result.confidence == 0.0
    assert len(result.contradicting_evidence_refs) > 0


def test_incorrect_file_hash_is_rejected(indexed_ground_truth: ClaimValidationEngine):
    """Test that a fabricated or modified hash fails verification."""
    finding = {
        "finding_id": "FIND-FAKE-HASH",
        "title": "Fake Hash Attribution",
        "claims": {
            "hash": "deadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef",
        },
    }
    result = indexed_ground_truth.validate_finding(finding)
    assert result.validation_status == ValidationStatus.UNVERIFIED


def test_incorrect_network_attribution_is_rejected(indexed_ground_truth: ClaimValidationEngine):
    """Test that connections not found in evidence cannot be confirmed."""
    finding = {
        "finding_id": "FIND-FAKE-NET",
        "title": "Fabricated C2 IP Connection",
        "claims": {
            "destination_ip": "203.0.113.99",
            "destination_port": 8080,
        },
    }
    result = indexed_ground_truth.validate_finding(finding)
    assert result.validation_status == ValidationStatus.UNVERIFIED

