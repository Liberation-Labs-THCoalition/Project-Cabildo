"""Donor scoring — prioritize fundraising calls by likelihood and capacity.

Uses FEC contribution history + basic heuristics to rank potential donors
and suggest ask amounts. No ML needed for a small district — rules and
public data go a long way.
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from .oppo import fec_contributions

logger = logging.getLogger(__name__)


@dataclass
class DonorProfile:
    name: str
    total_given: float = 0.0
    n_contributions: int = 0
    last_amount: float = 0.0
    last_date: str = ""
    employer: str = ""
    occupation: str = ""
    score: float = 0.0
    suggested_ask: float = 0.0


def score_donor(profile: DonorProfile) -> float:
    """Score a potential donor 0-1 based on giving history."""
    score = 0.0

    if profile.n_contributions > 0:
        score += 0.3
    if profile.n_contributions > 3:
        score += 0.2
    if profile.total_given > 500:
        score += 0.2
    if profile.total_given > 2000:
        score += 0.1
    if profile.last_date and profile.last_date >= "2025":
        score += 0.2

    return min(score, 1.0)


def suggest_ask(profile: DonorProfile) -> float:
    """Suggest an ask amount based on giving history."""
    if profile.last_amount > 0:
        return round(profile.last_amount * 1.25, -1)
    if profile.total_given > 0:
        avg = profile.total_given / max(profile.n_contributions, 1)
        return round(avg * 1.25, -1)
    return 25.0


def build_call_list_from_fec(committee_id: str,
                              api_key: str = "") -> list[DonorProfile]:
    """Build a ranked call list from FEC contribution data."""
    contributions = fec_contributions(committee_id, api_key, min_amount=25)

    donors: dict[str, DonorProfile] = {}
    for c in contributions:
        name = c.get("contributor_name", "Unknown")
        if name not in donors:
            donors[name] = DonorProfile(name=name)
        d = donors[name]
        amount = float(c.get("contribution_receipt_amount", 0))
        d.total_given += amount
        d.n_contributions += 1
        d.last_amount = amount
        d.last_date = c.get("contribution_receipt_date", "")
        d.employer = c.get("contributor_employer", d.employer)
        d.occupation = c.get("contributor_occupation", d.occupation)

    profiles = list(donors.values())
    for p in profiles:
        p.score = score_donor(p)
        p.suggested_ask = suggest_ask(p)

    profiles.sort(key=lambda p: p.score, reverse=True)
    return profiles


class DonorTracker:
    """Manages donor outreach and call list."""

    def __init__(self, state_dir: str | Path = "donor_data"):
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(exist_ok=True)
        self.profiles: list[DonorProfile] = []
        self.called: set[str] = set()
        self._load()

    def _load(self):
        path = self.state_dir / "donors.json"
        if path.exists():
            try:
                data = json.loads(path.read_text())
                self.profiles = [DonorProfile(**d) for d in data.get("profiles", [])]
                self.called = set(data.get("called", []))
            except (json.JSONDecodeError, ValueError):
                pass

    def save(self):
        path = self.state_dir / "donors.json"
        data = {
            "profiles": [
                {"name": p.name, "total_given": p.total_given,
                 "n_contributions": p.n_contributions,
                 "last_amount": p.last_amount, "last_date": p.last_date,
                 "employer": p.employer, "occupation": p.occupation,
                 "score": p.score, "suggested_ask": p.suggested_ask}
                for p in self.profiles
            ],
            "called": list(self.called),
        }
        path.write_text(json.dumps(data, indent=2))

    def mark_called(self, name: str):
        self.called.add(name)
        self.save()

    def uncalled(self, min_score: float = 0.3) -> list[DonorProfile]:
        return [p for p in self.profiles
                if p.name not in self.called and p.score >= min_score]

    def call_list_briefing(self, n: int = 10) -> str:
        uncalled = self.uncalled()[:n]
        if not uncalled:
            return "No pending donor calls."
        lines = ["FUNDRAISING CALL LIST", ""]
        for p in uncalled:
            lines.append(
                f"  {p.name} — score {p.score:.0%}, "
                f"suggest ${p.suggested_ask:.0f} "
                f"(gave ${p.total_given:.0f} over {p.n_contributions} contributions)"
            )
        return "\n".join(lines)
