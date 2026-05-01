"""Quick algorithm test - run from project root with: python scripts/test_algo.py"""
import sys
import os

# Add backend to path so we can import main
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from main import dijkstra_route, astar_route, bfs_route

tests = [('F2', 'F9'), ('F2', '3'), ('1', 'F1')]

for start, goal in tests:
    print(f'=== {start} -> {goal} ===')
    
    r = bfs_route(start, goal)
    print(f'BFS: {r.get("success")}')
    
    r = dijkstra_route(start, goal)
    print(f'Dijkstra: {r.get("success")}, dist: {r.get("data", {}).get("distance", 0):.1f}km')
    
    r = astar_route(start, goal)
    print(f'A*: {r.get("success")}')
