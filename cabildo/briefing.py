"""Daily campaign briefing — morning summary for the candidate.

Pulls together: calendar, metrics, oppo updates, content queue,
compliance deadlines, and today's priorities.
"""
from __future__ import annotations

from datetime import date

from .campaign import CampaignState, daily_briefing
from .compliance import california_filing_deadlines
from .oppo import OppoResearch
from .social import ContentQueue


def full_briefing(state: CampaignState,
                  oppo: OppoResearch | None = None,
                  content: ContentQueue | None = None) -> str:
    """Generate the complete morning briefing."""
    sections = [daily_briefing(state)]

    deadlines = california_filing_deadlines(state.config.election_date)
    upcoming_deadlines = [
        d for d in deadlines
        if isinstance(d.get("due"), str) and len(d["due"]) == 10
        and 0 <= (date.fromisoformat(d["due"]) - date.today()).days <= 30
    ]
    if upcoming_deadlines:
        sections.append("")
        sections.append("FILING DEADLINES (next 30 days):")
        for d in upcoming_deadlines:
            days = (date.fromisoformat(d["due"]) - date.today()).days
            sections.append(f"  - {d['name']}: {d['due']} ({days} days)")

    if oppo and oppo.findings:
        sections.append("")
        sections.append(oppo.briefing())

    if content:
        sections.append("")
        sections.append(content.weekly_summary())
        pending = content.pending()
        if pending:
            sections.append(f"  {len(pending)} posts awaiting your review")

    sections.append("")
    sections.append("---")
    sections.append("Remember: every AI-generated post needs your approval "
                    "before it goes out. Review the content queue when ready.")

    return "\n".join(sections)
