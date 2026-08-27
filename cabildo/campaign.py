"""Campaign BDI — goal tracking, milestones, daily priorities.

Beliefs: voter data, district issues, opponent intel, calendar
Desires: win election, advance platform, build community support
Intentions: today's canvass route, this week's posts, filing deadlines
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Optional

from .config import CampaignConfig


@dataclass
class Milestone:
    name: str
    due: str
    status: str = "pending"
    notes: str = ""

    @property
    def days_remaining(self) -> int:
        return (date.fromisoformat(self.due) - date.today()).days

    @property
    def overdue(self) -> bool:
        return self.days_remaining < 0 and self.status != "done"


@dataclass
class CampaignState:
    """Persistent campaign state — serialized to JSON between sessions."""

    config: CampaignConfig = field(default_factory=CampaignConfig)
    milestones: list[Milestone] = field(default_factory=list)
    doors_knocked: int = 0
    doors_target: int = 2000
    volunteers: list[str] = field(default_factory=list)
    donations_total: float = 0.0
    posts_this_week: int = 0
    oppo_findings: list[dict] = field(default_factory=list)
    daily_log: list[dict] = field(default_factory=list)

    def save(self, path: str | Path = "campaign_state.json"):
        data = {
            "candidate": self.config.candidate_name,
            "office": self.config.office,
            "election_date": self.config.election_date,
            "days_remaining": self.config.days_until_election,
            "doors_knocked": self.doors_knocked,
            "doors_target": self.doors_target,
            "donations_total": self.donations_total,
            "volunteers": self.volunteers,
            "posts_this_week": self.posts_this_week,
            "milestones": [
                {"name": m.name, "due": m.due, "status": m.status, "notes": m.notes}
                for m in self.milestones
            ],
            "oppo_findings": self.oppo_findings,
            "daily_log": self.daily_log[-30:],
            "saved_at": datetime.now().isoformat(),
        }
        Path(path).write_text(json.dumps(data, indent=2))

    @classmethod
    def load(cls, path: str | Path = "campaign_state.json") -> "CampaignState":
        p = Path(path)
        if not p.exists():
            return cls()
        data = json.loads(p.read_text())
        state = cls()
        state.doors_knocked = data.get("doors_knocked", 0)
        state.doors_target = data.get("doors_target", 2000)
        state.donations_total = data.get("donations_total", 0.0)
        state.volunteers = data.get("volunteers", [])
        state.posts_this_week = data.get("posts_this_week", 0)
        state.oppo_findings = data.get("oppo_findings", [])
        state.daily_log = data.get("daily_log", [])
        state.milestones = [
            Milestone(**m) for m in data.get("milestones", [])
        ]
        return state

    def add_milestone(self, name: str, due: str, notes: str = ""):
        self.milestones.append(Milestone(name=name, due=due, notes=notes))

    def log_day(self, doors: int = 0, calls: int = 0, events: int = 0,
                notes: str = ""):
        entry = {
            "date": date.today().isoformat(),
            "doors": doors,
            "calls": calls,
            "events": events,
            "notes": notes,
        }
        self.daily_log.append(entry)
        self.doors_knocked += doors


def default_milestones(config: CampaignConfig) -> list[Milestone]:
    """Standard municipal campaign milestones."""
    year = config.election_date[:4]
    return [
        Milestone("Candidate filing deadline", f"{year}-08-15",
                  notes="Check county clerk for exact date"),
        Milestone("First campaign finance report", f"{year}-09-30"),
        Milestone("Voter registration deadline", f"{year}-10-19"),
        Milestone("GOTV plan finalized", f"{year}-10-20"),
        Milestone("Mail ballot requests begin", f"{year}-10-07"),
        Milestone("Final pre-election finance report", f"{year}-10-24"),
        Milestone("Early voting begins", f"{year}-10-24"),
        Milestone("Election Day", config.election_date),
    ]


def daily_briefing(state: CampaignState) -> str:
    """Generate a morning campaign briefing."""
    config = state.config
    days = config.days_until_election
    door_pct = (state.doors_knocked / max(state.doors_target, 1)) * 100

    lines = [
        f"DAILY BRIEFING — {date.today().strftime('%A, %B %d')}",
        f"{config.candidate_name} for {config.office}",
        f"{days} days until Election Day",
        "",
        f"DOORS: {state.doors_knocked}/{state.doors_target} ({door_pct:.0f}%)",
        f"DONATIONS: ${state.donations_total:,.2f}",
        f"VOLUNTEERS: {len(state.volunteers)}",
        f"POSTS THIS WEEK: {state.posts_this_week}",
    ]

    overdue = [m for m in state.milestones if m.overdue]
    upcoming = [m for m in state.milestones
                if 0 <= m.days_remaining <= 14 and m.status != "done"]

    if overdue:
        lines.append("")
        lines.append("⚠ OVERDUE:")
        for m in overdue:
            lines.append(f"  - {m.name} (was due {m.due})")

    if upcoming:
        lines.append("")
        lines.append("UPCOMING:")
        for m in upcoming:
            lines.append(f"  - {m.name} — {m.days_remaining} days ({m.due})")

    if days <= 14:
        lines.append("")
        lines.append("FINAL STRETCH — GOTV MODE")
        lines.append(f"  Target: {state.doors_target - state.doors_knocked} doors remaining")
        daily_target = max(1, (state.doors_target - state.doors_knocked) // max(days, 1))
        lines.append(f"  Daily target: {daily_target} doors/day to hit goal")

    return "\n".join(lines)
