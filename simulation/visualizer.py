from pathlib import Path
import sys

import plotly.graph_objects as go

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from src.core.graph import CairoDataLoader
except ImportError:
    from core.graph import CairoDataLoader


def build_network_visualization(data_dir, include_potential_roads=False):
    """Load the core graph and build an interactive Plotly visualization."""

    loader = CairoDataLoader(data_dir)
    graph = loader.load_graph(include_potential_roads=include_potential_roads)

    fig = go.Figure()

    edge_x = []
    edge_y = []

    for edge in graph.unique_undirected_edges():
        from_node = graph.nodes[edge.from_id]
        to_node = graph.nodes[edge.to_id]
        edge_x.extend([from_node.x, to_node.x, None])
        edge_y.extend([from_node.y, to_node.y, None])

    fig.add_trace(go.Scatter(
        x=edge_x,
        y=edge_y,
        line=dict(width=1.5, color='#888'),
        hoverinfo='none',
        mode='lines',
        name='Roads'
    ))

    neighborhood_nodes = [node for node in graph.nodes.values() if not node.is_facility]
    facility_nodes = [node for node in graph.nodes.values() if node.is_facility]

    fig.add_trace(go.Scatter(
        x=[node.x for node in neighborhood_nodes],
        y=[node.y for node in neighborhood_nodes],
        mode='markers+text',
        text=[node.name for node in neighborhood_nodes],
        textposition='top center',
        hovertext=[f"{node.name}<br>Pop: {node.population}" for node in neighborhood_nodes],
        hoverinfo='text',
        marker=dict(
            showscale=True,
            colorscale='YlGnBu',
            size=12,
            color=[node.population for node in neighborhood_nodes],
            colorbar=dict(title='Population')
        ),
        name='Neighborhoods'
    ))

    fig.add_trace(go.Scatter(
        x=[node.x for node in facility_nodes],
        y=[node.y for node in facility_nodes],
        mode='markers',
        hovertext=[f"{node.name}<br>Type: {node.node_type}" for node in facility_nodes],
        hoverinfo='text',
        marker=dict(
            symbol='star',
            size=14,
            color='red',
            line=dict(width=1, color='darkred')
        ),
        name='Facilities'
    ))

    fig.update_layout(
        title='CairoFlow: Baseline Transportation Network Graph',
        showlegend=True,
        hovermode='closest',
        margin=dict(b=20, l=5, r=5, t=40),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor='white'
    )

    fig.show()

if __name__ == "__main__":
    DATA_DIRECTORY = PROJECT_ROOT / 'data'

    build_network_visualization(DATA_DIRECTORY)