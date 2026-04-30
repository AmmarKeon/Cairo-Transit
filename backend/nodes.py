"""GET /api/nodes"""
from backend.shared import NODES

def handler(request):
    return [NODES[n] for n in sorted(NODES.keys())]
