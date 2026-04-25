"""Graph domain models (Node, Edge, TimeProfile)."""

from __future__ import annotations

from dataclasses import dataclass, field
from math import isfinite
from typing import Dict, Optional, Tuple

try:
    from .utils import VALID_TIME_SLOTS
except ImportError:  
    from core.graph.utils import VALID_TIME_SLOTS


@dataclass(frozen=True)
class Node:
    """A graph node representing a neighborhood or facility."""

    node_id: str
    name: str
    node_type: str
    x: float
    y: float
    population: int = 0
    metadata: Dict[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.node_id.strip():
            raise ValueError("node_id must be a non-empty string.")
        if not self.name.strip():
            raise ValueError("name must be a non-empty string.")
        if not self.node_type.strip():
            raise ValueError("node_type must be a non-empty string.")
        if not isfinite(self.x) or not isfinite(self.y):
            raise ValueError("Node coordinates must be finite numbers.")
        if self.population < 0:
            raise ValueError("population must be non-negative.")

    @property
    def coordinates(self) -> Tuple[float, float]:
        """Return `(x, y)` coordinates for spatial algorithms."""
        return (self.x, self.y)

    @property
    def is_facility(self) -> bool:
        """Return whether this node represents a facility entry."""
        return self.node_id.startswith("F")


@dataclass
class Edge:
    """Weighted road segment between two nodes."""

    from_id: str
    to_id: str
    distance_km: float
    capacity_veh_per_hour: float
    condition_score: float 
    construction_cost_million_egp: Optional[float] = None
    existing_road: bool = True
    metadata: Dict[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.from_id.strip() or not self.to_id.strip():
            raise ValueError("Edge endpoints must be non-empty strings.")
        if self.from_id == self.to_id:
            raise ValueError("Self-loop edges are not supported.")
        if self.distance_km <= 0:
            raise ValueError("distance_km must be greater than 0.")
        if self.capacity_veh_per_hour < 0:
            raise ValueError("capacity_veh_per_hour must be non-negative.")
        if not 1.0 <= self.condition_score <= 10.0:
            raise ValueError("condition_score must be between 1.0 and 10.0.")
        if self.existing_road and self.construction_cost_million_egp is not None:
            raise ValueError("Existing roads should not define construction_cost_million_egp.")
        if self.construction_cost_million_egp is not None and self.construction_cost_million_egp < 0:
            raise ValueError("construction_cost_million_egp must be non-negative when provided.")


@dataclass
class TimeProfile:
    """
    Stores traffic volume data for different times of the day.
    Allows the system to simulate Cairo's rush hours (Morning, Afternoon, Evening, Night).
    """

    morning_peak: float
    afternoon: float
    evening_peak: float
    night: float

    def __post_init__(self) -> None:
        for field_name, value in (
            ("morning_peak", self.morning_peak),
            ("afternoon", self.afternoon),
            ("evening_peak", self.evening_peak),
            ("night", self.night),
        ):
            if value < 0:
                raise ValueError(f"{field_name} must be non-negative.")

    def volume(self, time_slot: str) -> float:
        """Return the traffic volume for the requested time slot."""
        slot = time_slot.lower().strip()
        if slot not in VALID_TIME_SLOTS:
            raise ValueError(f"Invalid time slot '{time_slot}'. Expected one of {VALID_TIME_SLOTS}.")
        mapping = {
            "morning": self.morning_peak,
            "afternoon": self.afternoon,
            "evening": self.evening_peak,
            "night": self.night,
        }
        return mapping[slot]
    

# if __name__ == "__main__":
#     n = Node(node_id="F101", name="Kasr Al-Ainy", node_type="Medical", x=30.0, y=31.0)
#     print(f"Node: {n.name}, Is Facility? {n.is_facility}") 
    
#     try:
#         n.x = 40.0
#     except Exception as e:
#         print(f"Frozen Check: Success (Cannot modify frozen node)")

#     tp = TimeProfile(morning_peak=100.0, afternoon=50.0, evening_peak=120.0, night=10.0)
#     print(f"Morning Volume: {tp.volume('  MORNING  ')}") 

#     try:
#         tp.volume("Noon")
#     except ValueError as e:
#         print(f"Validation Check: Success ({e})")
