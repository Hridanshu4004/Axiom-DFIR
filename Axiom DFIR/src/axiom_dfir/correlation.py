"""AXIOM DFIR - Evidence Correlation & Attack Reconstruction Subsystem (Phase 4).

Reconstructs complete cyber incidents from disparate forensic artifacts:
  - Directed Evidence Relationship Graph (Processes, Users, Files, IPs, Sockets, Events).
  - Chronological normalized timeline with timezone awareness.
  - MITRE ATT&CK technique mapping with explicit evidence traceability.
"""

from __future__ import annotations

import enum
import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger("axiom_dfir.correlation")


class EdgeCausalityType(str, enum.Enum):
    CAUSAL = "CAUSAL"          # Deterministic causal relationship (e.g. SPAWNED, INJECTED_INTO)
    TEMPORAL = "TEMPORAL"      # Temporal sequence only (e.g. OBSERVED_BEFORE)
    EVIDENTIARY = "EVIDENTIARY"  # Hypothesis/claim linking (e.g. EVIDENCE_FOR, TESTS_HYPOTHESIS)


@dataclass
class GraphNode:
    node_id: str
    node_type: str  # PROCESS, USER, FILE, IP_ADDRESS, CONNECTION, REGISTRY, EVENT, FINDING, HYPOTHESIS, MITRE_TECHNIQUE
    label: str
    attributes: Dict[str, Any] = field(default_factory=dict)
    evidence_ref: str = ""


@dataclass
class GraphEdge:
    edge_id: str
    source_node_id: str
    target_node_id: str
    relationship: str  # SPAWNED, ACCESSED, CONNECTED_TO, AUTHENTICATED_AS, CREATED, EXECUTED, OBSERVED_BEFORE, TESTS_HYPOTHESIS
    causality_type: EdgeCausalityType = EdgeCausalityType.CAUSAL
    timestamp: Optional[str] = None
    evidence_ref: str = ""
    confidence: float = 1.0
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TimelineEvent:
    timestamp: str
    event_type: str
    source_entity: str
    description: str
    evidence_ref: str
    is_malicious_indicator: bool = False
    mitre_technique_id: Optional[str] = None
    mitre_technique_name: Optional[str] = None


class IncidentReconstructionGraph:
    """Directed graph representing multi-source forensic incident correlations."""

    def __init__(self) -> None:
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: Dict[str, GraphEdge] = {}
        self.timeline_events: List[TimelineEvent] = []

    def add_node(
        self,
        node_id: str,
        node_type: str,
        label: str,
        attributes: Optional[Dict[str, Any]] = None,
        evidence_ref: str = "",
    ) -> GraphNode:
        if node_id not in self.nodes:
            self.nodes[node_id] = GraphNode(
                node_id=node_id,
                node_type=node_type,
                label=label,
                attributes=attributes or {},
                evidence_ref=evidence_ref,
            )
        return self.nodes[node_id]

    def add_edge(
        self,
        source_id: str,
        target_id: str,
        relationship: str,
        causality_type: EdgeCausalityType = EdgeCausalityType.CAUSAL,
        timestamp: Optional[str] = None,
        evidence_ref: str = "",
        confidence: float = 1.0,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> GraphEdge:
        edge_id = f"{source_id}->{relationship}->{target_id}"
        if edge_id not in self.edges:
            self.edges[edge_id] = GraphEdge(
                edge_id=edge_id,
                source_node_id=source_id,
                target_node_id=target_id,
                relationship=relationship,
                causality_type=causality_type,
                timestamp=timestamp,
                evidence_ref=evidence_ref,
                confidence=confidence,
                attributes=attributes or {},
            )
        return self.edges[edge_id]

    def detect_causal_cycles(self) -> List[List[str]]:
        """Detects any cycles within directed CAUSAL edges (e.g. impossible PPID loops)."""
        adj: Dict[str, List[str]] = {}
        for edge in self.edges.values():
            if edge.causality_type == EdgeCausalityType.CAUSAL:
                adj.setdefault(edge.source_node_id, []).append(edge.target_node_id)

        visited: Set[str] = set()
        rec_stack: Set[str] = set()
        cycles: List[List[str]] = []

        def dfs(node: str, path: List[str]) -> None:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in adj.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor, list(path))
                elif neighbor in rec_stack:
                    # Found cycle
                    cycle_start = path.index(neighbor)
                    cycles.append(path[cycle_start:] + [neighbor])

            rec_stack.remove(node)

        for n in list(self.nodes.keys()):
            if n not in visited:
                dfs(n, [])

        return cycles

    def to_cytoscape_elements(self) -> List[Dict[str, Any]]:
        """Exports graph elements formatted for interactive web visualizers (Cytoscape.js)."""
        elements: List[Dict[str, Any]] = []
        for node in self.nodes.values():
            elements.append({
                "data": {
                    "id": node.node_id,
                    "label": node.label,
                    "type": node.node_type,
                    "evidence_ref": node.evidence_ref,
                    **node.attributes,
                }
            })
        for edge in self.edges.values():
            elements.append({
                "data": {
                    "id": edge.edge_id,
                    "source": edge.source_node_id,
                    "target": edge.target_node_id,
                    "label": edge.relationship,
                    "causality": edge.causality_type.value,
                    "confidence": edge.confidence,
                    "evidence_ref": edge.evidence_ref,
                }
            })
        return elements

    def add_timeline_event(
        self,
        timestamp: str,
        event_type: str,
        source_entity: str,
        description: str,
        evidence_ref: str,
        is_malicious: bool = False,
        mitre_id: Optional[str] = None,
        mitre_name: Optional[str] = None,
    ) -> None:
        self.timeline_events.append(
            TimelineEvent(
                timestamp=timestamp,
                event_type=event_type,
                source_entity=source_entity,
                description=description,
                evidence_ref=evidence_ref,
                is_malicious_indicator=is_malicious,
                mitre_technique_id=mitre_id,
                mitre_technique_name=mitre_name,
            )
        )

    def get_sorted_timeline(self) -> List[Dict[str, Any]]:
        """Returns chronologically ordered timeline events."""
        def parse_ts(ts: str) -> float:
            try:
                # ISO-8601 parsing with timezone tolerance
                clean = ts.replace("Z", "+00:00")
                return datetime.fromisoformat(clean).timestamp()
            except Exception:
                return 0.0

        sorted_events = sorted(self.timeline_events, key=lambda e: parse_ts(e.timestamp))
        return [asdict(e) for e in sorted_events]

    def to_dict(self) -> Dict[str, Any]:
        edges_dict = {}
        for k, v in self.edges.items():
            ed = asdict(v)
            ed["causality_type"] = v.causality_type.value
            edges_dict[k] = ed
        return {
            "node_count": len(self.nodes),
            "edge_count": len(self.edges),
            "nodes": {k: asdict(v) for k, v in self.nodes.items()},
            "edges": edges_dict,
            "timeline": self.get_sorted_timeline(),
            "cytoscape": self.to_cytoscape_elements(),
        }


def reconstruct_incident_from_artifacts(
    findings: List[Dict[str, Any]],
    tool_records: Dict[str, Any],
    manifest: Optional[Dict[str, Any]] = None,
) -> IncidentReconstructionGraph:
    """Builds an incident graph and timeline from validated findings and raw tool facts."""
    graph = IncidentReconstructionGraph()

    # Ingest tool records
    for tool_name, result in tool_records.items():
        recs = result.get("records") if isinstance(result, dict) else None
        if not isinstance(recs, list):
            continue

        for r in recs:
            if not isinstance(r, dict):
                continue

            # Process nodes
            pid = r.get("pid") or r.get("PID")
            proc_name = r.get("process") or r.get("ImageFileName") or r.get("name") or "unknown"
            ppid = r.get("ppid") or r.get("PPID")
            ts = r.get("timestamp") or r.get("CreateTime") or datetime.now(timezone.utc).isoformat()

            if pid:
                node_id = f"proc_{pid}"
                graph.add_node(node_id, "PROCESS", f"{proc_name} (PID {pid})", attributes=r, evidence_ref=tool_name)
                graph.add_timeline_event(
                    timestamp=str(ts),
                    event_type="PROCESS_DISCOVERED",
                    source_entity=node_id,
                    description=f"Process {proc_name} (PID {pid}) discovered in {tool_name}",
                    evidence_ref=tool_name,
                )

                if ppid:
                    parent_node_id = f"proc_{ppid}"
                    graph.add_node(parent_node_id, "PROCESS", f"Parent PID {ppid}", evidence_ref=tool_name)
                    graph.add_edge(parent_node_id, node_id, "SPAWNED", timestamp=str(ts), evidence_ref=tool_name)

            # Network connection nodes
            remote_ip = r.get("remote_ip") or r.get("ForeignAddr") or r.get("dst_ip")
            remote_port = r.get("remote_port") or r.get("ForeignPort") or r.get("dst_port")
            if remote_ip and pid:
                ip_node_id = f"ip_{remote_ip}"
                graph.add_node(ip_node_id, "IP_ADDRESS", str(remote_ip), evidence_ref=tool_name)
                graph.add_edge(
                    f"proc_{pid}",
                    ip_node_id,
                    "CONNECTED_TO",
                    timestamp=str(ts),
                    evidence_ref=tool_name,
                    attributes={"port": remote_port},
                )
                graph.add_timeline_event(
                    timestamp=str(ts),
                    event_type="NETWORK_CONNECTION",
                    source_entity=f"proc_{pid}",
                    description=f"Process PID {pid} established connection to {remote_ip}:{remote_port}",
                    evidence_ref=tool_name,
                    is_malicious=True,
                    mitre_id="T1071",
                    mitre_name="Application Layer Protocol",
                )

    # Ingest validated findings
    for idx, f in enumerate(findings, start=1):
        f_id = f.get("finding_id", f"FIND-{idx:03d}")
        f_title = f.get("title", "Finding")
        f_node = graph.add_node(f_id, "FINDING", f_title, attributes=f, evidence_ref=str(f.get("evidence_refs", [])))

    return graph

