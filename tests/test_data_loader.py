from pathlib import Path
import csv

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


def test_load_graph_deduplicates_reverse_rows_for_undirected_data():
    root = Path(__file__).resolve().parents[1]
    loader = CairoDataLoader(root / "data")
    graph = loader.load_graph(include_potential_roads=False, directed=False)

    with (root / "data" / "existing_roads.csv").open("r", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    logical_pairs = {
        tuple(sorted((row["FromID"].strip(), row["ToID"].strip())))
        for row in rows
    }

    assert len(graph.unique_undirected_edges()) == len(logical_pairs)
