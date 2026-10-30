"""AXIOM DFIR - Open Cybersecurity Schema Framework (OCSF) Normalization Layer (Phase II).

Standardizes heterogeneous raw forensic evidence (EVTX, Volatility, Sysmon, Auditd)
into standard OCSF v1.1.0 JSON event schemas:
  - Class 1007: Process Activity (System Activity Category 1)
  - Class 4001: Network Activity (Network Activity Category 4)
  - Class 3002: Authentication (Identity & Access Management Category 3)
"""

from __future__ import annotations

import enum
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger("axiom_dfir.ocsf")


class OCSFClassUID(int, enum.Enum):
    PROCESS_ACTIVITY = 1007
    NETWORK_ACTIVITY = 4001
    AUTHENTICATION = 3002


class OCSFCategoryUID(int, enum.Enum):
    SYSTEM_ACTIVITY = 1
    IDENTITY_ACCESS = 3
    NETWORK_ACTIVITY = 4


@dataclass
class OCSFMetadata:
    version: str = "1.1.0"
    product: Dict[str, str] = field(default_factory=lambda: {
        "name": "AXIOM DFIR",
        "vendor_name": "AXIOM",
        "version": "1.0.0",
    })
    profiles: List[str] = field(default_factory=lambda: ["security_control"])


@dataclass
class OCSFProcessActivity:
    """OCSF Class 1007: Process Activity."""
    class_uid: int = OCSFClassUID.PROCESS_ACTIVITY.value
    category_uid: int = OCSFCategoryUID.SYSTEM_ACTIVITY.value
    class_name: str = "Process Activity"
    activity_id: int = 1  # 1: Launch, 2: Terminate
    activity_name: str = "Launch"
    time: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: OCSFMetadata = field(default_factory=OCSFMetadata)
    process: Dict[str, Any] = field(default_factory=dict)
    parent_process: Optional[Dict[str, Any]] = None
    actor: Optional[Dict[str, Any]] = None
    evidence_ref: str = ""

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["metadata"] = asdict(self.metadata)
        return d


@dataclass
class OCSFNetworkActivity:
    """OCSF Class 4001: Network Activity."""
    class_uid: int = OCSFClassUID.NETWORK_ACTIVITY.value
    category_uid: int = OCSFCategoryUID.NETWORK_ACTIVITY.value
    class_name: str = "Network Activity"
    activity_id: int = 1  # 1: Open, 2: Close, 3: Traffic
    activity_name: str = "Open"
    time: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: OCSFMetadata = field(default_factory=OCSFMetadata)
    src_endpoint: Dict[str, Any] = field(default_factory=dict)
    dst_endpoint: Dict[str, Any] = field(default_factory=dict)
    connection_info: Dict[str, Any] = field(default_factory=dict)
    evidence_ref: str = ""

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["metadata"] = asdict(self.metadata)
        return d


@dataclass
class OCSFAuthentication:
    """OCSF Class 3002: Authentication."""
    class_uid: int = OCSFClassUID.AUTHENTICATION.value
    category_uid: int = OCSFCategoryUID.IDENTITY_ACCESS.value
    class_name: str = "Authentication"
    activity_id: int = 1  # 1: Logon, 2: Logoff
    activity_name: str = "Logon"
    status_id: int = 1    # 1: Success, 2: Failure
    status_name: str = "Success"
    time: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: OCSFMetadata = field(default_factory=OCSFMetadata)
    user: Dict[str, Any] = field(default_factory=dict)
    logon_type: str = "Interactive"
    evidence_ref: str = ""

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["metadata"] = asdict(self.metadata)
        return d


class OCSFNormalizer:
    """Translates arbitrary raw tool facts and artifact outputs into OCSF JSON events."""

    @staticmethod
    def normalize_process(raw: Dict[str, Any], evidence_ref: str = "") -> OCSFProcessActivity:
        pid = raw.get("pid") or raw.get("PID")
        ppid = raw.get("ppid") or raw.get("PPID")
        name = raw.get("process") or raw.get("ImageFileName") or raw.get("name") or "unknown"
        cmdline = raw.get("command_line") or raw.get("cmdline") or raw.get("CommandLine") or ""
        ts = raw.get("timestamp") or raw.get("CreateTime") or datetime.now(timezone.utc).isoformat()
        user_name = raw.get("user") or raw.get("UserName") or "SYSTEM"

        hashes = []
        if raw.get("sha256") or raw.get("hash"):
            h = raw.get("sha256") or raw.get("hash")
            hashes.append({"algorithm": "SHA-256", "value": h})

        proc_data = {
            "name": name,
            "pid": int(pid) if pid is not None else 0,
            "cmd_line": cmdline,
            "file": {"hashes": hashes} if hashes else {},
        }
        parent_proc = None
        if ppid is not None:
            parent_proc = {
                "name": raw.get("parent_name", "unknown"),
                "pid": int(ppid),
            }

        actor = {"user": {"name": str(user_name)}}

        return OCSFProcessActivity(
            time=str(ts),
            process=proc_data,
            parent_process=parent_proc,
            actor=actor,
            evidence_ref=evidence_ref,
        )

    @staticmethod
    def normalize_network(raw: Dict[str, Any], evidence_ref: str = "") -> OCSFNetworkActivity:
        src_ip = raw.get("src_ip") or raw.get("LocalAddr") or "127.0.0.1"
        src_port = raw.get("src_port") or raw.get("LocalPort") or 0
        dst_ip = raw.get("dst_ip") or raw.get("remote_ip") or raw.get("ForeignAddr") or "0.0.0.0"
        dst_port = raw.get("dst_port") or raw.get("remote_port") or raw.get("ForeignPort") or 0
        proto = raw.get("protocol") or raw.get("proto") or "TCP"
        ts = raw.get("timestamp") or datetime.now(timezone.utc).isoformat()

        return OCSFNetworkActivity(
            time=str(ts),
            src_endpoint={"ip": str(src_ip), "port": int(src_port) if src_port else 0},
            dst_endpoint={"ip": str(dst_ip), "port": int(dst_port) if dst_port else 0},
            connection_info={"protocol_name": str(proto).upper(), "direction": "Outbound"},
            evidence_ref=evidence_ref,
        )

    @staticmethod
    def normalize_authentication(raw: Dict[str, Any], evidence_ref: str = "") -> OCSFAuthentication:
        user = raw.get("target_username") or raw.get("user") or raw.get("TargetUserName") or "unknown"
        domain = raw.get("target_domain") or raw.get("domain") or ""
        logon_type = raw.get("logon_type") or "Interactive"
        is_success = raw.get("status", "SUCCESS") == "SUCCESS"
        ts = raw.get("timestamp") or datetime.now(timezone.utc).isoformat()

        return OCSFAuthentication(
            time=str(ts),
            status_id=1 if is_success else 2,
            status_name="Success" if is_success else "Failure",
            user={"name": str(user), "domain": str(domain)},
            logon_type=str(logon_type),
            evidence_ref=evidence_ref,
        )

    @classmethod
    def normalize_batch(cls, records: List[Dict[str, Any]], event_type: str, evidence_ref: str = "") -> List[Dict[str, Any]]:
        normalized: List[Dict[str, Any]] = []
        for r in records:
            if not isinstance(r, dict):
                continue
            if event_type.upper() in ("PROCESS", "PSTREE", "PSLIST"):
                normalized.append(cls.normalize_process(r, evidence_ref).to_dict())
            elif event_type.upper() in ("NETWORK", "NETSCAN", "CONNECTIONS"):
                normalized.append(cls.normalize_network(r, evidence_ref).to_dict())
            elif event_type.upper() in ("AUTH", "LOGON", "AUTHENTICATION"):
                normalized.append(cls.normalize_authentication(r, evidence_ref).to_dict())
            else:
                # Default generic normalization
                normalized.append(cls.normalize_process(r, evidence_ref).to_dict())
        return normalized

