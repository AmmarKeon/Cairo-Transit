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