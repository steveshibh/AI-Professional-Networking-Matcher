# AI Professional Networking Matcher

A typed, immutable, and production-structured intro matcher designed for professional networking and community platforms to connect members intelligently based on user queries.

---

## Part 1: Mini Intro Matcher

Given a query such as `"I need a backend engineer who has worked on payments"`, the matcher analyzes candidate profiles, computes weighted relevance scores across structured fields, and returns the top 3 matches with clear, human-readable match rationales.

```python
import re
from dataclasses import dataclass

@dataclass(frozen=True)
class Profile:
    name: str
    title: str
    skills: tuple[str, ...]
    location: str

@dataclass(frozen=True)
class Match:
    profile: Profile
    score: float
    hits: tuple[str, ...]

STOP = {"i", "need", "a", "an", "who", "has", "worked", "on", "in", "with",
        "for", "the", "to", "and", "of", "me", "someone", "looking", "find"}
ALIASES = {"stripe": "payments"}
WEIGHTS = {"skill": 3.0, "title": 2.5, "loc": 1.0}

def _norm(w: str) -> str:
    w = ALIASES.get(w, w)
    return w[:-1] if len(w) > 3 and w.endswith("s") and not w.endswith("ss") else w

def tokenize(text: str) -> set[str]:
    return {_norm(w) for w in re.findall(r"\w+", text.lower()) if w not in STOP}

PROFILES = [
    Profile("Priya", "Staff Engineer, fintech", ("Python", "payments", "Kafka"), "Bangalore"),
    Profile("Daniel", "Product Designer", ("Figma", "design systems", "mobile"), "San Francisco"),
    Profile("Mei", "Backend Engineer", ("Go", "payments", "Postgres"), "Singapore"),
    Profile("Arjun", "ML Engineer", ("PyTorch", "ranking", "recommendations"), "Palo Alto"),
    Profile("Sofia", "Founder, climate tech", ("fundraising", "ops", "hiring"), "London"),
    Profile("Wei", "Full-stack Engineer", ("TypeScript", "React", "Stripe"), "Singapore"),
]

def match(query: str, top_k: int = 3) -> list[Match]:
    tokens = tokenize(query)
    if not tokens or top_k <= 0:
        return []
    results = []
    for p in PROFILES:
        fields = {
            "skill": tokenize(" ".join(p.skills)),
            "title": tokenize(p.title),
            "loc": tokenize(p.location),
        }
        score, hits = 0.0, []
        for t in sorted(tokens):
            w = max((WEIGHTS[f] for f, toks in fields.items() if t in toks), default=0.0)
            if w:
                score += w
                hits.append(t)
        if score > 0:
            results.append(Match(p, score, tuple(hits)))
    results.sort(key=lambda m: (-m.score, m.profile.name))
    return results[:top_k]

def format_match(m: Match) -> str:
    p = m.profile
    return (f"{p.name} (Score: {m.score:.1f} | Matches on {', '.join(m.hits)} "
            f"({p.title}; {', '.join(p.skills)}))")

if __name__ == "__main__":
    q = "I need a backend engineer who has worked on payments"
    print(f"Query: \"{q}\"")
    for m in match(q):
        print(f" - {format_match(m)}")
```

### Key Design Decisions & Edge Cases
- **Typed & Immutable (`@dataclass(frozen=True)`)**: Separates data retrieval (`Match`) from user presentation (`format_match`).
- **No Over-Counting via Max Field Weight**: A query term appearing in both a candidate's title and skills receives the highest applicable field weight (`skill` > `title` > `loc`) rather than falsely inflating scores.
- **Normalization & Stemming**: `_norm(w)` collapses plurals (`payment` $\leftrightarrow$ `payments`) while preserving short terms like `ops` via length bounds.
- **Domain Synonym Expansion**: Expands company/tool indicators to domain concepts (e.g., `Stripe` $\leftrightarrow$ `payments`).
- **Edge Cases Handled**:
  - Empty or whitespace-only queries.
  - Queries with non-positive `top_k` limits (`top_k <= 0`).
  - Stopword-only queries.
  - Zero-match queries.
  - Deterministic tie-breaking on `(-m.score, m.profile.name)`.

### Running the Code

```bash
# Run the demo queries
python3 intro_matcher.py

# Run unit tests
python3 -m unittest -v test_intro_matcher.py
```

#### Output:
```text
Query: "I need a backend engineer who has worked on payments"
 - Mei (Score: 8.0 | Matches on backend, engineer, payment (Backend Engineer; Go, payments, Postgres))
 - Priya (Score: 5.5 | Matches on engineer, payment (Staff Engineer, fintech; Python, payments, Kafka))
 - Wei (Score: 5.5 | Matches on engineer, payment (Full-stack Engineer; TypeScript, React, Stripe))
```

---

## Part 2: Scaling & Evaluation (Short Written Answer)

> To scale to 10 million profiles, I would implement a two-stage retrieval pipeline: an approximate nearest-neighbor (ANN) vector search (e.g., Milvus/Pinecone using HNSW indexes on multi-field profile embeddings) coupled with inverted boolean filters (Elasticsearch) for hard criteria like geo and seniority, feeding the top 200 candidates to a cross-encoder reranker. For professional intro matching, scoring must be mutual rather than purely asymmetric search, evaluating two-way relevance, current availability, and anti-spam rate limits. To evaluate match quality offline, I would track NDCG@k and Mean Reciprocal Rank (MRR) against curated evaluator benchmarks and synthetic relevance pairs. Online, the truest signals of match quality are double-opt-in acceptance rate (both parties agreeing to connect), conversation depth (exchanging $\ge 3$ follow-up messages), and post-intro NPS survey ratings.

---

## Tradeoffs & Future Iterations

| Dimension | Mini Version | Production Scale (10M Profiles) |
| :--- | :--- | :--- |
| **Search Mechanism** | Regex tokenization + stopword stripping + synonym map | Hybrid Dense Retrieval (Bi-encoder embeddings) + Sparse Lexical (BM25) |
| **Latency** | $< 1\text{ms}$ in-memory linear scan | $\le 40\text{ms}$ sub-linear ANN index lookups |
| **Mutual Intent** | One-way query matching | Two-way preference compatibility matrix (reciprocal recommendation) |
| **Cold Start** | Requires filled profile fields | Graph-based collaborative filtering (co-attendance, mutual network links) |

---

## AI Disclosure
Developed with the assistance of Google Antigravity / Gemini for formatting and unit test scaffolding.
