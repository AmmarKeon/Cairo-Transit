"""GET /api/network/mst"""
from api.shared import mst

def handler(request):
    return mst()
