"""Voice profile — train on candidate's writing to generate on-voice content.

Stores sample writings (past Facebook posts, council statements, speeches)
and uses them as few-shot context so generated content sounds like the
candidate, not like generic AI.

No ML training needed — this is retrieval-augmented generation with the
candidate's own words as the retrieval corpus.
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class WritingSample:
    text: str
    source: str
    date: str = ""
    category: str = ""


class VoiceProfile:
    """Candidate's voice profile built from their own writing."""

    def __init__(self, candidate_name: str,
                 state_dir: str | Path = "voice_profile"):
        self.candidate_name = candidate_name
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(exist_ok=True)
        self.samples: list[WritingSample] = []
        self._load()

    def _load(self):
        path = self.state_dir / "samples.json"
        if path.exists():
            try:
                data = json.loads(path.read_text())
                self.samples = [WritingSample(**s) for s in data]
            except (json.JSONDecodeError, ValueError):
                logger.warning("Corrupted voice profile — starting fresh")

    def save(self):
        path = self.state_dir / "samples.json"
        data = [
            {"text": s.text, "source": s.source,
             "date": s.date, "category": s.category}
            for s in self.samples
        ]
        path.write_text(json.dumps(data, indent=2))

    def add_sample(self, text: str, source: str, date: str = "",
                   category: str = ""):
        self.samples.append(WritingSample(
            text=text, source=source, date=date, category=category))
        self.save()

    def add_samples_from_file(self, path: str | Path):
        """Load writing samples from a text file (one per paragraph)."""
        p = Path(path)
        if not p.exists():
            logger.warning("Sample file not found: %s", path)
            return
        text = p.read_text()
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        for para in paragraphs:
            if len(para) > 50:
                self.add_sample(para, source=str(path))
        logger.info("Added %d samples from %s", len(paragraphs), path)

    def best_samples(self, category: str = "", n: int = 5) -> list[WritingSample]:
        """Get the most relevant samples for context."""
        if category:
            matching = [s for s in self.samples if s.category == category]
            if matching:
                return matching[-n:]
        return self.samples[-n:]

    def voice_prompt(self, task: str, category: str = "") -> str:
        """Generate a prompt that includes voice context."""
        samples = self.best_samples(category, n=5)
        if not samples:
            return f"""Write the following for {self.candidate_name}'s campaign:

{task}

Write in a warm, authentic, community-focused voice. Keep it conversational
and specific to the district. Include [AI-assisted draft] at the end."""

        examples = "\n\n---\n\n".join(
            f"[{s.source}]: {s.text}" for s in samples
        )

        return f"""You are drafting content for {self.candidate_name}'s campaign.

Here are examples of how {self.candidate_name} actually writes and speaks:

{examples}

---

Now write the following IN THEIR VOICE — match their tone, vocabulary, and
style. Don't be generic. Sound like the person above, not like an AI:

{task}

IMPORTANT: Include [AI-assisted draft — needs review] at the end.
The candidate must approve before this goes out."""

    def summary(self) -> str:
        cats = {}
        for s in self.samples:
            c = s.category or "uncategorized"
            cats[c] = cats.get(c, 0) + 1
        cat_str = ", ".join(f"{k}: {v}" for k, v in sorted(cats.items()))
        return (f"Voice profile: {len(self.samples)} samples "
                f"({cat_str})")
