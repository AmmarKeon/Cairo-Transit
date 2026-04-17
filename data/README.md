# Cairo Transportation Dataset

## Overview
This directory contains the dataset for the CairoFlow transportation optimization system. This data represents a scaled model of the Greater Cairo metropolitan area, capturing geographic nodes, current and potential road infrastructure, temporal traffic patterns, and public transit logistics. 

The data is separated into eight distinct CSV files.
---

## File Dictionary & Schema

### 1. Geographic Data (Nodes)
These files represent the nodes of the Cairo transportation graph.

#### `neighborhoods.csv`
Represents the primary residential, commercial, and industrial zones. These act as the standard source and destination nodes for route planning.
* **ID**: Unique integer identifier for the neighborhood.
* **Name**: String name of the district ("Maadi", "Nasr City").
* **Population**: Integer representing the resident population.
* **Type**: Category of the zone (Residential, Mixed, Business, Industrial, Government).
* **X/Y-coordinate**: Geographic coordinates for spatial distance calculations and map visualization.

#### `facilities.csv`
Represents critical infrastructure points requiring specialized routing constraints.
* **ID**: Unique alphanumeric identifier ("F1", "F9").
* **Name**: String name of the facility.
* **Type**: Category (Airport, Transit Hub, Medical, Education). *Medical* facilities are critical targets for the A* emergency routing subsystem.
* **X/Y-coordinate**: Geographic coordinates.

---

### 2. Infrastructure Data (Edges)
These files represent the edges between nodes, complete with weights and constraints.

#### `existing_roads.csv`
The current baseline road network.
* **FromID / ToID**: Origin and destination node IDs.
* **Distance(km)**: Edge weight used for standard spatial shortest path calculations.
* **Current Capacity(vehicles/hour)**: Maximum throughput before severe congestion occurs.
* **Condition(1-10)**: Structural health metric. Used by DP algorithms to allocate road maintenance resources to areas with poor conditions.

#### `potential_roads.csv`
Proposed infrastructure expansions.
* **FromID / ToID**: Origin and destination node IDs.
* **Distance(km)**: Physical length of the proposed road.
* **Estimated Capacity(vehicles/hour)**: Projected throughput.
* **Construction Cost(Million EGP)**: Financial weight of the edge.

---

### 3. Temporal & Dynamic Data (Weights)
Used to transition the graph from a static structure to a dynamic, real world simulation.

#### `traffic_flow.csv`
Historical traffic density across different times of the day.
* **RoadID**: The edge identifier (formatted as "FromID-ToID").
* **Morning Peak / Afternoon / Evening Peak / Night (veh/h)**: Time varying edge weights.
---

### 4. Transit Logistics
Data utilized specifically for the Public Transit Optimization subsystem.

#### `metro_lines.csv`
Current rail infrastructure.
* **LineID**: Unique identifier for the metro line.
* **Name**: Common name/endpoints of the line.
* **Stations**: Comma separated list of Node IDs serviced by this line.
* **Daily Passengers**: Number of passengers per day.

#### `bus_routes.csv`
Current fleet operations.
* **RouteID**: Unique identifier for the bus route.
* **Stops**: Comma separated list of Node IDs serviced.
* **Buses Assigned**: Current resource allocation.
* **Daily Passengers**: Ridership metric.

#### `public_transit_demand.csv`
Public transit demand. 
* **FromID / ToID**: Requested route origins and destinations.
* **Daily Passengers**: Volume of demand.