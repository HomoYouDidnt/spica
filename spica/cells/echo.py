MANIFEST = {
    "name": "echo",
    "version": "0.1.0",
    "inputs": ["text"],
    "outputs": ["text"],
}


def run(context, text: str) -> dict:
    return {"text": text}
