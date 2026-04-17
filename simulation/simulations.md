### `visualizer.py`

**Overview**
An interactive graphing script that visually verifies the CairoFlow transportation network. It reads the static CSV data (`neighborhoods.csv`, `facilities.csv`, `existing_roads.csv`) and renders a hoverable, 2D map using Plotly. 

**Features**
* Plots **Neighborhoods** scaled and colored by population density.
* Highlights critical **Facilities** (hospitals, airports) with distinct markers.
* Draws **Existing Roads** as edges connecting the spatial coordinates.

**How to run?**
```bash
python3 simulation/visualizer.py