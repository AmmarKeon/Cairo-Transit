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
