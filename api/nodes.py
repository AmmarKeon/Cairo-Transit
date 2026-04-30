"""GET /api/nodes"""
from api.shared import NODES

def handler(request):
    return [NODES[n] for n in sorted(NODES.keys())]
