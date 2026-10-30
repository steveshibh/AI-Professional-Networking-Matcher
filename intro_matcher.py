"""Mini Intro Matcher for Professional Networking and Communities.

Matches queries against candidate profiles with scoring, edge-case handling,
and human-readable match explanations.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Set, Tuple


@dataclass
class Profile:
    name: str
    title: str
    skills: list[str]
    location: str
    _searchable_tokens: set[str] = field(init=False, repr=False, default_factory=set)

    def __post_init__(self) -> None:
        # Domain aliases / synonyms expand recall (e.g. Stripe -> payments)
        aliases = {"stripe": "payments"}
        raw = f"{self.title} {' '.join(self.skills)} {self.location}".lower()
        tokens = set(re.findall(r"\w+", raw))
        self._searchable_tokens = tokens | {aliases[t] for t in tokens if t in aliases}

    @property
    def searchable_tokens(self) -> set[str]:
        return self._searchable_tokens


# Canonical profiles from requirement
DEFAULT_PROFILES: list[Profile] = [
    Profile("Priya", "Staff Engineer, fintech", ["Python", "payments", "Kafka"], "Bangalore"),
    Profile("Daniel", "Product Designer", ["Figma", "design systems", "mobile"], "San Francisco"),
    Profile("Mei", "Backend Engineer", ["Go", "payments", "Postgres"], "Singapore"),
    Profile("Arjun", "ML Engineer", ["PyTorch", "ranking", "recommendations"], "Palo Alto"),
    Profile("Sofia", "Founder, climate tech", ["fundraising", "ops", "hiring"], "London"),
    Profile("Wei", "Full-stack Engineer", ["TypeScript", "React", "Stripe"], "Singapore"),
]

# Standard conversational stopwords
STOPWORDS: set[str] = {
    "i", "need", "a", "an", "the", "who", "has", "have", "worked", "on", "in",
    "with", "for", "looking", "to", "and", "or", "at", "expert", "someone",
}


def match_profiles(
    query: str,
    profiles: list[Profile] | None = None,
    top_k: int = 3,
) -> list[tuple[float, str, Profile]]:
    """Match a natural language query against a list of candidate profiles.

    Args:
        query: User input query (e.g., 'I need a backend engineer who has worked on payments')
        profiles: Candidate list of profiles. Defaults to DEFAULT_PROFILES if None.
        top_k: Maximum number of top matches to return.

    Returns:
        List of tuples: (score, one_line_reason, profile) sorted by score descending.
    """
    if profiles is None:
        profiles = DEFAULT_PROFILES

    if not query or not query.strip():
        return []

    query_tokens = [w for w in re.findall(r"\w+", query.lower()) if w not in STOPWORDS]
    if not query_tokens:
        return []

    results: list[tuple[float, str, Profile]] = []

    for p in profiles:
        title_tokens = set(re.findall(r"\w+", p.title.lower()))
        loc_tokens = set(re.findall(r"\w+", p.location.lower()))

        title_hits = [w for w in query_tokens if w in title_tokens]
        skill_hits = [
            w for w in query_tokens
            if w in p.searchable_tokens and w not in title_hits and w not in loc_tokens
        ]
        loc_hits = [w for w in query_tokens if w in loc_tokens]

        # Scoring weights: Skills (3.0), Role/Title (2.5), Location (1.0)
        score = (len(skill_hits) * 3.0) + (len(title_hits) * 2.5) + (len(loc_hits) * 1.0)

        if score > 0:
            matched_terms = list(dict.fromkeys(title_hits + skill_hits + loc_hits))
            reason = (
                f"Matches on {', '.join(matched_terms)} "
                f"({p.title} with {', '.join(p.skills)})"
            )
            results.append((score, reason, p))

    # Sort descending by score; ties broken deterministically by profile name
    results.sort(key=lambda x: (-x[0], x[2].name))
    return results[:top_k]


if __name__ == "__main__":
    sample_queries = [
        "I need a backend engineer who has worked on payments",
        "Looking for a designer in San Francisco",
        "",  # Edge case: empty query
        "Rust and blockchain expert",  # Edge case: zero matches
    ]

    for q in sample_queries:
        print(f"\nQuery: \"{q}\"")
        matches = match_profiles(q)
        if not matches:
            print("  No matching profiles found.")
        for rank, (score, reason, p) in enumerate(matches, 1):
            print(f"  {rank}. {p.name} (Score: {score:.1f}) | {reason}")
