"""
intro_matcher.py
================
AI Professional Networking Matcher
-----------------------------------
Given a plain-English query (e.g. "I need a backend engineer who has worked
on payments"), this module scores every candidate profile against the query
and returns the top-k best matches with weighted relevance scores.

Scoring weights (highest wins per token):
  skill  → 3.0  (most important – direct skill overlap)
  title  → 2.5  (job-title match)
  loc    → 1.0  (location match)
"""

# ---------------------------------------------------------------------------
# Standard-library imports
# ---------------------------------------------------------------------------
import re                       # regex engine for tokenisation
from dataclasses import dataclass  # lightweight, immutable data containers


# ===========================================================================
# DATA MODELS
# Two frozen dataclasses act as simple, immutable value objects.
# ===========================================================================

@dataclass(frozen=True)
class Profile:
    """
    Represents a single professional's public networking profile.

    Attributes
    ----------
    name     : Full name of the person.
    title    : Job title / role (e.g. "Backend Engineer").
    skills   : Tuple of skill/domain keywords (e.g. ("Python", "payments")).
    location : City or region the person is based in.

    Why frozen=True?
    ----------------
    Makes instances hashable and prevents accidental mutation after creation,
    which is important when profiles are used as dict keys or in sets.
    """
    name: str
    title: str
    skills: tuple[str, ...]
    location: str


@dataclass(frozen=True)
class Match:
    """
    Wraps a Profile together with its relevance score for a specific query.

    Attributes
    ----------
    profile : The matched Profile object.
    score   : Cumulative weighted relevance score (higher = better match).
    hits    : Tuple of query tokens that actually matched this profile.

    Separation of concerns
    ----------------------
    Keeping score/hits separate from Profile means that the same Profile can
    participate in many different queries with different scores.
    """
    profile: Profile
    score: float
    hits: tuple[str, ...]


# ===========================================================================
# CONFIGURATION CONSTANTS
# Centralised so they are easy to tune without touching matching logic.
# ===========================================================================

# Tokens that carry no semantic signal and should be ignored during matching.
# Extending this set improves precision without changing any other code.
STOP = {
    "i", "need", "a", "an", "who", "has", "worked", "on", "in", "with",
    "for", "the", "to", "and", "of", "me", "someone", "looking", "find"
}

# Domain-synonym map: maps a specific tool/company name to its broader domain.
# e.g. "stripe" → "payments" so querying "payments" also surfaces Stripe users.
ALIASES = {"stripe": "payments"}

# Field weights: how many relevance points a matching token earns per field.
# "skill" outweighs "title" which outweighs "loc" to reflect hiring priorities.
WEIGHTS = {"skill": 3.0, "title": 2.5, "loc": 1.0}


# ===========================================================================
# TEXT NORMALISATION HELPERS
# ===========================================================================

def _norm(w: str) -> str:
    """
    Normalise a single word to a canonical form.

    Two transformations are applied in order:

    1. Alias expansion  – replace known synonyms before stemming
       e.g. "stripe" → "payments"

    2. Naïve plural stemming – strip a trailing 's' when:
         - the word is longer than 3 characters  (preserves "ops", "go", etc.)
         - it doesn't end with "ss"               (preserves "lass", "boss")
       e.g. "payments" → "payment", "engineers" → "engineer"
       This keeps singular and plural queries equivalent without an external
       NLP library.
    """
    # Step 1: apply alias/synonym map
    w = ALIASES.get(w, w)
    # Step 2: strip trailing plural 's' if safe to do so
    return w[:-1] if len(w) > 3 and w.endswith("s") and not w.endswith("ss") else w


def tokenize(text: str) -> set[str]:
    """
    Convert a free-form text string into a set of normalised, meaningful tokens.

    Pipeline:
      text → lowercase → extract word characters → remove stopwords → normalise

    Returns a *set* (not a list) so each unique concept is counted only once,
    preventing double-scoring if the same word appears twice in a query.

    Parameters
    ----------
    text : Any plain-text string (query or profile field).

    Returns
    -------
    set[str] : Zero or more normalised, non-stopword tokens.
    """
    return {
        _norm(w)
        for w in re.findall(r"\w+", text.lower())  # split on non-word chars
        if w not in STOP                            # discard stopwords
    }


# ===========================================================================
# PROFILE DATABASE
# In production this would be fetched from a database or search index.
# For the demo, six sample profiles are hard-coded.
# ===========================================================================

PROFILES = [
    Profile("Priya",  "Staff Engineer, fintech",   ("Python", "payments", "Kafka"),              "Bangalore"),
    Profile("Daniel", "Product Designer",           ("Figma", "design systems", "mobile"),        "San Francisco"),
    Profile("Mei",    "Backend Engineer",            ("Go", "payments", "Postgres"),               "Singapore"),
    Profile("Arjun",  "ML Engineer",                ("PyTorch", "ranking", "recommendations"),    "Palo Alto"),
    Profile("Sofia",  "Founder, climate tech",      ("fundraising", "ops", "hiring"),             "London"),
    Profile("Wei",    "Full-stack Engineer",         ("TypeScript", "React", "Stripe"),            "Singapore"),
]


# ===========================================================================
# CORE MATCHING LOGIC
# ===========================================================================

def match(query: str, top_k: int = 3) -> list[Match]:
    """
    Score every profile against *query* and return the top-k best matches.

    Algorithm (per profile):
      1. Tokenise the query into a set of meaningful terms.
      2. For each query token, check which profile fields (skill / title / loc)
         contain it.
      3. Award the *maximum* applicable field weight (not the sum) so a token
         that matches both skill and title is not double-counted.
      4. Accumulate field weights into a total score; track which tokens hit.
      5. Discard profiles with score = 0 (no overlap with the query).
      6. Sort by (-score, name) for deterministic ordering on ties.
      7. Return the top-k entries.

    Parameters
    ----------
    query : Plain-English search query from the user.
    top_k : Maximum number of results to return (must be > 0).

    Returns
    -------
    list[Match] : Up to top_k Match objects, best match first.
                  Returns [] for empty queries or top_k ≤ 0.

    Edge cases handled
    ------------------
    - Empty / whitespace-only query          → returns []
    - Query consisting only of stopwords     → returns []
    - top_k ≤ 0                              → returns []
    - Query with no matching profiles        → returns []
    """
    # --- Guard: tokenise query first; bail out if nothing meaningful remains ---
    tokens = tokenize(query)
    if not tokens or top_k <= 0:
        return []

    results = []

    # --- Score each profile against the query ---
    for p in PROFILES:
        # Pre-tokenise every field of this profile once (avoids repeated work)
        fields = {
            "skill": tokenize(" ".join(p.skills)),  # skill set as one string
            "title": tokenize(p.title),
            "loc":   tokenize(p.location),
        }

        score, hits = 0.0, []

        # Iterate tokens in sorted order → deterministic hit recording
        for t in sorted(tokens):
            # Find the highest weight among all fields that contain this token.
            # max(..., default=0.0) safely handles the case where t matches nothing.
            w = max(
                (WEIGHTS[f] for f, toks in fields.items() if t in toks),
                default=0.0
            )
            if w:
                score += w        # accumulate relevance score
                hits.append(t)    # record which query term contributed

        # Only keep profiles that have at least one matching token
        if score > 0:
            results.append(Match(p, score, tuple(hits)))

    # --- Rank: highest score first; alphabetical name breaks ties ---
    results.sort(key=lambda m: (-m.score, m.profile.name))

    # --- Truncate to the requested number of results ---
    return results[:top_k]


# ===========================================================================
# OUTPUT FORMATTING
# ===========================================================================

def format_match(m: Match) -> str:
    """
    Render a Match as a human-readable single-line summary.

    Format:
        <Name> (Score: <X.X> | Matches on <tokens> (<title>; <skills>))

    Example:
        Mei (Score: 8.0 | Matches on backend, engineer, payment
             (Backend Engineer; Go, payments, Postgres))

    Parameters
    ----------
    m : A Match object returned by the match() function.

    Returns
    -------
    str : Formatted summary string suitable for printing or logging.
    """
    p = m.profile
    return (
        f"{p.name} (Score: {m.score:.1f} | "
        f"Matches on {', '.join(m.hits)} "
        f"({p.title}; {', '.join(p.skills)}))"
    )


# ===========================================================================
# DEMO ENTRY POINT
# Run directly with:  python3 intro_matcher.py
# ===========================================================================

if __name__ == "__main__":
    # Sample query that exercises title, skill, and synonym matching
    q = "I need a backend engineer who has worked on payments"
    print(f'Query: "{q}"')
    for m in match(q):
        print(f" - {format_match(m)}")
