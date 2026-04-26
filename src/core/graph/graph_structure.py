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
        """Initialize graph storage for nodes, edges, and time profiles."""
        self.directed = directed
        self.nodes: Dict[str, Node] = {}
        self.adjacency: Dict[str, List[Edge]] = {}
        self.time_profiles: Dict[str, TimeProfile] = {}
        
    def get_node(self, node_id: str) -> Optional[Node]:
        """Return a node by ID, or None if absent."""
        return self.nodes.get(node_id)
        
    def add_node(self, node: Node) -> None:
        """Add a node to the graph and create its adjacency bucket."""
        if node.node_id in self.nodes:
            raise ValueError(f"Node '{node.node_id}' already exists.")
        self.nodes[node.node_id] = node
        self.adjacency.setdefault(node.node_id, [])

    def add_edge(self, edge: Edge) -> None:
        """Add an edge after validating endpoints and duplicate state."""
        if edge.from_id not in self.nodes or edge.to_id not in self.nodes:
            raise ValueError("Both edge endpoints must be added as nodes before adding an edge.")
        if self.get_edge(edge.from_id, edge.to_id) is not None:
            raise ValueError(f"Edge '{edge.from_id}' -> '{edge.to_id}' already exists.")
        if not self.directed and self.get_edge(edge.to_id, edge.from_id) is not None:
            raise ValueError(f"Edge '{edge.from_id}' <-> '{edge.to_id}' already exists.")

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
        """Attach a time profile to an existing edge."""
        if self.get_edge(from_id, to_id) is None:
            raise ValueError(f"Cannot attach a time profile to missing edge '{from_id}' -> '{to_id}'.")
        key = canonical_edge_key(from_id, to_id, self.directed)
        self.time_profiles[key] = profile

    def get_time_profile(self, from_id: str, to_id: str) -> Optional[TimeProfile]:
        """Return the time profile for an edge if one exists."""
        key = canonical_edge_key(from_id, to_id, self.directed)
        return self.time_profiles.get(key)

    def close_road(self, from_id: str, to_id: str) -> None:
        """Mark an edge as closed via `metadata['closed'] = True`."""
        self._set_road_state(from_id, to_id, closed=True)

    def open_road(self, from_id: str, to_id: str) -> None:
        """Mark an edge as open via `metadata['closed'] = False`."""
        self._set_road_state(from_id, to_id, closed=False)

    def neighbors(self, node_id: str) -> Iterable[Edge]:
        """Return outgoing edges for a node, or an empty iterable if absent."""
        return self.adjacency.get(node_id, [])

    def _set_road_state(self, from_id: str, to_id: str, closed: bool) -> None:
        """Update road state on an edge and its reverse copy when undirected."""
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
        """Raise when a node ID is not present in the graph."""
        if node_id not in self.nodes:
            raise ValueError(f"Unknown node '{node_id}'")

    def get_edge(self, from_id: str, to_id: str) -> Optional[Edge]:
        """Return a single matching edge, or `None` if absent."""
        for edge in self.adjacency.get(from_id, []):
            if edge.to_id == to_id:
                return edge
        return None

    def unique_undirected_edges(self) -> List[Edge]:
        """Return each logical edge once for undirected-graph consumers."""
        if self.directed:
            raise ValueError("unique_undirected_edges() is only available for undirected graphs.")
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
