from pathlib import Path

def ensure_paths(path: str):
    print(f"Ensuring the path exists: {path}")
    Path(path).mkdir(parents=True, exist_ok=True)