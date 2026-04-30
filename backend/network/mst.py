"""GET /api/network/mst"""
from backend.shared import mst

def handler(request):
    return mst()
