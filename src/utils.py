import os

def ensure_dir(path):
    """Create directory if it doesn't exist."""
    os.makedirs(path, exist_ok=True)

def truncate(text, max_chars=200):
    """Truncate text for display purposes."""
    return text[:max_chars] + "..." if len(text) > max_chars else text
