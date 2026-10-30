# AI Professional Networking Matcher

A compact (<40 lines), production-minded intro matcher designed for professional networking and community platforms to connect members intelligently based on user queries.

---

## Part 1: Mini Intro Matcher (31 Lines)

Given a query such as `"I need a backend engineer who has worked on payments"`, the matcher analyzes candidate profiles, computes weighted relevance scores across structured fields, and returns the top 3 matches with clear, human-readable match rationales.

```python
import re

PROFILES = [
    ("Priya", "Staff Engineer, fintech", ["Python", "payments", "Kafka"], "Bangalore"),
    ("Daniel", "Product Designer", ["Figma", "design systems", "mobile"], "San Francisco"),
    ("Mei", "Backend Engineer", ["Go", "payments", "Postgres"], "Singapore"),
    ("Arjun", "ML Engineer", ["PyTorch", "ranking", "recommendations"], "Palo Alto"),
    ("Sofia", "Founder, climate tech", ["fundraising", "ops", "hiring"], "London"),
    ("Wei", "Full-stack Engineer", ["TypeScript", "React", "Stripe"], "Singapore"),
]
STOP = {"i", "need", "a", "an", "who", "has", "worked", "on", "in", "with", "for", "the"}
ALIASES = {"stripe": "payments"}

def match(query: str, top_k: int = 3):
    tokens = {ALIASES.get(w, w) for w in re.findall(r"\w+", query.lower()) if w not in STOP}
    if not tokens: return []
    ranked = []
    for name, title, skills, loc in PROFILES:
        t_hits = tokens & set(re.findall(r"\w+", title.lower()))
        s_hits = (tokens & {ALIASES.get(w, w) for s in skills for w in re.findall(r"\w+", s.lower())}) - t_hits
        l_hits = tokens & set(re.findall(r"\w+", loc.lower()))
        score = len(s_hits) * 3.0 + len(t_hits) * 2.5 + len(l_hits) * 1.0
        if score > 0:
            hits = ", ".join(t_hits | s_hits | l_hits)
            ranked.append((-score, name, f"{score:.1f} | Matches on {hits} ({title}; {', '.join(skills)})"))
    return [f"{name} (Score: {msg})" for _, name, msg in sorted(ranked)[:top_k]]

if __name__ == "__main__":
    q = "I need a backend engineer who has worked on payments"
    print(f"Query: {q}")
    for res in match(q): print(f" - {res}")
```

### Key Design Decisions & Edge Cases
- **Field-Weighted Scoring**: Skills ($3.0\times$), Role/Title ($2.5\times$), Location ($1.0\times$). Direct skills and domain experience are prioritized over geographical mention.
- **Domain Synonym Expansion**: Expands company/tool indicators to domain concepts (e.g., `Stripe` $\leftrightarrow$ `payments`) so candidates like Wei are appropriately surfaced.
- **Edge Cases Handled**:
  - **Empty queries or whitespace**: Returns an empty match list `[]`.
  - **Stopwords-only queries**: Filtered out to avoid false keyword collisions.
  - **Zero matches**: Gracefully returns `[]`.
  - **Deterministic Tie-Breaking**: Ordered by `(-score, name)` to avoid nondeterministic ranking jitter.

### Running the Code

```bash
# Run the demo queries
python3 intro_matcher.py

# Run unit tests
python3 -m unittest -v test_intro_matcher.py
```

#### Output:
```text
Query: I need a backend engineer who has worked on payments
 - Mei (Score: 8.0 | Matches on payments, engineer, backend (Backend Engineer; Go, payments, Postgres))
 - Priya (Score: 5.5 | Matches on engineer, payments (Staff Engineer, fintech; Python, payments, Kafka))
 - Wei (Score: 5.5 | Matches on engineer, payments (Full-stack Engineer; TypeScript, React, Stripe))
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
