from main import kruskal_mst, astar_path

print('Testing A* from ramses to 57357:')
path = astar_path('ramses', '57357')
if path:
    print(f'Path: {[p["name"] for p in path]}')
else:
    print('No path found')

print('\nTesting MST:')
mst = kruskal_mst()
print(f'MST edges: {len(mst)}')
for edge in mst:
    print(f'  {edge["from"]["name"]} -> {edge["to"]["name"]}')