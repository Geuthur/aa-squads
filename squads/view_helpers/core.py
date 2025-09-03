"""Core view helpers for squads app."""

# Standard Library
import hashlib
import time


def generate_unique_id():
    return hashlib.sha256(str(time.time()).encode()).hexdigest()[:12]
