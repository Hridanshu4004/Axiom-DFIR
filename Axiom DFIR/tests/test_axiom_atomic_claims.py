"""Tests for AXIOM DFIR Atomic Claim Validation Engine (Phase II)."""

from axiom_dfir.atomic_claims import (
    AtomicClaim,
    AtomicClaimValidator,
    RuleProcessRelationship,
    RuleHashMatch,
    RuleSocketAttribution,
    RuleTimestampConsistency,
    RuleUserLogon,
)
from axiom_dfir.validation import ValidationStatus


def test_rule_process_relationship_verified_and_contradicted():
    rule = RuleProcessRelationship()
    context = {
        "pids": {
            4120: {"name": "powershell.exe", "ppid": 1024},
            1024: {"name": "explorer.exe", "ppid": 800},
        }
    }

    # Verified claim
    c1 = AtomicClaim(
        claim_id="CLM-01",
        claim_type="PROCESS_SPAWN",
        subject="process:powershell.exe:4120",
        predicate="SPAWNED_BY",
        object="process:explorer.exe:1024",
    )
    status, conf, explanation = rule.evaluate(c1, context)
    assert status == ValidationStatus.VERIFIED
    assert conf == 1.0
    assert "confirmed spawned by PPID 1024" in explanation

    # Contradicted claim (claimed PPID 9999 instead of real 1024)
    c2 = AtomicClaim(
        claim_id="CLM-02",
        claim_type="PROCESS_SPAWN",
        subject="process:powershell.exe:4120",
        predicate="SPAWNED_BY",
        object="process:svchost.exe:9999",
    )
    status2, conf2, explanation2 = rule.evaluate(c2, context)
    assert status2 == ValidationStatus.CONTRADICTED
    assert conf2 == 0.0
    assert "was spawned by PPID 1024, not claimed PPID 9999" in explanation2


def test_rule_socket_attribution():
    rule = RuleSocketAttribution()
    context = {
        "connections": [
            {"remote_ip": "192.168.1.50", "remote_port": 4444, "pid": 4120},
        ]
    }

    # Verified connection
    c1 = AtomicClaim(
        claim_id="CLM-03",
        claim_type="NETWORK_CONNECTION",
        subject="process:powershell.exe:4120",
        predicate="CONNECTED_TO",
        object="socket:192.168.1.50:4444",
    )
    status, conf, _ = rule.evaluate(c1, context)
    assert status == ValidationStatus.VERIFIED

    # Contradicted connection (connection owned by different PID)
    c2 = AtomicClaim(
        claim_id="CLM-04",
        claim_type="NETWORK_CONNECTION",
        subject="process:malware.exe:8888",
        predicate="CONNECTED_TO",
        object="socket:192.168.1.50:4444",
    )
    status2, conf2, explanation2 = rule.evaluate(c2, context)
    assert status2 == ValidationStatus.CONTRADICTED
    assert "owned by PID 4120, not claimed PID 8888" in explanation2


def test_rule_timestamp_consistency():
    rule = RuleTimestampConsistency()
    context = {
        "timestamps": {
            "process:parent": "2026-10-30T04:10:00Z",
            "process:child": "2026-10-30T04:15:00Z",
        }
    }

    # Verified: child happened after parent
    c1 = AtomicClaim(
        claim_id="CLM-05",
        claim_type="TIMESTAMP_ORDER",
        subject="process:child",
        predicate="OBSERVED_AFTER",
        object="process:parent",
    )
    status, _, _ = rule.evaluate(c1, context)
    assert status == ValidationStatus.VERIFIED

    # Contradicted: parent happened after child is false
    c2 = AtomicClaim(
        claim_id="CLM-06",
        claim_type="TIMESTAMP_ORDER",
        subject="process:parent",
        predicate="OBSERVED_AFTER",
        object="process:child",
    )
    status2, _, _ = rule.evaluate(c2, context)
    assert status2 == ValidationStatus.CONTRADICTED


def test_atomic_claim_validator_batch():
    validator = AtomicClaimValidator()
    context = {
        "pids": {4120: {"name": "powershell.exe", "ppid": 1024}},
        "hashes": ["deadbeefdeadbeefdeadbeefdeadbeefdeadbeef"],
        "connections": [{"remote_ip": "192.168.1.50", "remote_port": 4444, "pid": 4120}],
    }
    claims = [
        AtomicClaim(
            claim_id="C1",
            claim_type="PROCESS_SPAWN",
            subject="process:powershell.exe:4120",
            predicate="SPAWNED_BY",
            object="process:explorer.exe:1024",
        ),
        AtomicClaim(
            claim_id="C2",
            claim_type="FILE_HASH",
            subject="binary:backdoor.exe",
            predicate="HAS_HASH",
            object="hash:deadbeefdeadbeefdeadbeefdeadbeefdeadbeef",
        ),
    ]

    results = validator.validate_claims_batch(claims, context)
    assert len(results) == 2
    assert all(r.status == ValidationStatus.VERIFIED for r in results)

