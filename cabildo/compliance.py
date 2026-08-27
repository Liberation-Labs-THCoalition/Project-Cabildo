"""Campaign compliance — election law + ethical guardrails.

Based on Brennan Center principles + California campaign finance law.
BoundaryGuardian pattern from Kintsugi.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date, datetime

logger = logging.getLogger(__name__)


@dataclass
class ComplianceCheck:
    rule: str
    passed: bool
    detail: str = ""


ETHICS_RULES = [
    "AI disclosure: all AI-generated voter-facing content must include disclosure",
    "No impersonation: AI must not pretend to be the candidate",
    "No targeting: must not target voters by race, religion, or protected class",
    "No suppression: must not generate content designed to discourage voting",
    "Human approval: all persuasive messaging requires human sign-off before distribution",
    "Public records only: opposition research uses only publicly available data",
    "Audit trail: all AI-generated communications are logged",
]


def check_content(content: str, candidate_name: str = "") -> list[ComplianceCheck]:
    """Run compliance checks on draft content."""
    checks = []

    has_disclosure = any(phrase in content.lower() for phrase in [
        "ai assist", "ai-assist", "drafted with ai", "generated with ai",
        "ai tool", "ai-generated",
    ])
    checks.append(ComplianceCheck(
        "AI disclosure present",
        has_disclosure,
        "Content must include AI disclosure for voter-facing use",
    ))

    impersonation_phrases = [
        "i am " + candidate_name.lower() if candidate_name else "",
        "this is " + candidate_name.lower() if candidate_name else "",
        "speaking as your",
        "as your council member, i",
    ]
    has_impersonation = any(
        p and p in content.lower() for p in impersonation_phrases if p
    )
    checks.append(ComplianceCheck(
        "No candidate impersonation",
        not has_impersonation,
        "AI must not write in first person as the candidate without review",
    ))

    suppression_phrases = [
        "don't bother voting", "your vote doesn't matter",
        "stay home", "voting is pointless", "rigged",
    ]
    has_suppression = any(p in content.lower() for p in suppression_phrases)
    checks.append(ComplianceCheck(
        "No voter suppression language",
        not has_suppression,
        "Content must not discourage voting",
    ))

    return checks


def california_filing_deadlines(election_date: str) -> list[dict]:
    """Key California campaign finance filing deadlines."""
    edate = date.fromisoformat(election_date)
    return [
        {
            "name": "Semi-Annual Statement (Period 1)",
            "due": f"{edate.year}-07-31",
            "period": f"Jan 1 - Jun 30, {edate.year}",
        },
        {
            "name": "First Pre-Election Statement",
            "due": str(edate - __import__('datetime').timedelta(days=40)),
            "period": "Covers through 45 days before election",
        },
        {
            "name": "Second Pre-Election Statement",
            "due": str(edate - __import__('datetime').timedelta(days=12)),
            "period": "Covers through 17 days before election",
        },
        {
            "name": "24-Hour Contribution Reports",
            "period": "Last 16 days: report contributions $1,000+ within 24 hours",
            "due": f"Rolling, {edate - __import__('datetime').timedelta(days=16)} through {edate}",
        },
        {
            "name": "Semi-Annual Statement (Period 2)",
            "due": f"{edate.year + 1}-01-31",
            "period": f"Jul 1 - Dec 31, {edate.year}",
        },
    ]
