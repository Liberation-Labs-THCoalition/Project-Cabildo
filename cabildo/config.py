"""Cabildo campaign configuration.

All campaign-specific settings in one place. Sensitive credentials
come from environment variables, never hardcoded.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass
class CampaignConfig:
    """Campaign-specific configuration."""

    candidate_name: str = "Mario Fernandez"
    office: str = "Eureka City Council, District 3"
    election_date: str = "2026-11-03"
    party: str = "Democratic"
    incumbent: bool = True

    district: str = "Eureka CA, District 3"
    estimated_voters: int = 5000

    opponent_name: str = ""
    opponent_party: str = ""

    platform_issues: list[str] = field(default_factory=lambda: [
        "Workers' rights and union protections",
        "Affordable housing",
        "Living wage",
        "Community safety through investment, not policing",
        "Environmental justice",
        "Government transparency and accountability",
    ])

    social_platforms: list[str] = field(default_factory=lambda: [
        "facebook",
    ])

    nationbuilder_slug: str = ""
    nationbuilder_api_token: str = ""
    pdi_export_path: str = ""

    fec_api_key: str = ""
    propublica_api_key: str = ""

    def __post_init__(self):
        self.nationbuilder_api_token = os.environ.get(
            "NATIONBUILDER_API_TOKEN", self.nationbuilder_api_token)
        self.nationbuilder_slug = os.environ.get(
            "NATIONBUILDER_SLUG", self.nationbuilder_slug)
        self.fec_api_key = os.environ.get(
            "FEC_API_KEY", self.fec_api_key)
        self.propublica_api_key = os.environ.get(
            "PROPUBLICA_API_KEY", self.propublica_api_key)

    @property
    def days_until_election(self) -> int:
        from datetime import date
        election = date.fromisoformat(self.election_date)
        return (election - date.today()).days
