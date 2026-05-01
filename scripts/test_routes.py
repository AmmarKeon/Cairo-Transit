import urllib.request
import json

for algo in ['bfs', 'dijkstra', 'astar', 'osrm']:
    url = f'http://localhost:8000/api/route/{algo}?start=F2&goal=F9'
    try:
        r = urllib.request.urlopen(url)
        data = json.loads(r.read().decode())
        print(algo + ': ' + str(data.get('success')))
    except Exception as e:
        print(algo + ': Error - ' + str(e))