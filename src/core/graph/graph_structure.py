"""Graph storage and mutation operations (adjacency-list structure)."""

from __future__ import annotations

from typing import Dict, Iterable, List, Optional

try:    
    from .graph_models import Edge, Node, TimeProfile
    from .utils import canonical_edge_key
except ImportError:  
    from core.graph.graph_models import Edge, Node, TimeProfile
    from core.graph.utils import canonical_edge_key


class GraphStructure:
    """Adjacency-list graph state and non-algorithm operations."""

    def __init__(self, directed: bool = False) -> None:
        self.directed = directed
        self.nodes: Dict[str, Node] = {}
        self.adjacency: Dict[str, List[Edge]] = {}
        self.time_profiles: Dict[str, TimeProfile] = {}

    def add_node(self, node: Node) -> None:
        self.nodes[node.node_id] = node
        self.adjacency.setdefault(node.node_id, [])

    def add_edge(self, edge: Edge) -> None:
        if edge.from_id not in self.nodes or edge.to_id not in self.nodes:
            raise ValueError("Both edge endpoints must be added as nodes before adding an edge.")

        self.adjacency.setdefault(edge.from_id, []).append(edge)

        if not self.directed:
            self.adjacency.setdefault(edge.to_id, []).append(
                Edge(
                    from_id=edge.to_id,
                    to_id=edge.from_id,
                    distance_km=edge.distance_km,
                    capacity_veh_per_hour=edge.capacity_veh_per_hour,
                    condition_score=edge.condition_score,
                    construction_cost_million_egp=edge.construction_cost_million_egp,
                    existing_road=edge.existing_road,
                    metadata=dict(edge.metadata),
                )
            )

    def add_time_profile(self, from_id: str, to_id: str, profile: TimeProfile) -> None:
        key = canonical_edge_key(from_id, to_id, self.directed)
        self.time_profiles[key] = profile

    def get_time_profile(self, from_id: str, to_id: str) -> Optional[TimeProfile]:
        key = canonical_edge_key(from_id, to_id, self.directed)
        return self.time_profiles.get(key)

    def close_road(self, from_id: str, to_id: str) -> None:
        self._set_road_state(from_id, to_id, closed=True)

    def open_road(self, from_id: str, to_id: str) -> None:
        self._set_road_state(from_id, to_id, closed=False)

    def neighbors(self, node_id: str) -> Iterable[Edge]:
        return self.adjacency.get(node_id, [])

    def _set_road_state(self, from_id: str, to_id: str, closed: bool) -> None:
        changed = False
        for edge in self.adjacency.get(from_id, []):
            if edge.to_id == to_id:
                edge.metadata["closed"] = closed
                changed = True
        if not self.directed:
            for edge in self.adjacency.get(to_id, []):
                if edge.to_id == from_id:
                    edge.metadata["closed"] = closed
                    changed = True
        if not changed:
            raise ValueError(f"Road {from_id} <-> {to_id} does not exist.")

    def assert_node_exists(self, node_id: str) -> None:
        if node_id not in self.nodes:
            raise ValueError(f"Unknown node '{node_id}'")

    def get_edge(self, from_id: str, to_id: str) -> Optional[Edge]:
        for edge in self.adjacency.get(from_id, []):
            if edge.to_id == to_id:
                return edge
        return None

    def unique_undirected_edges(self) -> List[Edge]:
        seen = set()
        unique: List[Edge] = []
        for node_edges in self.adjacency.values():
            for edge in node_edges:
                key = canonical_edge_key(edge.from_id, edge.to_id, directed=False)
                if key in seen:
                    continue
                seen.add(key)
                unique.append(edge)
        return unique
