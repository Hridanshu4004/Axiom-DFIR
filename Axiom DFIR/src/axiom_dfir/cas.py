"""AXIOM DFIR - Content-Addressed Storage (CAS) Engine (Phase II).

Provides an immutable, SHA256-indexed storage subsystem for raw evidence,
tool outputs, and intermediate forensic artifacts.

Principles:
  - Identity is Content: Files and artifacts are addressed strictly by SHA256 digest.
  - Immutability: Once written, blobs cannot be modified or replaced.
  - Streaming Integrity: Multi-gigabyte disk and memory images are streamed in 64KB blocks.
  - Anti-Spoliation: Corruption or unauthorized alteration triggers an immediate halt.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import shutil
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterator, Optional

from axiom_dfir.integrity import EvidenceSpoliationError

logger = logging.getLogger("axiom_dfir.cas")

CHUNK_SIZE = 64 * 1024  # 64 KB streaming buffer


@dataclass
class BlobMetadata:
    digest: str
    size_bytes: int
    created_at: str
    original_filename: Optional[str] = None
    content_type: str = "application/octet-stream"
    custom_metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> BlobMetadata:
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


class ContentAddressedStorage:
    """Deterministic Content-Addressed Storage keyed by SHA-256."""

    def __init__(self, root_dir: Path | str) -> None:
        self.root_dir = Path(root_dir).resolve()
        self.blobs_dir = self.root_dir / "sha256"
        self.blobs_dir.mkdir(parents=True, exist_ok=True)

    def _blob_path(self, digest: str) -> Path:
        """Returns sharded path: root/sha256/ab/cd/<digest>.blob"""
        digest_clean = digest.lower().strip()
        shard1 = digest_clean[:2]
        shard2 = digest_clean[2:4]
        return self.blobs_dir / shard1 / shard2 / f"{digest_clean}.blob"

    def _meta_path(self, digest: str) -> Path:
        digest_clean = digest.lower().strip()
        shard1 = digest_clean[:2]
        shard2 = digest_clean[2:4]
        return self.blobs_dir / shard1 / shard2 / f"{digest_clean}.meta.json"

    @staticmethod
    def compute_sha256(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def compute_stream_sha256(file_path: Path | str) -> tuple[str, int]:
        h = hashlib.sha256()
        total_bytes = 0
        with open(file_path, "rb") as f:
            while chunk := f.read(CHUNK_SIZE):
                h.update(chunk)
                total_bytes += len(chunk)
        return h.hexdigest(), total_bytes

    def has_blob(self, digest: str) -> bool:
        return self._blob_path(digest).is_file()

    def store_bytes(
        self,
        data: bytes,
        original_filename: Optional[str] = None,
        content_type: str = "application/octet-stream",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Stores raw bytes into CAS and writes sidecar metadata."""
        digest = self.compute_sha256(data)
        bp = self._blob_path(digest)
        mp = self._meta_path(digest)

        if bp.is_file():
            logger.debug("Blob %s already present in CAS. Skipping write.", digest)
            return digest

        bp.parent.mkdir(parents=True, exist_ok=True)
        # Atomic write
        tmp_blob = bp.with_suffix(".tmp")
        with open(tmp_blob, "wb") as f:
            f.write(data)
        tmp_blob.replace(bp)

        meta = BlobMetadata(
            digest=digest,
            size_bytes=len(data),
            created_at=datetime.now(timezone.utc).isoformat(),
            original_filename=original_filename,
            content_type=content_type,
            custom_metadata=metadata or {},
        )
        tmp_meta = mp.with_suffix(".tmp")
        with open(tmp_meta, "w", encoding="utf-8") as f:
            json.dump(meta.to_dict(), f, indent=2)
        tmp_meta.replace(mp)

        logger.info("Stored blob %s (%d bytes) in CAS", digest, len(data))
        return digest

    def store_file(
        self,
        file_path: Path | str,
        content_type: str = "application/octet-stream",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Streams a local file into CAS without loading entire content into memory."""
        source = Path(file_path).resolve()
        if not source.is_file():
            raise FileNotFoundError(f"Source file not found: {source}")

        digest, total_bytes = self.compute_stream_sha256(source)
        bp = self._blob_path(digest)
        mp = self._meta_path(digest)

        if bp.is_file():
            logger.debug("File %s already present in CAS as %s", source.name, digest)
            return digest

        bp.parent.mkdir(parents=True, exist_ok=True)
        tmp_blob = bp.with_suffix(".tmp")
        with open(source, "rb") as src, open(tmp_blob, "wb") as dst:
            while chunk := src.read(CHUNK_SIZE):
                dst.write(chunk)
        tmp_blob.replace(bp)

        meta = BlobMetadata(
            digest=digest,
            size_bytes=total_bytes,
            created_at=datetime.now(timezone.utc).isoformat(),
            original_filename=source.name,
            content_type=content_type,
            custom_metadata=metadata or {},
        )
        tmp_meta = mp.with_suffix(".tmp")
        with open(tmp_meta, "w", encoding="utf-8") as f:
            json.dump(meta.to_dict(), f, indent=2)
        tmp_meta.replace(mp)

        logger.info("Stored file %s -> CAS blob %s (%d bytes)", source.name, digest, total_bytes)
        return digest

    def retrieve_bytes(self, digest: str) -> bytes:
        bp = self._blob_path(digest)
        if not bp.is_file():
            raise FileNotFoundError(f"Blob with digest {digest} not found in CAS")

        data = bp.read_bytes()
        # Verify on read
        actual_digest = self.compute_sha256(data)
        if actual_digest.lower() != digest.lower():
            raise EvidenceSpoliationError(
                f"CAS Integrity Violation! Blob {digest} corrupted on disk. Actual digest: {actual_digest}"
            )
        return data

    def get_metadata(self, digest: str) -> BlobMetadata:
        mp = self._meta_path(digest)
        if not mp.is_file():
            raise FileNotFoundError(f"Metadata for blob {digest} not found")
        with open(mp, "r", encoding="utf-8") as f:
            return BlobMetadata.from_dict(json.load(f))

    def verify_blob(self, digest: str) -> bool:
        """Verifies integrity of a blob without holding full content in memory."""
        bp = self._blob_path(digest)
        if not bp.is_file():
            return False
        calc_digest, _ = self.compute_stream_sha256(bp)
        return calc_digest.lower() == digest.lower()

    def verify_all(self, halt_on_error: bool = True) -> Dict[str, bool]:
        """Audits all blobs in the CAS repository."""
        results: Dict[str, bool] = {}
        for blob_file in self.blobs_dir.rglob("*.blob"):
            expected = blob_file.stem
            is_valid = self.verify_blob(expected)
            results[expected] = is_valid
            if not is_valid and halt_on_error:
                raise EvidenceSpoliationError(f"CAS Spoliation detected for blob {expected}!")
        return results

