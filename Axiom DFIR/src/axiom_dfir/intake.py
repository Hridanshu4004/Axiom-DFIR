"""AXIOM DFIR - Evidence Intake Engine (Phase 2.1).

Responsible for:
  - Discovering and cataloging all forensic artifacts (EVTX, memory dumps, disk images,
    JSON/CSV logs, process records, network connections, file metadata).
  - Calculating initial SHA256 cryptographic fingerprints.
  - Generating unique, durable Evidence IDs (EV-001, EV-002, ...).
  - Enforcing strict read-only evidence access.
  - Emitting an immutable Evidence Manifest (evidence_manifest.json) before investigation.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import stat
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger("axiom_dfir.intake")

# Supported forensic evidence extensions and signatures
EVIDENCE_TYPE_MAP = {
    ".raw": "MEMORY_IMAGE",
    ".vmem": "MEMORY_IMAGE",
    ".dmp": "MEMORY_IMAGE",
    ".bin": "MEMORY_IMAGE",
    ".lime": "MEMORY_IMAGE",
    ".img": "DISK_IMAGE",
    ".dd": "DISK_IMAGE",
    ".e01": "DISK_IMAGE",
    ".vmdk": "DISK_IMAGE",
    ".vhdx": "DISK_IMAGE",
    ".evtx": "WINDOWS_EVENT_LOG",
    ".json": "JSON_FORENSIC_ARTIFACT",
    ".jsonl": "JSONL_FORENSIC_STREAM",
    ".csv": "CSV_FORENSIC_TABLE",
    ".log": "TEXT_LOG_ARTIFACT",
    ".txt": "TEXT_REPORT_ARTIFACT",
    ".pf": "PREFETCH_ARTIFACT",
    ".hve": "REGISTRY_HIVE",
    "amcache.hve": "AMCACHE_REGISTRY_HIVE",
    "system": "REGISTRY_HIVE",
    "software": "REGISTRY_HIVE",
    "sam": "REGISTRY_HIVE",
    "security": "REGISTRY_HIVE",
    "ntuser.dat": "USER_REGISTRY_HIVE",
}


@dataclass
class EvidenceItem:
    evidence_id: str
    original_filename: str
    source_path: str
    artifact_type: str
    sha256_hash: str
    size_bytes: int
    acquisition_timestamp: str
    is_read_only: bool
    parsing_status: str
    provenance: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class EvidenceManifest:
    manifest_id: str
    case_id: str
    created_at: str
    evidence_root: str
    item_count: int
    total_bytes: int
    items: List[EvidenceItem] = field(default_factory=list)
    tamper_evident_seal: str = ""

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        return d

    def save_json(self, path: Path) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        # Calculate seal over the serialized items
        raw_payload = json.dumps([item.to_dict() for item in self.items], sort_keys=True)
        self.tamper_evident_seal = hashlib.sha256(raw_payload.encode("utf-8")).hexdigest()
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)
        logger.info("Saved evidence manifest (%d items, seal=%s) to %s", len(self.items), self.tamper_evident_seal[:12], path)
        return path


def compute_sha256(file_path: Path, max_bytes: Optional[int] = None) -> str:
    """Computes SHA256 digest in chunks using strictly read-only binary streaming."""
    hasher = hashlib.sha256()
    bytes_read = 0
    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(1024 * 1024)  # 1MB buffer
            if not chunk:
                break
            if max_bytes and (bytes_read + len(chunk) > max_bytes):
                remaining = max_bytes - bytes_read
                hasher.update(chunk[:remaining])
                break
            hasher.update(chunk)
            bytes_read += len(chunk)
    return hasher.hexdigest()


def detect_artifact_type(file_path: Path) -> str:
    """Infers forensic artifact category from filename, extension, or header signature."""
    lower_name = file_path.name.lower()
    suffix = file_path.suffix.lower()

    if lower_name in EVIDENCE_TYPE_MAP:
        return EVIDENCE_TYPE_MAP[lower_name]
    if suffix in EVIDENCE_TYPE_MAP:
        return EVIDENCE_TYPE_MAP[suffix]

    # Content signature check on first 16 bytes
    try:
        with open(file_path, "rb") as f:
            magic = f.read(16)
            if magic.startswith(b"ElfFile\x00"):
                return "WINDOWS_EVENT_LOG"  # EVTX magic header
            if magic.startswith(b"regf"):
                return "REGISTRY_HIVE"  # Windows registry header
            if magic.startswith(b"FILE") or magic.startswith(b"BAAD"):
                return "MFT_RECORD_TABLE"
            if magic.startswith(b"SCCA"):
                return "PREFETCH_ARTIFACT"
            if magic.startswith(b"PK\x03\x04"):
                return "ZIP_EVIDENCE_CONTAINER"
    except Exception:
        pass

    return "GENERIC_FORENSIC_FILE"


def is_file_read_only(file_path: Path) -> bool:
    """Verifies that the evidence file is protected from in-place writes."""
    try:
        mode = os.stat(file_path).st_mode
        # If write bit is not set for user/group, or if on Windows read-only attribute is on
        is_ro = bool(mode & (stat.S_IREAD)) and not bool(mode & stat.S_IWRITE)
        return is_ro
    except Exception:
        return False


def build_evidence_manifest(
    evidence_path: str | Path,
    case_id: str = "CASE-AUTO-001",
    provenance_label: str = "HOST_FORENSIC_TRIAGE",
    output_dir: Optional[Path] = None,
) -> EvidenceManifest:
    """Scans evidence directory or single evidence file, hashes each item, and generates a manifest."""
    root = Path(evidence_path).resolve()
    items: List[EvidenceItem] = []
    total_bytes = 0

    candidates: List[Path] = []
    if root.is_file():
        candidates.append(root)
    elif root.is_dir():
        for dirpath, _, filenames in os.walk(root):
            for fname in filenames:
                # Skip temporary artifacts or state dirs
                if fname.startswith((".", "forensic_audit", "pipeline_summary")):
                    continue
                candidates.append(Path(dirpath) / fname)
    else:
        # If path does not exist, return synthetic empty manifest
        logger.warning("Evidence path does not exist: %s. Emitting empty manifest.", root)

    # Sort for deterministic evidence IDs
    candidates.sort(key=lambda p: str(p).lower())

    for idx, cand in enumerate(candidates, start=1):
        try:
            sz = cand.stat().st_size
            total_bytes += sz
            file_hash = compute_sha256(cand)
            art_type = detect_artifact_type(cand)
            mtime = datetime.fromtimestamp(cand.stat().st_mtime, tz=timezone.utc).isoformat()
            ro_status = is_file_read_only(cand)

            item = EvidenceItem(
                evidence_id=f"EV-{idx:03d}",
                original_filename=cand.name,
                source_path=str(cand),
                artifact_type=art_type,
                sha256_hash=file_hash,
                size_bytes=sz,
                acquisition_timestamp=mtime,
                is_read_only=ro_status,
                parsing_status="IDENTIFIED",
                provenance=provenance_label,
                metadata={
                    "extension": cand.suffix.lower(),
                    "absolute_path": str(cand.absolute()),
                },
            )
            items.append(item)
        except Exception as exc:
            logger.error("Failed to ingest evidence item %s: %s", cand, exc)

    now_iso = datetime.now(timezone.utc).isoformat()
    manifest_id = f"MAN-{hashlib.sha256(f'{case_id}-{now_iso}'.encode()).hexdigest()[:10].upper()}"

    manifest = EvidenceManifest(
        manifest_id=manifest_id,
        case_id=case_id,
        created_at=now_iso,
        evidence_root=str(root),
        item_count=len(items),
        total_bytes=total_bytes,
        items=items,
    )

    if output_dir:
        manifest.save_json(output_dir / "evidence_manifest.json")

    return manifest

