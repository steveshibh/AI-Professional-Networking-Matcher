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
