"""Opposition research — public records only.

Sources:
  - OpenFEC API: campaign finance filings
  - ProPublica Campaign Finance API: near real-time FEC data
  - Public court records (manual / county-specific)
  - Public social media statements
  - Voting records (via NationBuilder/PDI)
  - News articles (web search)

Ethics: everything here is public record. No hacking, no private data,
no manufactured context. Present facts, let the candidate decide messaging.
"""
from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional
from urllib.request import urlopen, Request
from urllib.error import URLError

logger = logging.getLogger(__name__)

FEC_BASE = "https://api.open.fec.gov/v1"
PROPUBLICA_BASE = "https://api.propublica.org/campaign-finance/v1"


@dataclass
class OppoFinding:
    source: str
    category: str
    summary: str
    detail: str = ""
    url: str = ""
    date_found: str = field(default_factory=lambda: datetime.now().isoformat())
    verified: bool = False


def fec_candidate_search(name: str, api_key: str = "",
                         state: str = "", office: str = "") -> list[dict]:
    """Search FEC for a candidate by name."""
    key = api_key or os.environ.get("FEC_API_KEY", "")
    if not key:
        logger.warning("No FEC API key — set FEC_API_KEY env var (free at api.data.gov)")
        return []

    params = f"q={name}&api_key={key}"
    if state:
        params += f"&state={state}"
    url = f"{FEC_BASE}/candidates/search/?{params}"

    try:
        req = Request(url, headers={"Accept": "application/json"})
        with urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
            return data.get("results", [])
    except (URLError, json.JSONDecodeError) as e:
        logger.error("FEC search failed: %s", e)
        return []


def fec_committee_finances(committee_id: str,
                           api_key: str = "") -> dict:
    """Get financial summary for a committee."""
    key = api_key or os.environ.get("FEC_API_KEY", "")
    if not key:
        return {}

    url = f"{FEC_BASE}/committee/{committee_id}/totals/?api_key={key}"
    try:
        req = Request(url, headers={"Accept": "application/json"})
        with urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
            results = data.get("results", [])
            return results[0] if results else {}
    except (URLError, json.JSONDecodeError) as e:
        logger.error("FEC committee lookup failed: %s", e)
        return {}


def fec_contributions(committee_id: str, api_key: str = "",
                      min_amount: float = 200) -> list[dict]:
    """Get individual contributions above threshold."""
    key = api_key or os.environ.get("FEC_API_KEY", "")
    if not key:
        return []

    url = (f"{FEC_BASE}/schedules/schedule_a/"
           f"?committee_id={committee_id}&min_amount={min_amount}"
           f"&sort=-contribution_receipt_amount&per_page=50&api_key={key}")
    try:
        req = Request(url, headers={"Accept": "application/json"})
        with urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
            return data.get("results", [])
    except (URLError, json.JSONDecodeError) as e:
        logger.error("FEC contributions lookup failed: %s", e)
        return []


class OppoResearch:
    """Manages opposition research findings from public sources."""

    def __init__(self, state_dir: str | Path = "oppo_data"):
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(exist_ok=True)
        self.findings: list[OppoFinding] = []
        self._load()

    def _load(self):
        path = self.state_dir / "findings.json"
        if path.exists():
            data = json.loads(path.read_text())
            self.findings = [OppoFinding(**f) for f in data]

    def save(self):
        path = self.state_dir / "findings.json"
        data = [
            {"source": f.source, "category": f.category,
             "summary": f.summary, "detail": f.detail,
             "url": f.url, "date_found": f.date_found,
             "verified": f.verified}
            for f in self.findings
        ]
        path.write_text(json.dumps(data, indent=2))

    def add(self, finding: OppoFinding):
        self.findings.append(finding)
        self.save()

    def by_category(self) -> dict[str, list[OppoFinding]]:
        cats: dict[str, list[OppoFinding]] = {}
        for f in self.findings:
            cats.setdefault(f.category, []).append(f)
        return cats

    def briefing(self) -> str:
        if not self.findings:
            return "No opposition research findings on file."
        cats = self.by_category()
        lines = ["OPPOSITION RESEARCH SUMMARY", ""]
        for cat, findings in sorted(cats.items()):
            lines.append(f"  {cat.upper()} ({len(findings)} items):")
            for f in findings[:5]:
                verified = "✓" if f.verified else "?"
                lines.append(f"    [{verified}] {f.summary}")
        return "\n".join(lines)
