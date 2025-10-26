MANIFEST = {
    "name": "uppercase",
    "version": "0.1.0",
    "inputs": ["text"],
    "outputs": ["text"],
    "governance": {"risk_class": "low", "data_scopes": ["public"]},
    "resources": {"cpu": "1", "ram_mb": 64, "gpu": "none"},
}


def run(context, text: str) -> dict:
    return {"text": text.upper()}
