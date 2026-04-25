"""Utility helpers shared across CairoFlow core modules."""

from __future__ import annotations

from math import sqrt
from typing import Dict, List, Optional, Sequence


VALID_TIME_SLOTS = {"morning", "afternoon", "evening", "night"}

def canonical_edge_key(from_id: str, to_id: str, directed: bool) -> str:
	"""Return a stable edge identifier used for maps and lookups."""
	if directed:
		return f"{from_id}->{to_id}"
	if from_id <= to_id:
		return f"{from_id}-{to_id}"
	return f"{to_id}-{from_id}"

