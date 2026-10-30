"""Tests for AXIOM DFIR OCSF Normalization Layer (Phase II)."""

from axiom_dfir.ocsf import OCSFNormalizer, OCSFClassUID, OCSFCategoryUID


def test_normalize_process_activity():
    raw_proc = {
        "pid": 4120,
        "name": "powershell.exe",
        "ppid": 1024,
        "parent_name": "explorer.exe",
        "command_line": "powershell.exe -enc SQBFAFgA...",
        "user": "DOMAIN\\Administrator",
        "sha256": "deadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef",
        "timestamp": "2026-10-30T04:15:10Z",
    }
    ocsf = OCSFNormalizer.normalize_process(raw_proc, evidence_ref="EV-001")
    d = ocsf.to_dict()

    assert d["class_uid"] == OCSFClassUID.PROCESS_ACTIVITY.value
    assert d["category_uid"] == OCSFCategoryUID.SYSTEM_ACTIVITY.value
    assert d["process"]["name"] == "powershell.exe"
    assert d["process"]["pid"] == 4120
    assert d["parent_process"]["pid"] == 1024
    assert d["evidence_ref"] == "EV-001"
    assert d["metadata"]["product"]["name"] == "AXIOM DFIR"


def test_normalize_network_activity():
    raw_net = {
        "src_ip": "10.0.0.15",
        "src_port": 49210,
        "remote_ip": "192.168.1.50",
        "remote_port": 4444,
        "protocol": "TCP",
    }
    ocsf = OCSFNormalizer.normalize_network(raw_net, evidence_ref="EV-002")
    d = ocsf.to_dict()

    assert d["class_uid"] == OCSFClassUID.NETWORK_ACTIVITY.value
    assert d["src_endpoint"]["ip"] == "10.0.0.15"
    assert d["dst_endpoint"]["ip"] == "192.168.1.50"
    assert d["dst_endpoint"]["port"] == 4444
    assert d["connection_info"]["protocol_name"] == "TCP"


def test_normalize_authentication():
    raw_auth = {
        "target_username": "Administrator",
        "target_domain": "CORP",
        "logon_type": "Network",
        "status": "SUCCESS",
    }
    ocsf = OCSFNormalizer.normalize_authentication(raw_auth, evidence_ref="EV-003")
    d = ocsf.to_dict()

    assert d["class_uid"] == OCSFClassUID.AUTHENTICATION.value
    assert d["status_id"] == 1
    assert d["user"]["name"] == "Administrator"
    assert d["logon_type"] == "Network"


def test_normalize_batch():
    records = [
        {"pid": 100, "name": "cmd.exe"},
        {"pid": 200, "name": "calc.exe"},
    ]
    batch = OCSFNormalizer.normalize_batch(records, "PROCESS", "vol_pstree")
    assert len(batch) == 2
    assert batch[0]["process"]["name"] == "cmd.exe"
    assert batch[1]["process"]["name"] == "calc.exe"

