"""Sentiment monitoring — track local news and social media for issue shifts.

Lightweight version: Google News RSS + keyword matching + LLM summary.
No expensive APIs needed — designed for a $3K campaign budget.
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional
from urllib.request import urlopen, Request
from urllib.error import URLError
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)


@dataclass
class SentimentAlert:
    topic: str
    headline: str
    source: str
    url: str = ""
    detected_at: str = field(default_factory=lambda: datetime.now().isoformat())
    summary: str = ""
    response_drafted: bool = False


class SentimentMonitor:
    """Monitors local news and social media for issue-relevant activity."""

    def __init__(self, district: str, topics: list[str],
                 candidate_name: str = "", opponent_name: str = "",
                 state_dir: str | Path = "sentiment_data"):
        self.district = district
        self.topics = topics
        self.candidate_name = candidate_name
        self.opponent_name = opponent_name
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(exist_ok=True)
        self.alerts: list[SentimentAlert] = []
        self._load()

    def _load(self):
        path = self.state_dir / "alerts.json"
        if path.exists():
            try:
                data = json.loads(path.read_text())
                self.alerts = [SentimentAlert(**a) for a in data]
            except (json.JSONDecodeError, ValueError):
                pass

    def save(self):
        path = self.state_dir / "alerts.json"
        data = [
            {"topic": a.topic, "headline": a.headline,
             "source": a.source, "url": a.url,
             "detected_at": a.detected_at, "summary": a.summary,
             "response_drafted": a.response_drafted}
            for a in self.alerts
        ]
        path.write_text(json.dumps(data, indent=2))

    def google_news_search(self, query: str, n: int = 10) -> list[dict]:
        """Search Google News RSS for recent articles."""
        encoded = quote_plus(f"{query} {self.district}")
        url = f"https://news.google.com/rss/search?q={encoded}&hl=en-US&gl=US&ceid=US:en"
        try:
            req = Request(url, headers={"User-Agent": "Cabildo/0.1"})
            with urlopen(req, timeout=15) as resp:
                content = resp.read().decode()
            import xml.etree.ElementTree as ET
            root = ET.fromstring(content)
            items = []
            for item in root.findall(".//item")[:n]:
                title = item.findtext("title", "")
                link = item.findtext("link", "")
                source = item.findtext("source", "")
                items.append({"title": title, "link": link, "source": source})
            return items
        except Exception as e:
            logger.debug("Google News search failed: %s", e)
            return []

    def scan_topics(self) -> list[SentimentAlert]:
        """Scan all tracked topics for new activity."""
        new_alerts = []
        search_terms = self.topics[:]
        if self.opponent_name:
            search_terms.append(self.opponent_name)
        if self.candidate_name:
            search_terms.append(self.candidate_name)

        seen_urls = {a.url for a in self.alerts}

        for topic in search_terms:
            articles = self.google_news_search(topic)
            for article in articles:
                if article["link"] not in seen_urls:
                    alert = SentimentAlert(
                        topic=topic,
                        headline=article["title"],
                        source=article["source"],
                        url=article["link"],
                    )
                    new_alerts.append(alert)
                    self.alerts.append(alert)
                    seen_urls.add(article["link"])

        if new_alerts:
            self.save()
            logger.info("Found %d new articles across %d topics",
                        len(new_alerts), len(search_terms))
        return new_alerts

    def generate_digest_prompt(self, alerts: list[SentimentAlert] | None = None) -> str:
        """Generate a prompt for LLM to summarize recent sentiment."""
        items = alerts or self.alerts[-20:]
        if not items:
            return ""

        headlines = "\n".join(
            f"- [{a.topic}] {a.headline} ({a.source})" for a in items
        )

        return f"""Summarize the following recent news relevant to a city council
campaign in {self.district}. Identify:
1. Issues gaining attention
2. Any mentions of the candidates
3. Opportunities for the campaign to respond or engage

Headlines:
{headlines}

Provide a brief (under 200 words) campaign-relevant summary."""

    def briefing(self) -> str:
        recent = [a for a in self.alerts[-10:]]
        if not recent:
            return "No recent sentiment alerts."
        lines = ["SENTIMENT MONITOR", ""]
        topics_seen = {}
        for a in recent:
            topics_seen.setdefault(a.topic, []).append(a)
        for topic, alerts in topics_seen.items():
            lines.append(f"  {topic}: {len(alerts)} articles")
            for a in alerts[:3]:
                lines.append(f"    - {a.headline[:80]}")
        return "\n".join(lines)
