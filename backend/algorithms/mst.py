"""
Kruskal's Minimum Spanning Tree - Connects all nodes with minimum total weight.
Uses Union-Find (disjoint set) for cycle detection.
"""
from typing import Dict, List, Tuple


def find_mst(
    graph: Dict[str, List[Tuple[str, float]]],
    nodes: Dict[str, dict],
) -> dict:
    parent = {n: n for n in graph}
    rank = {n: 0 for n in graph}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y):
        px, py = find(x), find(y)
        if px == py:
            return False
        if rank[px] < rank[py]:
            px, py = py, px
        parent[py] = px
        if rank[px] == rank[py]:
            rank[px] += 1
        return True

    # Build unique edge list
    edges = []
    seen = set()
    for u, neighbors in graph.items():
        for v, w in neighbors:
            if (u, v) not in seen and (v, u) not in seen:
                edges.append((w, u, v))
                seen.add((u, v))

    edges.sort()

    mst_edges = []
    for w, a, b in edges:
        if union(a, b):
            mst_edges.append({
                "from": {"lat": nodes[a]["lat"], "lng": nodes[a]["lng"], "name": nodes[a]["name"]},
                "to": {"lat": nodes[b]["lat"], "lng": nodes[b]["lng"], "name": nodes[b]["name"]},
                "weight": w,
            })

    return {
        "success": True,
        "data": {
            "edges": mst_edges,
            "algorithm": "Kruskal",
            "node_count": len(graph),
        },
    }
