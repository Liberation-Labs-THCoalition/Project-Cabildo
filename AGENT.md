# Cabildo Agent Setup Guide

**For the person setting up the AI agent (not the candidate).**

---

## Architecture

Cabildo runs as a Claude Code agent with OAuth authentication.
The agent uses the `.claude/CLAUDE.md` identity file for campaign-specific
instructions and ethics guardrails.

```
Cabildo Agent
├── Claude OAuth (model connection)
├── CLAUDE.md (campaign identity + ethics)
├── cabildo/ (Python modules)
│   ├── campaign.py      — BDI goals, milestones, daily briefing
│   ├── voter_data.py    — NationBuilder API + PDI import
│   ├── social.py        — Content drafting + approval queue
│   ├── oppo.py          — FEC/ProPublica opposition research
│   ├── canvassing.py    — Walk lists, scripts, contact tracking
│   ├── compliance.py    — Ethics + filing deadlines
│   ├── briefing.py      — Full morning briefing (all systems)
│   ├── opponent_watch.py — Rapid response to opponent activity
│   ├── voice_profile.py — Candidate voice training
│   ├── sentiment.py     — News/social monitoring
│   ├── donor_score.py   — Fundraising call prioritization
│   └── config.py        — Campaign configuration
├── MCP connections (optional)
│   ├── Buffer — social media scheduling
│   └── Custom tools as needed
└── State files (persistent between sessions)
    ├── campaign_state.json
    ├── content_queue/
    ├── oppo_data/
    ├── voice_profile/
    ├── opponent_watch/
    ├── sentiment_data/
    └── donor_data/
```

## Setup Steps

### 1. Environment Variables

Create a `.envrc` file (NOT committed to git):

```bash
# NationBuilder (from Dem sponsorship)
export NATIONBUILDER_SLUG=mario-fernandez    # Your NB site slug
export NATIONBUILDER_API_TOKEN=your-token    # Settings > Developer > API tokens

# FEC (free — register at api.data.gov)
export FEC_API_KEY=your-key

# ProPublica (free — email apihelp@propublica.org)
export PROPUBLICA_API_KEY=your-key

# Optional: Buffer for social media scheduling
# Set up via MCP connection in Claude Code settings
```

### 2. Campaign Configuration

Edit `cabildo/config.py` to match the campaign:

```python
candidate_name = "Mario Fernandez"
office = "Eureka City Council, District 3"
election_date = "2026-11-03"
incumbent = True
estimated_voters = 5000

opponent_name = ""           # Fill in when known
platform_issues = [          # Customize to candidate
    "Workers' rights and union protections",
    "Affordable housing",
    # ...
]
```

### 3. Voice Profile Setup

Collect the candidate's past writing and load it:

```python
from cabildo.voice_profile import VoiceProfile

voice = VoiceProfile("Mario Fernandez")
voice.add_samples_from_file("mario_facebook_posts.txt")
voice.add_samples_from_file("mario_council_statements.txt")
voice.save()
```

The more samples, the better. Aim for 20+ across different contexts
(social media, formal statements, casual community posts).

### 4. Voter Data Import

**NationBuilder** (preferred — live API):
```python
from cabildo.voter_data import NationBuilderClient

nb = NationBuilderClient(slug="mario-fernandez", token="your-token")
voters = nb.list_people(page=1, per_page=100)
```

**PDI** (CSV export):
```python
from cabildo.voter_data import load_pdi_export

voters = load_pdi_export("pdi_export_district3.csv")
```

### 5. Opponent Watch Setup

```python
from cabildo.opponent_watch import OpponentWatcher
from cabildo.config import CampaignConfig

config = CampaignConfig()
watcher = OpponentWatcher(
    opponent_name="Opponent Name",
    candidate_name=config.candidate_name,
    platform_issues=config.platform_issues,
)
```

To add opponent activity manually (until social API monitoring is set up):
```python
watcher.add_activity(
    source="Facebook",
    content="Opponent posted about public safety...",
    url="https://facebook.com/..."
)
```

### 6. Initialize Campaign State

```python
from cabildo.campaign import CampaignState, default_milestones
from cabildo.config import CampaignConfig

config = CampaignConfig()
state = CampaignState(config=config)
state.milestones = default_milestones(config)
state.save()
```

### 7. Daily Operations

**Morning briefing (run daily):**
```python
from cabildo.campaign import CampaignState
from cabildo.briefing import full_briefing
from cabildo.oppo import OppoResearch
from cabildo.social import ContentQueue
from cabildo.opponent_watch import OpponentWatcher
from cabildo.sentiment import SentimentMonitor
from cabildo.donor_score import DonorTracker
from cabildo.voice_profile import VoiceProfile

state = CampaignState.load()
print(full_briefing(
    state,
    oppo=OppoResearch(),
    content=ContentQueue(),
    opponent=OpponentWatcher("Opponent", state.config.candidate_name,
                              state.config.platform_issues),
    sentiment=SentimentMonitor(state.config.district, 
                                ["housing", "safety", "wages"]),
    donors=DonorTracker(),
    voice=VoiceProfile(state.config.candidate_name),
))
```

**News scan (run 2-3x daily):**
```python
from cabildo.sentiment import SentimentMonitor

monitor = SentimentMonitor("Eureka CA", ["housing", "safety", "wages"])
new_alerts = monitor.scan_topics()
if new_alerts:
    print(f"Found {len(new_alerts)} new articles")
    print(monitor.generate_digest_prompt())
```

## MCP Connections

### Buffer (Social Media)
If using Claude Code with Buffer MCP:
1. Connect Buffer in Claude Code settings
2. Use `list_channels` to find the Facebook page
3. Approved posts can be scheduled directly via `create_post`

### Custom MCP Tools
Any additional tools (calendar, email, SMS) can be added as MCP
connections without modifying Cabildo code.

## Cron Jobs (Optional)

For automated daily operations on a server:

```crontab
# Morning briefing at 7 AM
0 7 * * * cd /path/to/Cabildo && python -m cabildo.briefing

# News scan 3x daily
0 8,12,17 * * * cd /path/to/Cabildo && python -c "
from cabildo.sentiment import SentimentMonitor
m = SentimentMonitor('Eureka CA', ['housing', 'safety', 'wages'])
alerts = m.scan_topics()
if alerts: print(f'{len(alerts)} new articles found')
"
```

## Security Notes

- Never commit `.envrc` or any file containing API tokens
- NationBuilder tokens use Bearer auth header (not URL params)
- All voter data stays local — never uploaded to third-party services
- PDI exports may contain PII — handle with care, don't commit to git
- The AI disclosure in content is NOT optional — it's law in California

## Extending

Cabildo is designed to be extended. Each module follows the same pattern:
- Dataclass for records
- Manager class with save/load/briefing
- LLM prompt generators (return prompt strings, not LLM responses)

To add a new capability: write a module, add it to `briefing.py`, done.

---

*Built by CC (Coalition Code) — Liberation Labs / THCoalition*
*MIT License — fork it, help your neighbor run for office.*
