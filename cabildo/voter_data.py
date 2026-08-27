"""Voter data integration — NationBuilder API + PDI exports.

NationBuilder: REST API v1, documented at nationbuilder.com/api_documentation_v1
PDI: contract-based, no public API — we ingest CSV/Excel exports.
"""
from __future__ import annotations

import csv
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
from urllib.request import urlopen, Request
from urllib.error import URLError

logger = logging.getLogger(__name__)


@dataclass
class Voter:
    voter_id: str = ""
    first_name: str = ""
    last_name: str = ""
    address: str = ""
    precinct: str = ""
    party: str = ""
    vote_history: list[str] = field(default_factory=list)
    contacted: bool = False
    support_level: str = ""
    notes: str = ""
    phone: str = ""
    email: str = ""


class NationBuilderClient:
    """NationBuilder API v1 client for voter data."""

    def __init__(self, slug: str, token: str):
        self.base_url = f"https://{slug}.nationbuilder.com/api/v1"
        self.token = token

    def _get(self, endpoint: str, params: dict | None = None) -> dict:
        from urllib.parse import urlencode
        query = params or {}
        query["access_token"] = self.token
        sep = "&" if "?" in endpoint else "?"
        url = f"{self.base_url}{endpoint}{sep}{urlencode(query)}"
        try:
            req = Request(url, headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {self.token}",
            })
            with urlopen(req, timeout=15) as resp:
                return json.loads(resp.read())
        except (URLError, json.JSONDecodeError) as e:
            logger.error("NationBuilder API failed: %s", e)
            return {}

    def list_people(self, page: int = 1, per_page: int = 100) -> list[dict]:
        data = self._get(f"/people?page={page}&per_page={per_page}")
        return data.get("results", [])

    def search_people(self, query: str) -> list[dict]:
        data = self._get("/people/search", {"name": query})
        return data.get("results", [])

    def get_person(self, person_id: int) -> dict:
        data = self._get(f"/people/{person_id}")
        return data.get("person", {})

    def list_tags(self) -> list[dict]:
        data = self._get("/tags")
        return data.get("results", [])

    def people_by_tag(self, tag: str) -> list[dict]:
        data = self._get(f"/tags/{tag}/people")
        return data.get("results", [])

    def list_events(self) -> list[dict]:
        data = self._get("/sites/1/pages/events")
        return data.get("results", [])

    def list_donations(self, page: int = 1) -> list[dict]:
        data = self._get(f"/donations?page={page}")
        return data.get("results", [])


def load_pdi_export(path: str | Path) -> list[Voter]:
    """Load voter records from a PDI CSV export."""
    p = Path(path)
    if not p.exists():
        logger.warning("PDI export not found: %s", path)
        return []

    voters = []
    with open(p, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            voter = Voter(
                voter_id=row.get("VoterID", row.get("voter_id", "")),
                first_name=row.get("FirstName", row.get("first_name", "")),
                last_name=row.get("LastName", row.get("last_name", "")),
                address=row.get("Address", row.get("address", "")),
                precinct=row.get("Precinct", row.get("precinct", "")),
                party=row.get("Party", row.get("party", "")),
                phone=row.get("Phone", row.get("phone", "")),
                email=row.get("Email", row.get("email", "")),
            )
            hist = row.get("VoteHistory", row.get("vote_history", ""))
            if hist:
                voter.vote_history = [h.strip() for h in hist.split(",")]
            voters.append(voter)

    logger.info("Loaded %d voters from PDI export %s", len(voters), path)
    return voters


def generate_walk_list(voters: list[Voter], precinct: str = "",
                       party_filter: str = "",
                       exclude_contacted: bool = True) -> list[Voter]:
    """Generate a canvassing walk list from voter data."""
    filtered = voters
    if precinct:
        filtered = [v for v in filtered if v.precinct == precinct]
    if party_filter:
        filtered = [v for v in filtered if v.party == party_filter]
    if exclude_contacted:
        filtered = [v for v in filtered if not v.contacted]
    return sorted(filtered, key=lambda v: v.address)
