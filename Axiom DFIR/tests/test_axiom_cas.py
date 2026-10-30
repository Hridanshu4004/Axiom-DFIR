"""Tests for AXIOM DFIR Content-Addressed Storage (CAS) Engine (Phase II)."""

import hashlib
import tempfile
from pathlib import Path
import pytest

from axiom_dfir.cas import ContentAddressedStorage
from axiom_dfir.integrity import EvidenceSpoliationError


def test_cas_store_and_retrieve_bytes():
    with tempfile.TemporaryDirectory() as td:
        cas = ContentAddressedStorage(td)
        payload = b"FORENSIC EVIDENCE DUMP TEST BYTES 12345"
        expected_hash = hashlib.sha256(payload).hexdigest()

        digest = cas.store_bytes(payload, original_filename="test.raw")
        assert digest == expected_hash
        assert cas.has_blob(digest) is True

        retrieved = cas.retrieve_bytes(digest)
        assert retrieved == payload

        meta = cas.get_metadata(digest)
        assert meta.original_filename == "test.raw"
        assert meta.size_bytes == len(payload)


def test_cas_store_file_streaming():
    with tempfile.TemporaryDirectory() as td:
        cas = ContentAddressedStorage(td)
        sample_file = Path(td) / "sample_mem.raw"
        sample_data = b"STREAMING MEMORY ARTIFACT CHUNK" * 1000
        sample_file.write_bytes(sample_data)

        digest = cas.store_file(sample_file)
        assert cas.verify_blob(digest) is True

        # Test deduplication: storing again returns same digest without re-writing
        digest2 = cas.store_file(sample_file)
        assert digest2 == digest


def test_cas_tamper_detection_and_spoliation():
    with tempfile.TemporaryDirectory() as td:
        cas = ContentAddressedStorage(td)
        payload = b"CRITICAL FORENSIC RECORD DO NOT MODIFY"
        digest = cas.store_bytes(payload)

        # Directly tamper with the blob file on disk
        blob_path = cas._blob_path(digest)
        assert blob_path.is_file()
        blob_path.write_bytes(b"MALICIOUS ATTACKER OVERWRITE")

        # verify_blob should fail
        assert cas.verify_blob(digest) is False

        # retrieve_bytes should raise EvidenceSpoliationError
        with pytest.raises(EvidenceSpoliationError) as exc_info:
            cas.retrieve_bytes(digest)
        assert "CAS Integrity Violation" in str(exc_info.value)

