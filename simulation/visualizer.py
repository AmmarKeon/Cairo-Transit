import pandas as pd
import plotly.graph_objects as go
import os

def build_network_visualization(data_dir):
    """Reads project CSVs and builds an interactive Plotly graph."""

    neighborhoods = pd.read_csv(os.path.join(data_dir, 'neighborhoods.csv'))
    facilities = pd.read_csv(os.path.join(data_dir, 'facilities.csv'))
    roads = pd.read_csv(os.path.join(data_dir, 'existing_roads.csv'))

    node_coords = {}
    node_names = {}
    
    for _, row in neighborhoods.iterrows():
        n_id = str(row['ID']).strip() 
        node_coords[n_id] = (row['X-coordinate'], row['Y-coordinate'])
        node_names[n_id] = row['Name']
        
    for _, row in facilities.iterrows():
        f_id = str(row['ID']).strip()
        node_coords[f_id] = (row['X-coordinate'], row['Y-coordinate'])
        node_names[f_id] = row['Name']

    fig = go.Figure()

    edge_x = []
    edge_y = []
    
    for _, row in roads.iterrows():
        from_id = str(row['FromID']).strip()
        to_id = str(row['ToID']).strip()
        
        if from_id in node_coords and to_id in node_coords:
            x0, y0 = node_coords[from_id]
            x1, y1 = node_coords[to_id]
            
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

    fig.add_trace(go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1.5, color='#888'),
        hoverinfo='none',
        mode='lines',
        name='Roads'
    ))

    fig.add_trace(go.Scatter(
        x=neighborhoods['X-coordinate'], 
        y=neighborhoods['Y-coordinate'],
        mode='markers+text',
        text=neighborhoods['Name'],
        textposition="top center",
        hovertext=[f"{name}<br>Pop: {pop}" for name, pop in zip(neighborhoods['Name'], neighborhoods['Population'])],
        hoverinfo='text',
        marker=dict(
            showscale=True,
            colorscale='YlGnBu', 
            size=12,
            color=neighborhoods['Population'],
            colorbar=dict(title='Population')
        ),
        name='Neighborhoods'
    ))

    fig.add_trace(go.Scatter(
        x=facilities['X-coordinate'], 
        y=facilities['Y-coordinate'],
        mode='markers',
        hovertext=[f"{name}<br>Type: {ftype}" for name, ftype in zip(facilities['Name'], facilities['Type'])],
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
        margin=dict(b=20,l=5,r=5,t=40),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor='white'
    )

    fig.show()

if __name__ == "__main__":
    DATA_DIRECTORY = os.path.join(os.path.dirname(__file__), '..', 'data')
    
    build_network_visualization(DATA_DIRECTORY)