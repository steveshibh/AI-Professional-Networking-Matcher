# AI Professional Networking Matcher

A lightweight, robust intro matcher designed for professional networking and community platforms to connect members intelligently based on user queries.

---

## Part 1: Mini Intro Matcher

Given a query such as `"I need a backend engineer who has worked on payments"`, the matcher analyzes candidate profiles, computes weighted relevance scores across structured fields, and returns the top 3 matches with clear, human-readable match rationales.

### Candidate Profiles
1. **Priya** | Staff Engineer, fintech | Python, payments, Kafka | Bangalore
2. **Daniel** | Product Designer | Figma, design systems, mobile | San Francisco
3. **Mei** | Backend Engineer | Go, payments, Postgres | Singapore
4. **Arjun** | ML Engineer | PyTorch, ranking, recommendations | Palo Alto
5. **Sofia** | Founder, climate tech | fundraising, ops, hiring | London
6. **Wei** | Full-stack Engineer | TypeScript, React, Stripe | Singapore

### Key Design Decisions & Edge Cases
- **Field-Weighted Scoring**: Skills ($3.0\times$), Role/Title ($2.5\times$), Location ($1.0\times$). Direct skills and domain experience are prioritized over geographical mention.
- **Domain Synonym Expansion**: Expands company/tool indicators to domain concepts (e.g., `Stripe` $\leftrightarrow$ `payments`) so candidates like Wei are appropriately surfaced.
- **Edge Cases Handled**:
  - **Empty queries or whitespace**: Returns an empty match list `[]`.
  - **Stopwords-only queries**: Filtered out to avoid false keyword collisions.
  - **Zero matches**: Gracefully returns `[]`.
  - **Deterministic Tie-Breaking**: Ordered by `(-score, profile.name)` to avoid nondeterministic ranking jitter.

### Running the Code

Requires Python 3.8+ (standard library only, zero external dependencies).

```bash
# Run the demo queries
python3 intro_matcher.py

# Run unit tests
python3 -m unittest -v test_intro_matcher.py
```

#### Sample Output:
```text
Query: "I need a backend engineer who has worked on payments"
  1. Mei (Score: 8.5) | Matches on backend, engineer, payments (Backend Engineer with Go, payments, Postgres)
  2. Priya (Score: 5.5) | Matches on engineer, payments (Staff Engineer, fintech with Python, payments, Kafka)
  3. Wei (Score: 5.5) | Matches on engineer, payments (Full-stack Engineer with TypeScript, React, Stripe)

Query: "Looking for a designer in San Francisco"
  1. Daniel (Score: 4.5) | Matches on designer, san, francisco (Product Designer with Figma, design systems, mobile)

Query: ""
  No matching profiles found.

Query: "Rust and blockchain expert"
  No matching profiles found.
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
