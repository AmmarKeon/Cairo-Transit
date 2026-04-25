from pathlib import Path

from core.graph import CairoDataLoader


def test_load_graph_from_project_data():
    root = Path(__file__).resolve().parents[1]
    loader = CairoDataLoader(root / "data")
    graph = loader.load_graph(include_potential_roads=False)

    assert len(graph.nodes) > 0
    assert len(graph.adjacency) > 0
    assert len(graph.time_profiles) > 0

    first_node_id = next(iter(graph.nodes.keys()))
    assert isinstance(list(graph.neighbors(first_node_id)), list)
