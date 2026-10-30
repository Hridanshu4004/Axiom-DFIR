"""Tests for AXIOM DFIR Threat Intelligence Layer (Phase II)."""

from axiom_dfir.threat_intel import ThreatIntelligenceEngine, ThreatIntelReport


def test_private_ip_bypass():
    engine = ThreatIntelligenceEngine(api_key="mock_key")
    report = engine.enrich_ioc("192.168.1.50", "IP_ADDRESS")
    assert report is not None
    assert report.reputation == "BENIGN"
    assert "Private or Loopback" in report.summary
    assert report.source_type == "EXTERNAL_THREAT_INTEL"


def test_unconfigured_skips_gracefully():
    engine = ThreatIntelligenceEngine(api_key="")
    assert engine.is_configured() is False
    report = engine.enrich_ioc("8.8.8.8", "IP_ADDRESS")
    assert report is None


def test_cache_deduplication():
    engine = ThreatIntelligenceEngine(api_key="mock_key")
    # Enrich 10.0.0.1
    r1 = engine.enrich_ioc("10.0.0.1", "IP_ADDRESS")
    r2 = engine.enrich_ioc("10.0.0.1", "IP_ADDRESS")
    assert r1 is r2  # Same cached instance

