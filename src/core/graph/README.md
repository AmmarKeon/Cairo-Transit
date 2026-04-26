# CairoFlow Graph Core

## Package Files

- `graph_models.py`: domain entities (`Node`, `Edge`, `TimeProfile`).
- `graph_structure.py`: adjacency-list storage and graph mutations.
- `graph.py`: public graph facade (`Graph`) that exposes only structure-level APIs.
- `data_loader.py`: dataset-to-graph adapter (CSV -> graph).
- `utils.py`: neutral utility helpers used by the graph layer.

## `graph_models.py`

### Node

| Attribute | Type | Used By | Description |
|-----------|------|---------|-------------|
| `node_id` | `str` | — | Unique node identifier for neighborhoods and facilities |
| `name` | `str` | — | Display name |
| `node_type` | `str` | MST, A* | `"residential"`, `"hospital"`, `"government"`, `"fire_station"`, etc. |
| `x` | `float` | A* | X-coordinate for Euclidean distance / heuristic |
| `y` | `float` | A* | Y-coordinate for Euclidean distance / heuristic |
| `population` | `int` | MST | Priority weight for high-population connections |
| `metadata` | `dict` | — | Extension point. Check keys before use |

**Properties**

| Property | Returns | Used By | Description |
|----------|---------|---------|-------------|
| `coordinates` | `tuple[float, float]` | A* | `(x, y)` for spatial calculations |
| `is_facility` | `bool` | MST, A* | `True` if `node_id` starts with `F`. Use for facility constraints and target filtering |

---

### Edge

| Attribute | Type | Used By | Description |
|-----------|------|---------|-------------|
| `from_id` | `str` | — | Source node ID |
| `to_id` | `str` | — | Destination node ID |
| `distance_km` | `float` | Shortest Path, A* | Base weight for route cost calculations |
| `capacity_veh_per_hour` | `float` | Greedy Traffic, Shortest Path | Infrastructure limit. Greedy: denominator for congestion ratio. Shortest Path: use with traffic volume for effective travel time |
| `condition_score` | `float` | DP Maintenance | Road condition score on the dataset's `1-10` scale. Lower = worse condition, higher maintenance priority |
| `construction_cost_million_egp` | `float \| None` | MST | Cost to build new road. `None` = cannot build |
| `existing_road` | `bool` | MST | `False` = potential new construction. Only include in MST if `construction_cost_million_egp` is not `None` |
| `metadata` | `dict` | Shortest Path, A* | Holds optional fields such as `avg_speed_kmh` or `lanes` |

---

### TimeProfile

`TimeProfile` stores traffic volume values loaded from `traffic_flow.csv` in `veh/h` for each time window. Treat these as traffic volumes, not abstract multipliers.

| Attribute | Type | Used By | Description |
|-----------|------|---------|-------------|
| `morning_peak` | `float` | Shortest Path, A*, Greedy Traffic | Morning traffic volume in `veh/h` |
| `afternoon` | `float` | Shortest Path, A*, Greedy Traffic | Afternoon traffic volume in `veh/h` |
| `evening_peak` | `float` | Shortest Path, A*, Greedy Traffic | Evening traffic volume in `veh/h` |
| `night` | `float` | Shortest Path, A*, Greedy Traffic | Night traffic volume in `veh/h` |

**Methods**

| Method | Returns | Used By | Description |
|--------|---------|---------|-------------|
| `volume(time_slot: str)` | `float` | Shortest Path, A*, Greedy Traffic | Pass `"morning"`, `"afternoon"`, `"evening"`, or `"night"`. Case-insensitive. Returns the stored traffic volume for that slot. Raises `ValueError` on invalid slot |

### Model Invariants

- `Node.node_id`, `Node.name`, and `Node.node_type` must be non-empty strings
- `Node.population` must be non-negative
- `Edge` self-loops are not allowed
- `Edge.distance_km` must be greater than `0`
- `Edge.capacity_veh_per_hour` must be non-negative
- `Edge.condition_score` must stay on the dataset `1-10` scale
- `existing_road=True` edges should not define `construction_cost_million_egp`
- `TimeProfile` values must be non-negative traffic volumes

## `graph_structure.py`

Adjacency-list graph with undirected default. Stores nodes, edges, time profiles, and road state.

| Attribute | Type | Description |
|-----------|------|-------------|
| `directed` | `bool` | Default `False`. If `True`, edges are one-way only. |
| `nodes` | `dict[str, Node]` | All nodes by `node_id`. |
| `adjacency` | `dict[str, list[Edge]]` | `node_id` -> outgoing edges. Undirected graphs store both directions. |
| `time_profiles` | `dict[str, TimeProfile]` | Edge traffic profiles. Key format handled by `canonical_edge_key()`. |

### Graph Invariants

- Duplicate node IDs are rejected
- Duplicate edges are rejected
- In undirected graphs, adding `A -> B` already represents the logical edge `A <-> B`
- `add_time_profile()` requires a real edge to exist first
- `unique_undirected_edges()` is only valid for undirected graphs
- Missing lookups such as `neighbors()` or `get_edge()` return empty results / `None`
- Invalid mutations raise `ValueError`

### Functions

- `__init__(directed: bool = False)`
- `add_node(node: Node)`
- `add_edge(edge: Edge)`
- `add_time_profile(from_id, to_id, profile)`
- `get_time_profile(from_id, to_id) -> TimeProfile | None`
- `close_road(from_id, to_id)`
- `open_road(from_id, to_id)`
- `neighbors(node_id) -> Iterable[Edge]`
- `assert_node_exists(node_id)`
- `get_edge(from_id, to_id) -> Edge | None`
- `unique_undirected_edges() -> list[Edge]`
- get_node(self, node_id: str) -> Optional[Node]

### `__init__(directed: bool = False)`

| Param | Default | Description |
|-------|---------|-------------|
| `directed` | `False` | Set `True` for one-way roads. Most Cairo roads are undirected. |

**Errors**: None.

### `add_node(node: Node)`

Adds node to graph. Initializes empty adjacency list.

| Param | Description |
|-------|-------------|
| `node` | `Node` instance. `node_id` must be unique. |

**Errors**: Raises `ValueError` if the node ID already exists or if the `Node` itself fails model validation.

### `add_edge(edge: Edge)`

Adds edge. **Both endpoints must exist first** or raises `ValueError`.

| Param | Description |
|-------|-------------|
| `edge` | `Edge` instance. |

**Undirected behavior**: Automatically creates reverse edge with swapped `from_id`/`to_id`. Copies all attributes including `metadata`.

**Errors**: Raises `ValueError` if either endpoint is missing, if the edge already exists, or if the `Edge` itself fails model validation.

### `add_time_profile(from_id, to_id, profile)`

Attaches `TimeProfile` to an edge.

| Param | Description |
|-------|-------------|
| `from_id` | Source node ID. |
| `to_id` | Destination node ID. |
| `profile` | `TimeProfile` instance. |

Key format handled internally by `canonical_edge_key()`. Overwrites existing profile.

**Errors**: Raises `ValueError` if the edge does not exist first or if the `TimeProfile` itself fails model validation.

### `get_time_profile(from_id, to_id) -> TimeProfile | None`

Returns traffic profile for edge. `None` if not set.

| Param | Description |
|-------|-------------|
| `from_id` | Source node ID. |
| `to_id` | Destination node ID. |

**Errors**: None. Returns `None` when the edge has no attached profile.

### `close_road(from_id, to_id)` / `open_road(from_id, to_id)`

Toggles road availability by setting `edge.metadata["closed"] = True/False`.

| Param | Description |
|-------|-------------|
| `from_id` | Source node ID. |
| `to_id` | Destination node ID. |

**Undirected**: Updates both directions. Raises `ValueError` if edge does not exist.

**Used by**: Future shortest-path consumers for road-closure scenarios.

**Errors**: Raises `ValueError` if the road does not exist.

### `neighbors(node_id) -> Iterable[Edge]`

Returns outgoing edges from node. Empty if node has no edges or does not exist.

| Param | Description |
|-------|-------------|
| `node_id` | Node ID to query. |

**Used by**: Dijkstra, A*, and all traversal algorithms.

**Errors**: None. Returns an empty iterable when the node has no outgoing edges or is unknown.

### `assert_node_exists(node_id)`

Raises `ValueError` if node not in graph. Use for input validation.

| Param | Description |
|-------|-------------|
| `node_id` | Node ID to check. |

**Errors**: Raises `ValueError` if the node does not exist.

### `get_edge(from_id, to_id) -> Edge | None`

Returns single edge matching direction. `None` if not found.

| Param | Description |
|-------|-------------|
| `from_id` | Source node ID. |
| `to_id` | Destination node ID. |

**Note**: For undirected graphs, `get_edge(u, v)` and `get_edge(v, u)` both return the same logical edge but from different adjacency lists.

**Errors**: None. Returns `None` if no matching edge is found.

### `unique_undirected_edges() -> list[Edge]`

Returns each undirected edge once. Filters out reverse duplicates.

**Used by**: MST consumers. Kruskal/Prim only need one copy per edge.

| Returns | Description |
|---------|-------------|
| `list[Edge]` | Unique edges. Keyed by `canonical_edge_key()` with `directed=False`. |

**Errors**: Raises `ValueError` if called on a directed graph.

## Internal

### `_set_road_state(from_id, to_id, closed)`

Sets `metadata["closed"]` on edge and reverse edge. Called by `close_road()` / `open_road()`. Raises `ValueError` if edge missing.
 
 
## How To Run

### Demo modules

These modules include a small `__main__` demo and should print output when run:

```bash
PYTHONPATH=src .venv/bin/python src/core/graph/graph.py
PYTHONPATH=src .venv/bin/python src/core/graph/data_loader.py
```

### Library modules

These modules are library-only. Running them is technically fine, but no output is expected:

```bash
PYTHONPATH=src .venv/bin/python src/core/graph/graph_models.py
PYTHONPATH=src .venv/bin/python src/core/graph/graph_structure.py
PYTHONPATH=src .venv/bin/python src/core/graph/utils.py
```

### Tests

```bash
.venv/bin/pytest -v tests/test_graph_core.py
.venv/bin/pytest -v tests/test_data_loader.py
.venv/bin/pytest -v tests/
.venv/bin/pytest -v -s tests/
.venv/bin/pytest -v --tb=long --showlocals tests/
```
