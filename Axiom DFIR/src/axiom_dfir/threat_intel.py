"""AXIOM DFIR - Optional Tavily Threat Intelligence Enrichment (Phase II).

Queries external threat intelligence sources via Tavily API for public IOCs
(external IPs, suspicious domains, file hashes).

Forensic Integrity Invariant:
  EXTERNAL THREAT INTEL IS STRICTLY ISOLATED FROM LOCAL FORENSIC EVIDENCE.
  External reputation never auto-verifies an internal factual claim.
  All enriched indicators are tagged with source_type="EXTERNAL_THREAT_INTEL".
"""

from __future__ import annotations

import json
import logging
import os
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger("axiom_dfir.threat_intel")

TAVILY_SEARCH_ENDPOINT = "https://api.tavily.com/search"


@dataclass
class ThreatIntelReport:
    ioc_value: str
    ioc_type: str  # IP_ADDRESS, DOMAIN, FILE_HASH
    reputation: str  # SUSPICIOUS, BENIGN, UNKNOWN
    summary: str
    source_type: str = "EXTERNAL_THREAT_INTEL"
    external_sources: List[str] = field(default_factory=list)
    queried_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ThreatIntelligenceEngine:
    """Enriches forensic IOCs with external OSINT intelligence."""

    def __init__(self, api_key: Optional[str] = None, timeout: float = 8.0) -> None:
        self.api_key = api_key or os.environ.get("TAVILY_API_KEY") or os.environ.get("AXIOM_TAVILY_KEY") or ""
        self.timeout = timeout
        self._cache: Dict[str, ThreatIntelReport] = {}

    def is_configured(self) -> bool:
        return bool(self.api_key.strip())

    def enrich_ioc(self, ioc_value: str, ioc_type: str = "IP_ADDRESS") -> Optional[ThreatIntelReport]:
        """Queries Tavily API for a specific IOC if configured."""
        val = ioc_value.strip()
        if not val:
            return None

        # Check local cache
        if val in self._cache:
            return self._cache[val]

        # Skip private/loopback IP addresses
        if ioc_type == "IP_ADDRESS":
            if val.startswith(("127.", "10.", "192.168.", "172.16.", "172.17.", "172.18.", "172.19.", "172.2", "172.3", "0.0.0.0")):
                report = ThreatIntelReport(
                    ioc_value=val,
                    ioc_type=ioc_type,
                    reputation="BENIGN",
                    summary="RFC1918 Private or Loopback IP Address. Not routable on public internet.",
                )
                self._cache[val] = report
                return report

        if not self.is_configured():
            logger.debug("Tavily API key not configured; skipping external enrichment for %s", val)
            return None

        query = f"threat intelligence reputation analysis {val}"
        payload = {
            "api_key": self.api_key,
            "query": query,
            "search_depth": "basic",
            "include_answer": True,
            "max_results": 3,
        }

        try:
            req = urllib.request.Request(
                TAVILY_SEARCH_ENDPOINT,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json", "User-Agent": "AXIOM-DFIR-ThreatIntel/1.0"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            answer = data.get("answer") or ""
            results = data.get("results") or []
            sources = [r.get("url") for r in results if isinstance(r, dict) and r.get("url")]

            # Classify reputation based on OSINT text
            text_lower = (answer + " " + " ".join(r.get("content", "") for r in results)).lower()
            if any(term in text_lower for term in ["c2", "malware", "botnet", "ransomware", "trojan", "cobalt strike", "phishing"]):
                reputation = "SUSPICIOUS"
            elif any(term in text_lower for term in ["clean", "safe", "legitimate", "microsoft", "google", "cloudflare"]):
                reputation = "BENIGN"
            else:
                reputation = "UNKNOWN"

            summary = answer if answer else (results[0].get("content")[:300] if results else "No specific threat intelligence found.")

            report = ThreatIntelReport(
                ioc_value=val,
                ioc_type=ioc_type,
                reputation=reputation,
                summary=summary,
                external_sources=sources,
            )
            self._cache[val] = report
            logger.info("Tavily threat intel retrieved for %s: %s", val, reputation)
            return report

        except Exception as exc:
            logger.warning("Failed to enrich IOC %s via Tavily: %s", val, exc)
            return None

    def enrich_batch(self, iocs: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Enriches a batch of IOCs [{'value': ..., 'type': ...}]."""
        results = []
        for item in iocs:
            val = item.get("value", "")
            itype = item.get("type", "IP_ADDRESS")
            rep = self.enrich_ioc(val, itype)
            if rep:
                results.append(rep.to_dict())
        return results

