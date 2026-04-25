"""Public graph facade exposing only graph data structures and operations."""

from __future__ import annotations

try:
    from .graph_models import Edge, Node, TimeProfile
    from .graph_structure import GraphStructure
except ImportError:  
    from core.graph.graph_models import Edge, Node, TimeProfile
    from core.graph.graph_structure import GraphStructure


class Graph(GraphStructure):
    """Main graph."""

if __name__ == "__main__":
    graph = Graph(directed=False)
    graph.add_node(Node("A", "Maadi", "Residential", 31.25, 29.96, population=250000))
    graph.add_node(Node("B", "Nasr City", "Mixed", 31.34, 30.06, population=500000))
    graph.add_edge(Edge("A", "B", 8.5, 3000, 7))
    graph.add_time_profile("A", "B", TimeProfile(2800, 1500, 2600, 800))

    print("=== CairoFlow Graph Core Demo ===")
    print(f"Nodes: {len(graph.nodes)}")
    print(f"Adjacency entries from A: {len(list(graph.neighbors('A')))}")
    print(f"Has A-B time profile: {graph.get_time_profile('A', 'B') is not None}")
