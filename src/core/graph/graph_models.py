"""Graph domain models (Node, Edge, TimeProfile)."""

from __future__ import annotations

from dataclasses import dataclass, field
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

    @property
    def coordinates(self) -> Tuple[float, float]:
        return (self.x, self.y)

    @property
    def is_facility(self) -> bool:
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

    def volume(self, time_slot: str) -> float:
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