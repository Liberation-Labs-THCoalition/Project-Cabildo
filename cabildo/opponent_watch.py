"""Opponent watcher — monitor public statements, generate rapid response.

Watches opponent's public social media and news mentions. When activity
is detected, generates a draft response for the candidate's review.

All monitoring uses public data only. No hacking, no private accounts.
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class OpponentActivity:
    source: str
    content: str
    url: str = ""
    detected_at: str = field(default_factory=lambda: datetime.now().isoformat())
    response_draft: str = ""
    responded: bool = False


class OpponentWatcher:
    """Monitors opponent public activity and prepares rapid responses."""

    def __init__(self, opponent_name: str, candidate_name: str,
                 platform_issues: list[str],
                 state_dir: str | Path = "opponent_watch"):
        self.opponent_name = opponent_name
        self.candidate_name = candidate_name
        self.platform_issues = platform_issues
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(exist_ok=True)
        self.activities: list[OpponentActivity] = []
        self._load()

    def _load(self):
        path = self.state_dir / "activities.json"
        if path.exists():
            try:
                data = json.loads(path.read_text())
                self.activities = [OpponentActivity(**a) for a in data]
            except (json.JSONDecodeError, ValueError):
                logger.warning("Corrupted activities file — starting fresh")

    def save(self):
        path = self.state_dir / "activities.json"
        data = [
            {"source": a.source, "content": a.content, "url": a.url,
             "detected_at": a.detected_at, "response_draft": a.response_draft,
             "responded": a.responded}
            for a in self.activities
        ]
        path.write_text(json.dumps(data, indent=2))

    def add_activity(self, source: str, content: str, url: str = ""):
        activity = OpponentActivity(source=source, content=content, url=url)
        self.activities.append(activity)
        self.save()
        return activity

    def generate_response_prompt(self, activity: OpponentActivity) -> str:
        """Generate a prompt for an LLM to draft a rapid response."""
        return f"""You are drafting a rapid response for {self.candidate_name}'s campaign.

OPPONENT ACTIVITY:
Source: {activity.source}
Content: {activity.content}

CANDIDATE'S PLATFORM:
{chr(10).join(f'- {issue}' for issue in self.platform_issues)}

RULES:
- Respond to the substance, not the person
- Stay on the candidate's platform and values
- Be factual — cite specific actions or votes if relevant
- Keep it under 200 words for social media
- Do NOT attack personally — contrast on issues and record
- Include [AI-assisted draft — needs candidate review] at the end

Draft a response post:"""

    def pending_responses(self) -> list[tuple[int, OpponentActivity]]:
        return [(i, a) for i, a in enumerate(self.activities)
                if not a.responded and not a.response_draft]

    def unresponded(self) -> list[tuple[int, OpponentActivity]]:
        return [(i, a) for i, a in enumerate(self.activities)
                if not a.responded]

    def briefing(self) -> str:
        recent = self.activities[-10:]
        if not recent:
            return "No opponent activity detected."
        lines = [f"OPPONENT WATCH — {self.opponent_name}", ""]
        for a in recent:
            status = "responded" if a.responded else "NEEDS RESPONSE" if a.response_draft else "NEW"
            lines.append(f"  [{status}] {a.source} ({a.detected_at[:10]})")
            lines.append(f"    {a.content[:100]}")
        return "\n".join(lines)
