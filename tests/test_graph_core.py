import pytest

from core.graph import Edge, Graph, Node, TimeProfile


def build_test_graph() -> Graph:
    graph = Graph(directed=False)
    graph.add_node(Node("1", "A", "Residential", 0.0, 0.0, population=1000))
    graph.add_node(Node("2", "B", "Residential", 1.0, 0.0, population=2000))
    graph.add_node(Node("3", "C", "Medical", 2.0, 0.0, population=0))

    graph.add_edge(Edge("1", "2", 10.0, 1000.0, 7.0))
    graph.add_edge(Edge("2", "3", 5.0, 1000.0, 8.0))
    graph.add_edge(Edge("1", "3", 30.0, 1000.0, 7.0))

    graph.add_time_profile("1", "2", TimeProfile(3000.0, 800.0, 2800.0, 200.0))
    graph.add_time_profile("2", "3", TimeProfile(900.0, 700.0, 800.0, 200.0))
    graph.add_time_profile("1", "3", TimeProfile(500.0, 500.0, 500.0, 200.0))
    return graph


def test_add_node_and_edge_updates_adjacency():
    graph = build_test_graph()
    neighbors = list(graph.neighbors("1"))
    assert len(neighbors) == 2
    assert {edge.to_id for edge in neighbors} == {"2", "3"}


def test_time_profile_is_registered():
    graph = build_test_graph()
    profile = graph.get_time_profile("1", "2")
    assert profile is not None
    assert profile.volume("morning") == 3000.0


def test_road_closure_marks_edge_closed():
    graph = build_test_graph()
    graph.close_road("1", "2")
    edges = list(graph.neighbors("1"))
    edge = next(edge for edge in edges if edge.to_id == "2")
    assert edge.metadata.get("closed") is True


def test_road_reopen_unmarks_closed_flag():
    graph = build_test_graph()
    graph.close_road("1", "2")
    graph.open_road("1", "2")
    edges = list(graph.neighbors("1"))
    edge = next(edge for edge in edges if edge.to_id == "2")
    assert edge.metadata.get("closed") is False


def test_add_edge_requires_existing_nodes():
    graph = Graph(directed=False)
    with pytest.raises(ValueError, match="Both edge endpoints"):
        graph.add_edge(Edge("1", "2", 10.0, 1000.0, 7.0))


def test_add_node_rejects_duplicate_ids():
    graph = Graph(directed=False)
    graph.add_node(Node("1", "A", "Residential", 0.0, 0.0, population=1000))

    with pytest.raises(ValueError, match="already exists"):
        graph.add_node(Node("1", "A2", "Residential", 1.0, 1.0, population=500))


def test_add_edge_rejects_duplicate_logical_edge_in_undirected_graph():
    graph = Graph(directed=False)
    graph.add_node(Node("1", "A", "Residential", 0.0, 0.0, population=1000))
    graph.add_node(Node("2", "B", "Residential", 1.0, 0.0, population=2000))
    graph.add_edge(Edge("1", "2", 10.0, 1000.0, 7.0))

    with pytest.raises(ValueError, match="already exists"):
        graph.add_edge(Edge("2", "1", 10.0, 1000.0, 7.0))


def test_add_time_profile_requires_existing_edge():
    graph = Graph(directed=False)
    graph.add_node(Node("1", "A", "Residential", 0.0, 0.0, population=1000))
    graph.add_node(Node("2", "B", "Residential", 1.0, 0.0, population=2000))

    with pytest.raises(ValueError, match="missing edge"):
        graph.add_time_profile("1", "2", TimeProfile(3000.0, 800.0, 2800.0, 200.0))


def test_get_edge_returns_none_for_missing_edge():
    graph = build_test_graph()
    assert graph.get_edge("3", "2") is not None
    assert graph.get_edge("2", "999") is None


def test_unique_undirected_edges_returns_each_logical_edge_once():
    graph = build_test_graph()
    unique_edges = graph.unique_undirected_edges()

    assert len(unique_edges) == 3
    assert {(edge.from_id, edge.to_id) for edge in unique_edges} == {("1", "2"), ("1", "3"), ("2", "3")}


def test_assert_node_exists_raises_for_unknown_node():
    graph = build_test_graph()

    with pytest.raises(ValueError, match="Unknown node"):
        graph.assert_node_exists("missing")


def test_time_profile_rejects_invalid_time_slot():
    profile = TimeProfile(3000.0, 800.0, 2800.0, 200.0)

    with pytest.raises(ValueError, match="Invalid time slot"):
        profile.volume("dawn")


def test_time_profile_rejects_negative_values():
    with pytest.raises(ValueError, match="must be non-negative"):
        TimeProfile(-1.0, 1.0, 1.0, 1.0)


def test_edge_rejects_invalid_values():
    with pytest.raises(ValueError, match="Self-loop"):
        Edge("1", "1", 1.0, 100.0, 7.0)

    with pytest.raises(ValueError, match="distance_km"):
        Edge("1", "2", 0.0, 100.0, 7.0)

    with pytest.raises(ValueError, match="condition_score"):
        Edge("1", "2", 1.0, 100.0, 0.5)


def test_directed_graph_preserves_directionality():
    graph = Graph(directed=True)
    graph.add_node(Node("1", "A", "Residential", 0.0, 0.0, population=1000))
    graph.add_node(Node("2", "B", "Residential", 1.0, 0.0, population=2000))
    graph.add_edge(Edge("1", "2", 10.0, 1000.0, 7.0))
    graph.add_time_profile("1", "2", TimeProfile(3000.0, 800.0, 2800.0, 200.0))

    assert len(list(graph.neighbors("1"))) == 1
    assert len(list(graph.neighbors("2"))) == 0
    assert graph.get_edge("2", "1") is None
    assert graph.get_time_profile("2", "1") is None


def test_unique_undirected_edges_rejects_directed_graph():
    graph = Graph(directed=True)
    graph.add_node(Node("1", "A", "Residential", 0.0, 0.0, population=1000))
    graph.add_node(Node("2", "B", "Residential", 1.0, 0.0, population=2000))
    graph.add_edge(Edge("1", "2", 10.0, 1000.0, 7.0))

    with pytest.raises(ValueError, match="undirected graphs"):
        graph.unique_undirected_edges()

def test_get_node_returns_node_for_existing_id():
    graph = build_test_graph()
    node = graph.get_node("1")
    assert node is not None
    assert node.node_id == "1"
    assert node.name == "A"

def test_get_node_returns_none_for_missing_id():
    graph = build_test_graph()
    assert graph.get_node("999") is None
