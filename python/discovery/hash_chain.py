"""
python/discovery/hash_chain.py - The hash-chained event log of the cited-results registry (ADR-DISCOVERY-083), shared
with the freeze service (ADR-DISCOVERY-085).

Each event carries its sequence number, its kind, a payload, the wall-clock time and the hash of the previous event.
Its own hash is the SHA-256 of the canonical JSON of everything except `at` and `hash`. Editing, removing or
reordering an event breaks the chain from that event on, and `verify` refuses the log. A time that must be covered by
the hash, such as the moment criteria were frozen, goes in the payload.
"""

from __future__ import annotations

from typing import Any, Dict, List, Type

from python.discovery import formal_provenance


def append(events: List[Dict[str, Any]], kind: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Appends one event to `events` and returns it."""
    prev = events[-1]["hash"] if events else ""
    event = {"seq": len(events) + 1, "kind": kind, "payload": payload, "at": formal_provenance.utc_now(), "prev": prev}
    event["hash"] = formal_provenance.sha256_canonical({k: v for k, v in event.items() if k != "at"})
    events.append(event)
    return event


def verify(events: List[Dict[str, Any]], error: Type[Exception], what: str = "store") -> None:
    """Raises `error` at the first event whose sequence, link or hash does not match."""
    prev = ""
    for i, event in enumerate(events, start=1):
        expected = formal_provenance.sha256_canonical({k: v for k, v in event.items() if k not in ("at", "hash")})
        if event.get("seq") != i or event.get("prev") != prev or event.get("hash") != expected:
            raise error(f"Event log broken at event {i}; the {what} was edited outside its service.")
        prev = event["hash"]
