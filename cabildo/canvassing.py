"""Canvassing support — scripts, walk lists, tracking.

Generates door-knock scripts tailored to the candidate's platform
and the voter's profile. Tracks contacts and follow-ups.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .config import CampaignConfig
from .voter_data import Voter


def door_knock_script(config: CampaignConfig, voter: Optional[Voter] = None,
                      issue_focus: str = "") -> str:
    """Generate a canvassing script for a door knock."""
    name = config.candidate_name.split()[-1]
    greeting = f"Hi, I'm a volunteer with the {config.candidate_name} campaign."

    if voter and voter.first_name:
        greeting = (f"Hi {voter.first_name}, I'm a volunteer with the "
                    f"{config.candidate_name} campaign.")

    issue = issue_focus or config.platform_issues[0]

    script = f"""
{greeting}

Council Member {name} is running for re-election in District 3, and
we wanted to hear what's on your mind about our neighborhood.

[LISTEN FIRST — let them talk]

One thing {name} has been working on is {issue.lower()}.

[If they're interested]: Can we count on your support this November?

[If they have concerns]: I'll make sure {name} hears that directly.
What's the best way to follow up with you?

[Close]: Thanks for your time! Election Day is {config.election_date}.
Make sure you're registered at voterstatus.sos.ca.gov.

[Record: support level, issues raised, follow-up needed]
"""
    return script.strip()


def phone_bank_script(config: CampaignConfig,
                      voter: Optional[Voter] = None) -> str:
    """Generate a phone banking script."""
    name = config.candidate_name.split()[-1]

    script = f"""
Hi, is this {{voter_name}}? This is {{volunteer_name}}, calling on
behalf of Council Member {config.candidate_name} in District 3.

I'm calling to let you know about the upcoming election on
{config.election_date} and to ask if {name} can count on your
support.

[If YES]: Great! Can we count on you to vote? Do you know where
your polling place is?

[If UNDECIDED]: Is there a particular issue that's important to you?
[Address with platform positions]

[If NO]: We appreciate your time. Is there anything you'd like us
to pass along to Council Member {name}?

Thank you for your time!
"""
    return script.strip()


@dataclass
class ContactRecord:
    voter_id: str
    contact_type: str
    date: str
    support_level: str
    issues_raised: list[str]
    follow_up_needed: bool = False
    notes: str = ""
