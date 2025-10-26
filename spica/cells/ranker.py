MANIFEST = {
    "name": "ranker",
    "version": "0.1.0",
    "inputs": ["candidates", "query"],
    "outputs": ["selected"],
    "governance": {"risk_class": "low", "data_scopes": ["public"]},
    "resources": {"cpu": "1", "ram_mb": 64, "gpu": "none"},
}


def run(context, candidates, query: str) -> dict:
    # Toy ranker: pick candidate with highest substring overlap
    scored = sorted(
        candidates,
        key=lambda c: sum(w in c for w in query.split()),
        reverse=True,
    )
    return {"selected": scored[:1] if scored else []}
