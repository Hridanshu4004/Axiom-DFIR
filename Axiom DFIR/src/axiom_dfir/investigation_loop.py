"""AXIOM DFIR - Adaptive Investigation Loop (Phase II).

Implements bounded iterative investigation:
  - Dynamic hypothesis selection
  - Falsification-first inquiry generation
  - Tool selection and evidence collection
  - Hypothesis status evaluation (OPEN -> TESTING -> CONFIRMED / REFUTED)
  - Strict turn, budget, and timeout controls
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from axiom_dfir.hypothesis import (
    EvidenceCitation,
    Hypothesis,
    HypothesisStatus,
    InvestigationLedger,
)
from axiom_dfir.nebius import NebiusClient

logger = logging.getLogger("axiom_dfir.investigation_loop")


@dataclass
class InvestigationStep:
    hypothesis_id: str
    tool_name: str
    tool_arguments: Dict[str, Any]
    falsification_focus: str
    rationale: str


class AdaptiveInvestigationEngine:
    """Orchestrates an adaptive, evidence-driven investigation cycle."""

    def __init__(
        self,
        case_id: str,
        state_dir: Path | str,
        llm_client: Optional[NebiusClient] = None,
        tool_executor: Optional[Callable[[str, Dict[str, Any]], Dict[str, Any]]] = None,
        max_turns: int = 5,
        timeout_seconds: float = 300.0,
    ) -> None:
        self.case_id = case_id
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.llm_client = llm_client or NebiusClient()
        self.tool_executor = tool_executor or self._default_tool_executor
        self.max_turns = max_turns
        self.timeout_seconds = timeout_seconds

        ledger_path = self.state_dir / "investigation_ledger.json"
        if ledger_path.is_file():
            self.ledger = InvestigationLedger.load(ledger_path)
        else:
            self.ledger = InvestigationLedger(case_id=case_id, state_path=ledger_path, max_turns=max_turns)

    def _default_tool_executor(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback tool executor for unit testing or when external runner is not injected."""
        logger.info("Executing tool: %s with args %s", tool_name, args)
        return {
            "tool": tool_name,
            "status": "SUCCESS",
            "records": [
                {
                    "evidence_id": f"EV-{tool_name}-01",
                    "source": tool_name,
                    "summary": f"Observed artifact record from {tool_name}",
                    "raw_offset": "0x0041F0",
                }
            ],
        }

    def generate_initial_hypotheses(self, triage_facts: List[Dict[str, Any]]) -> List[Hypothesis]:
        """Generates initial structured hypotheses based on initial triage facts."""
        hypotheses: List[Hypothesis] = []

        # If triage facts contain process or network anomalies, generate primary and competing hypotheses
        pids = [f["pid"] for f in triage_facts if "pid" in f]
        primary_pid = pids[0] if pids else 4120

        # Primary Hypothesis: Malicious Execution
        hyp1 = Hypothesis(
            hypothesis_id="HYP-001",
            title=f"Malicious Process Execution (PID {primary_pid})",
            description=f"Process PID {primary_pid} is an unauthorized reverse shell spawned by an interactive session.",
            entities=[f"PROCESS-{primary_pid}", "NETWORK-PORT-4444"],
            expected_observations=[
                f"Parent process PID indicates abnormal spawn hierarchy",
                f"Network socket established to external IP on non-standard port",
                f"Command line contains encoded script or suspicious execution flags",
            ],
            missing_evidence=["Network connection table", "Command line string from memory/auditd"],
            falsification_tests=[
                f"Process was launched by legitimate Windows Update or Task Scheduler service",
                f"Binary hash matches known benign OS signature with clean digital certificate",
            ],
            status=HypothesisStatus.OPEN,
            competing_hypotheses=["HYP-002"],
        )

        # Competing Hypothesis: Benign Dual-Use Administration
        hyp2 = Hypothesis(
            hypothesis_id="HYP-002",
            title=f"Legitimate Dual-Use System Administration (PID {primary_pid})",
            description=f"Process PID {primary_pid} is legitimate administrative tooling run by an authorized administrator.",
            entities=[f"PROCESS-{primary_pid}", "USER-ADMIN"],
            expected_observations=[
                f"Interactive logon record precedes execution within 5 minutes",
                f"Standard administrative script in known sysadmin directory",
            ],
            missing_evidence=["Logon event 4624/4672", "User SID confirmation"],
            falsification_tests=[
                f"Destination IP is located in foreign known bulletproof hosting range",
                f"Process memory contains injected code or unbacked executable pages",
            ],
            status=HypothesisStatus.OPEN,
            competing_hypotheses=["HYP-001"],
        )

        self.ledger.register_hypothesis(hyp1)
        self.ledger.register_hypothesis(hyp2)
        hypotheses.extend([hyp1, hyp2])
        return hypotheses

    def plan_next_step(self, hypothesis: Hypothesis) -> InvestigationStep:
        """Determines the next forensic tool and falsification inquiry for a hypothesis."""
        tool_mapping = {
            "NETWORK-PORT": ("vol_netscan", {"protocol": "tcp"}),
            "PROCESS": ("vol_pstree", {"pid": 4120}),
            "MALFIND": ("vol_malfind", {"pid": 4120}),
            "AMCACHE": ("get_amcache", {}),
            "PREFETCH": ("parse_prefetch", {}),
        }

        # Select tool based on entities or missing evidence
        selected_tool = "vol_pstree"
        args: Dict[str, Any] = {"pid": 4120}

        for ent in hypothesis.entities:
            if "NETWORK" in ent:
                selected_tool = "vol_netscan"
                args = {"port": 4444}
                break
            elif "MALFIND" in ent or "INJECTION" in ent:
                selected_tool = "vol_malfind"
                args = {"pid": 4120}
                break

        falsification_target = (
            hypothesis.falsification_tests[0]
            if hypothesis.falsification_tests
            else "Verify if execution signature matches known benign baseline"
        )

        return InvestigationStep(
            hypothesis_id=hypothesis.hypothesis_id,
            tool_name=selected_tool,
            tool_arguments=args,
            falsification_focus=falsification_target,
            rationale=f"Testing hypothesis {hypothesis.hypothesis_id} by querying {selected_tool}",
        )

    def run_investigation_turn(self, turn_number: int) -> bool:
        """Executes a single adaptive investigation round. Returns True if further work needed."""
        open_hypotheses = self.ledger.get_open_hypotheses()
        if not open_hypotheses:
            logger.info("No open hypotheses remain. Investigation cycle complete.")
            return False

        # Prioritize OPEN before TESTING
        target_hyp = next((h for h in open_hypotheses if h.status == HypothesisStatus.OPEN), open_hypotheses[0])

        step = self.plan_next_step(target_hyp)
        logger.info(
            "Turn %d: Testing hypothesis %s using tool %s (Falsification: %s)",
            turn_number,
            target_hyp.hypothesis_id,
            step.tool_name,
            step.falsification_focus,
        )

        # Run tool
        tool_result = self.tool_executor(step.tool_name, step.tool_arguments)
        records = tool_result.get("records", [])

        # Ingest tool records as observations
        for rec in records:
            citation = EvidenceCitation(
                evidence_id=rec.get("evidence_id", f"EV-{turn_number}"),
                artifact_type=tool_result.get("tool", "FORENSIC_TOOL"),
                source_path=f"artifacts/{step.tool_name}.output",
                line_or_offset=rec.get("raw_offset", "0x0"),
                description=rec.get("summary", "Forensic observation"),
            )
            target_hyp.add_supporting(citation)

        # Evaluate hypothesis status
        old_status = target_hyp.status
        new_status = target_hyp.evaluate_status(min_supporting_for_confirmation=2)
        logger.info("Hypothesis %s status changed: %s -> %s", target_hyp.hypothesis_id, old_status, new_status)

        # If confirmed, resolve competing hypotheses
        if new_status == HypothesisStatus.CONFIRMED:
            for comp_id in target_hyp.competing_hypotheses:
                self.ledger.resolve_competing(
                    winning_id=target_hyp.hypothesis_id,
                    losing_id=comp_id,
                    reason=f"Evidence confirmed {target_hyp.hypothesis_id}",
                )

        # Record turn in ledger
        self.ledger.record_turn(
            turn_number=turn_number,
            targeted_hypothesis_id=target_hyp.hypothesis_id,
            tool_selected=step.tool_name,
            investigative_inquiry=step.falsification_focus,
            observations=records,
            notes=f"Turn {turn_number} completed. New status: {new_status.value}",
        )
        return True

    def execute_bounded_loop(self) -> InvestigationLedger:
        """Executes the full bounded investigation loop within limits."""
        start_time = time.time()
        logger.info("Starting adaptive investigation loop (max_turns=%d, timeout=%.1fs)", self.max_turns, self.timeout_seconds)

        for turn in range(1, self.max_turns + 1):
            if time.time() - start_time > self.timeout_seconds:
                logger.warning("Investigation loop reached timeout of %.1fs. Halting.", self.timeout_seconds)
                break

            should_continue = self.run_investigation_turn(turn)
            if not should_continue:
                break

        # Mark any remaining OPEN/TESTING hypotheses as INCONCLUSIVE
        for hyp in self.ledger.get_open_hypotheses():
            hyp.status = HypothesisStatus.INCONCLUSIVE
            hyp.resolution_reason = "Turn limit reached before definitive confirmation or refutation."

        self.ledger.persist()
        logger.info("Investigation loop finished. Summary: %s", self.ledger.summary())
        return self.ledger

