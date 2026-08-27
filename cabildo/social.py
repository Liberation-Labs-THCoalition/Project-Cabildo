"""Social media content generation and scheduling.

Generates draft posts for human review. NEVER posts without approval.
All AI-generated content is marked with a disclosure footer.

Connects to Buffer MCP for scheduling when available.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional


AI_DISCLOSURE = "\n\n[This post was drafted with AI assistance]"


@dataclass
class PostDraft:
    platform: str
    content: str
    category: str
    created: str = field(default_factory=lambda: datetime.now().isoformat())
    approved: bool = False
    posted: bool = False
    approved_by: str = ""
    posted_at: str = ""

    @property
    def content_with_disclosure(self) -> str:
        if AI_DISCLOSURE.strip() not in self.content:
            return self.content + AI_DISCLOSURE
        return self.content


POST_TEMPLATES = {
    "door_knock_update": (
        "Great conversations today in District 3! Knocked {doors} doors "
        "and heard from neighbors about {issue}. Your voice matters — "
        "and I'm listening. {hashtag}"
    ),
    "issue_position": (
        "{issue_intro}\n\n{position}\n\n"
        "As your City Council member, I'll keep fighting for {value}. "
        "{call_to_action}"
    ),
    "event_promo": (
        "Join me {when} at {where}!\n\n{description}\n\n"
        "Everyone welcome. Let's talk about what matters to District 3."
    ),
    "endorsement": (
        "Honored to have the support of {endorser}. {quote}\n\n"
        "Together, we're building a District 3 that works for everyone."
    ),
    "gotv": (
        "Election Day is {days} days away! Make sure you're registered "
        "and have a plan to vote.\n\nCheck your registration: "
        "voterstatus.sos.ca.gov\n\n"
        "District 3 needs YOUR voice. {personal_note}"
    ),
}


class ContentQueue:
    """Manages draft posts awaiting approval."""

    def __init__(self, state_dir: str | Path = "content_queue"):
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(exist_ok=True)
        self.drafts: list[PostDraft] = []
        self._load()

    def _load(self):
        path = self.state_dir / "drafts.json"
        if path.exists():
            data = json.loads(path.read_text())
            self.drafts = [PostDraft(**d) for d in data]

    def save(self):
        path = self.state_dir / "drafts.json"
        data = [
            {"platform": d.platform, "content": d.content,
             "category": d.category, "created": d.created,
             "approved": d.approved, "posted": d.posted,
             "approved_by": d.approved_by, "posted_at": d.posted_at}
            for d in self.drafts
        ]
        path.write_text(json.dumps(data, indent=2))

    def add_draft(self, platform: str, content: str, category: str) -> PostDraft:
        draft = PostDraft(platform=platform, content=content, category=category)
        self.drafts.append(draft)
        self.save()
        return draft

    def approve(self, index: int, approved_by: str = "candidate"):
        if 0 <= index < len(self.drafts):
            self.drafts[index].approved = True
            self.drafts[index].approved_by = approved_by
            self.save()

    def pending(self) -> list[tuple[int, PostDraft]]:
        return [(i, d) for i, d in enumerate(self.drafts)
                if not d.approved and not d.posted]

    def approved_unposted(self) -> list[tuple[int, PostDraft]]:
        return [(i, d) for i, d in enumerate(self.drafts)
                if d.approved and not d.posted]

    def weekly_summary(self) -> str:
        total = len(self.drafts)
        approved = sum(1 for d in self.drafts if d.approved)
        posted = sum(1 for d in self.drafts if d.posted)
        pending = sum(1 for d in self.drafts if not d.approved and not d.posted)
        return (f"Content queue: {total} total, {posted} posted, "
                f"{approved - posted} approved/unposted, {pending} pending review")
