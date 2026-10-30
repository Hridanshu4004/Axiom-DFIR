"""AXIOM DFIR - Adaptive Hypothesis Engine (Phase II).

Structured hypothesis models, falsification-first reasoning, competing hypothesis
tracking, and persistent investigation ledger.

Core principle:
    THE AI MAY PROPOSE A HYPOTHESIS, BUT ONLY DETERMINISTIC FORENSIC EVIDENCE
    CAN CONFIRM OR REFUTE IT.
"""

from __future__ import annotations

import enum
import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger("axiom_dfir.hypothesis")


class HypothesisStatus(str, enum.Enum):
    OPEN = "OPEN"
    TESTING = "TESTING"
    CONFIRMED = "CONFIRMED"
    REFUTED = "REFUTED"
    INCONCLUSIVE = "INCONCLUSIVE"


@dataclass
class EvidenceCitation:
    """Explicit pointer to a forensic artifact backing or contradicting a hypothesis."""
    evidence_id: str
    artifact_type: str
    source_path: str
    line_or_offset: Optional[str] = None
    sha256_digest: Optional[str] = None
    description: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> EvidenceCitation:
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class Hypothesis:
    """Structured hypothesis representing an investigative proposition."""
    hypothesis_id: str
    title: str
    description: str
    entities: List[str] = field(default_factory=list)
    expected_observations: List[str] = field(default_factory=list)
    supporting_evidence: List[EvidenceCitation] = field(default_factory=list)
    contradicting_evidence: List[EvidenceCitation] = field(default_factory=list)
    missing_evidence: List[str] = field(default_factory=list)
    falsification_tests: List[str] = field(default_factory=list)
    confidence_score: float = 0.5  # 0.0 (fully refuted) to 1.0 (fully confirmed)
    status: HypothesisStatus = HypothesisStatus.OPEN
    competing_hypotheses: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    resolution_reason: Optional[str] = None

    def add_supporting(self, citation: EvidenceCitation | Dict[str, Any]) -> None:
        if isinstance(citation, dict):
            citation = EvidenceCitation.from_dict(citation)
        self.supporting_evidence.append(citation)
        self.updated_at = datetime.now(timezone.utc).isoformat()
        self._recompute_confidence()

    def add_contradicting(self, citation: EvidenceCitation | Dict[str, Any]) -> None:
        if isinstance(citation, dict):
            citation = EvidenceCitation.from_dict(citation)
        self.contradicting_evidence.append(citation)
        self.updated_at = datetime.now(timezone.utc).isoformat()
        self._recompute_confidence()

    def _recompute_confidence(self) -> None:
        """Heuristic confidence based on balance of supporting vs contradicting citations."""
        n_sup = len(self.supporting_evidence)
        n_con = len(self.contradicting_evidence)
        if n_sup == 0 and n_con == 0:
            self.confidence_score = 0.5
            return
        total = n_sup + (n_con * 2)  # Contradicting evidence carries heavier weight (falsification-first)
        self.confidence_score = round(n_sup / (total + 0.001), 3)

    def evaluate_status(self, min_supporting_for_confirmation: int = 2) -> HypothesisStatus:
        """Deterministically evaluates status based on citations.

        Falsification rule: Any strong contradicting evidence directly REFUTES
        the hypothesis unless corroborated by counter-forensics.
        """
        if len(self.contradicting_evidence) > 0:
            self.status = HypothesisStatus.REFUTED
            self.resolution_reason = f"Refuted by {len(self.contradicting_evidence)} contradicting evidence citations."
            return self.status

        if len(self.supporting_evidence) >= min_supporting_for_confirmation:
            self.status = HypothesisStatus.CONFIRMED
            self.resolution_reason = f"Confirmed with {len(self.supporting_evidence)} corroborating evidence citations."
            return self.status

        if len(self.supporting_evidence) > 0:
            self.status = HypothesisStatus.TESTING
            return self.status

        self.status = HypothesisStatus.OPEN
        return self.status

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["status"] = self.status.value
        d["supporting_evidence"] = [e.to_dict() if hasattr(e, "to_dict") else e for e in self.supporting_evidence]
        d["contradicting_evidence"] = [e.to_dict() if hasattr(e, "to_dict") else e for e in self.contradicting_evidence]
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Hypothesis:
        data_copy = dict(data)
        if "status" in data_copy and isinstance(data_copy["status"], str):
            data_copy["status"] = HypothesisStatus(data_copy["status"])
        if "supporting_evidence" in data_copy:
            data_copy["supporting_evidence"] = [
                EvidenceCitation.from_dict(e) if isinstance(e, dict) else e
                for e in data_copy["supporting_evidence"]
            ]
        if "contradicting_evidence" in data_copy:
            data_copy["contradicting_evidence"] = [
                EvidenceCitation.from_dict(e) if isinstance(e, dict) else e
                for e in data_copy["contradicting_evidence"]
            ]
        return cls(**{k: v for k, v in data_copy.items() if k in cls.__dataclass_fields__})


class InvestigationLedger:
    """Thread-safe persistent ledger tracking all hypotheses and investigation turns."""

    def __init__(self, case_id: str, state_path: Optional[Path | str] = None, max_turns: int = 5) -> None:
        self.case_id = case_id
        self.state_path = Path(state_path) if state_path else None
        self.max_turns = max_turns
        self.current_turn = 0
        self.hypotheses: Dict[str, Hypothesis] = {}
        self.turns: List[Dict[str, Any]] = []

    def register_hypothesis(self, hypothesis: Hypothesis) -> None:
        """Adds a hypothesis to the ledger."""
        self.hypotheses[hypothesis.hypothesis_id] = hypothesis
        logger.info("Hypothesis registered: [%s] %s", hypothesis.hypothesis_id, hypothesis.title)
        self.persist()

    def get_hypothesis(self, hypothesis_id: str) -> Optional[Hypothesis]:
        return self.hypotheses.get(hypothesis_id)

    def get_open_hypotheses(self) -> List[Hypothesis]:
        return [h for h in self.hypotheses.values() if h.status in (HypothesisStatus.OPEN, HypothesisStatus.TESTING)]

    def record_turn(
        self,
        turn_number: int,
        targeted_hypothesis_id: str,
        tool_selected: str,
        investigative_inquiry: str,
        observations: List[Dict[str, Any]],
        notes: str = "",
    ) -> None:
        turn_record = {
            "turn_number": turn_number,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "targeted_hypothesis": targeted_hypothesis_id,
            "tool_selected": tool_selected,
            "inquiry": investigative_inquiry,
            "observations_count": len(observations),
            "observations": observations,
            "notes": notes,
        }
        self.turns.append(turn_record)
        self.current_turn = turn_number
        logger.info("Turn %d recorded for hypothesis %s with tool %s", turn_number, targeted_hypothesis_id, tool_selected)
        self.persist()

    def resolve_competing(self, winning_id: str, losing_id: str, reason: str) -> None:
        """If one hypothesis is confirmed, formally refutes or deprioritizes its competing hypothesis."""
        winner = self.get_hypothesis(winning_id)
        loser = self.get_hypothesis(losing_id)
        if winner and loser:
            loser.status = HypothesisStatus.REFUTED
            loser.resolution_reason = f"Refuted by competing hypothesis {winning_id}: {reason}"
            loser.confidence_score = 0.0
            loser.updated_at = datetime.now(timezone.utc).isoformat()
            logger.info("Hypothesis %s refuted by competing hypothesis %s", losing_id, winning_id)
            self.persist()

    def persist(self) -> None:
        if not self.state_path:
            return
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.state_path.with_suffix(".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)
        tmp.replace(self.state_path)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "case_id": self.case_id,
            "current_turn": self.current_turn,
            "max_turns": self.max_turns,
            "hypotheses": {k: v.to_dict() for k, v in self.hypotheses.items()},
            "turns": self.turns,
            "summary": self.summary(),
        }

    @classmethod
    def load(cls, path: Path | str) -> InvestigationLedger:
        p = Path(path)
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
        ledger = cls(case_id=data["case_id"], state_path=p, max_turns=data.get("max_turns", 5))
        ledger.current_turn = data.get("current_turn", 0)
        ledger.turns = data.get("turns", [])
        for k, v in data.get("hypotheses", {}).items():
            ledger.hypotheses[k] = Hypothesis.from_dict(v)
        return ledger

    def summary(self) -> Dict[str, Any]:
        counts = {s.value: 0 for s in HypothesisStatus}
        for h in self.hypotheses.values():
            counts[h.status.value] += 1
        return {
            "total_hypotheses": len(self.hypotheses),
            "status_breakdown": counts,
            "open_count": counts[HypothesisStatus.OPEN.value] + counts[HypothesisStatus.TESTING.value],
            "confirmed_count": counts[HypothesisStatus.CONFIRMED.value],
            "refuted_count": counts[HypothesisStatus.REFUTED.value],
            "turns_executed": len(self.turns),
        }

