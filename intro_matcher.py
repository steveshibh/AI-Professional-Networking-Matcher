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
