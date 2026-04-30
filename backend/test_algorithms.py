"""
Test all algorithms against the enhanced Cairo graph.
Shows path differences between algorithms.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from algorithms import dijkstra, astar, bfs, dfs, greedy, bellmanford, bidirectional, randomwalk
from main import GRAPH, NODES, ROADS


def test_all():
    print(f"Graph: {len(GRAPH)} nodes, {len(ROADS)} edges")
    print(f"Nodes: {sorted(GRAPH.keys())}")
    print()

    # Test multiple pairs
    pairs = [
        ("1", "7"),    # Maadi -> 6th October
        ("1", "13"),   # Maadi -> New Administrative Capital
        ("5", "15"),   # Heliopolis -> Sheikh Zayed
        ("2", "12"),   # Nasr City -> Helwan
        ("4", "9"),    # New Cairo -> Mohandessin
        ("F1", "F2"),  # Airport -> Ramses Station
        ("3", "23"),   # Downtown -> Town of October
        ("11", "25"),  # Shubra -> Faisal
    ]

    for start, goal in pairs:
        if start not in NODES or goal not in NODES:
            continue

        print(f"\n{'='*80}")
        print(f"Route: {start} ({NODES[start]['name']}) -> {goal} ({NODES[goal]['name']})")
        print(f"{'='*80}")

        algos = [
            ("Dijkstra", dijkstra),
            ("A*", astar),
            ("BFS", bfs),
            ("DFS", dfs),
            ("Greedy", greedy),
            ("Bellman-Ford", bellmanford),
            ("Bidirectional", bidirectional),
            ("Random Walk", randomwalk),
        ]

        results = {}
        for name, fn in algos:
            result = fn(GRAPH, start, goal, NODES)
            if result["success"]:
                d = result["data"]
                path_names = [NODES[n]["name"] for n in d["nodes"]]
                print(f"  {name:20s} | {d['distance']:6.1f} km | {len(d['nodes'])-1:2d} hops | {' -> '.join(path_names)}")
                results[name] = d["distance"]
            else:
                print(f"  {name:20s} | FAILED: {result['error']}")
                results[name] = None

        # Show distance comparison
        opt = min(v for v in results.values() if v is not None) if results else 0
        if opt > 0:
            print(f"\n  {'Algorithm':20s} | {'Distance':>8s} | {'vs Optimal':>10s}")
            print(f"  {'-'*20} | {'-'*8} | {'-'*10}")
            for name, dist in results.items():
                if dist is not None:
                    pct = ((dist - opt) / opt * 100)
                    bar = "#" * min(int(pct / 5), 20) if pct > 0 else "(optimal)"
                    print(f"  {name:20s} | {dist:6.1f} km | +{pct:5.1f}% {bar}")


if __name__ == "__main__":
    test_all()
