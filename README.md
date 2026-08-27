# Cabildo

**AI campaign scaffold for values-aligned municipal candidates.**

*Cabildo* — Spanish for "town council." The institution this tool serves.

## What It Does

Cabildo is a free, open-source AI campaign management tool built for small local campaigns that can't afford professional campaign tech. It handles:

- **Daily briefings** — what needs to happen today, who to call, where to knock
- **Voter data** — NationBuilder API + PDI export integration
- **Social media** — draft posts with mandatory AI disclosure, human approval required
- **Opposition research** — public records only (FEC, court records, news)
- **Canvassing** — walk lists, door-knock scripts, contact tracking
- **Compliance** — California campaign finance deadlines, ethical guardrails

## Ethics — Non-Negotiable

1. All AI-generated voter-facing content includes disclosure
2. No impersonation of the candidate
3. No targeting based on protected characteristics
4. No voter suppression content
5. Human-in-the-loop for all persuasive messaging
6. Public records only for opposition research
7. Full audit trail for all AI-generated communications

## Quick Start

```bash
# Set up credentials
export NATIONBUILDER_SLUG=your-campaign
export NATIONBUILDER_API_TOKEN=your-token
export FEC_API_KEY=your-key  # Free at api.data.gov

# Run a daily briefing
python -c "
from cabildo.campaign import CampaignState, default_milestones
from cabildo.briefing import full_briefing
state = CampaignState.load()
print(full_briefing(state))
"
```

## Architecture

Built on the [Kintsugi](https://github.com/Liberation-Labs-THCoalition/Project-Kintsugi) scaffold engine:
- **BDI goal tracking** for campaign milestones
- **BoundaryGuardian** pattern for ethics enforcement
- **SkillDomain** modules for each campaign function

Connects to:
- NationBuilder API v1 (voter data, events, donations)
- PDI exports (voter file, walk lists)
- OpenFEC API (opponent campaign finance)
- ProPublica Campaign Finance API
- Buffer (social media scheduling, via MCP)

## Built For

Originally built for a progressive city council incumbent in Eureka, CA. Designed to be reusable by any values-aligned local candidate.

## License

MIT — use it, fork it, help your neighbor run for office.

---

*Built by [CC (Coalition Code)](https://github.com/Liberation-Labs-THCoalition) — Liberation Labs / THCoalition*
