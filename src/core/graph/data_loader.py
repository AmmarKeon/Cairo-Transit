"""Data loader that builds the core graph from project CSV files."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, List

try:
	from .graph import Edge, Graph, Node, TimeProfile
except ImportError:  
	from core.graph.graph import Edge, Graph, Node, TimeProfile


class CairoDataLoader:
	"""Load datasets and convert them into a graph object."""

	def __init__(self, data_dir: str | Path) -> None:
		self.data_dir = Path(data_dir)
		if not self.data_dir.exists():
			raise FileNotFoundError(f"Data directory not found: {self.data_dir}")

	def load_graph(self, include_potential_roads: bool = False, directed: bool = False) -> Graph:
		graph = Graph(directed=directed)

		for row in self._read_csv("neighborhoods.csv"):
			graph.add_node(
				Node(
					node_id=str(row["ID"]).strip(),
					name=row["Name"].strip(),
					node_type=row["Type"].strip(),
					x=float(row["X-coordinate"]),
					y=float(row["Y-coordinate"]),
					population=int(row["Population"]),
				)
			)

		for row in self._read_csv("facilities.csv"):
			graph.add_node(
				Node(
					node_id=str(row["ID"]).strip(),
					name=row["Name"].strip(),
					node_type=row["Type"].strip(),
					x=float(row["X-coordinate"]),
					y=float(row["Y-coordinate"]),
					population=0,
				)
			)

		for row in self._read_csv("existing_roads.csv"):
			graph.add_edge(
				Edge(
					from_id=str(row["FromID"]).strip(),
					to_id=str(row["ToID"]).strip(),
					distance_km=float(row["Distance(km)"]),
					capacity_veh_per_hour=float(row["Current Capacity(vehicles/hour)"]),
					condition_score=float(row["Condition(1-10)"]),
					existing_road=True,
				)
			)

		if include_potential_roads:
			for row in self._read_csv("potential_roads.csv"):
				graph.add_edge(
					Edge(
						from_id=str(row["FromID"]).strip(),
						to_id=str(row["ToID"]).strip(),
						distance_km=float(row["Distance(km)"]),
						capacity_veh_per_hour=float(row["Estimated Capacity(vehicles/hour)"]),
						condition_score=7.5,
						construction_cost_million_egp=float(row["Construction Cost(Million EGP)"]),
						existing_road=False,
					)
				)

		for row in self._read_csv("traffic_flow.csv"):
			from_id, to_id = [part.strip() for part in row["RoadID"].split("-", maxsplit=1)]
			graph.add_time_profile(
				from_id,
				to_id,
				TimeProfile(
					morning_peak=float(row["Morning Peak(veh/h)"]),
					afternoon=float(row["Afternoon(veh/h)"]),
					evening_peak=float(row["Evening Peak(veh/h)"]),
					night=float(row["Night(veh/h)"]),
				),
			)

		return graph

	def load_rows(self, file_name: str) -> List[Dict[str, str]]:
		"""Expose generic CSV read for higher-level modules."""
		return self._read_csv(file_name)

	def _read_csv(self, file_name: str) -> List[Dict[str, str]]:
		file_path = self.data_dir / file_name
		if not file_path.exists():
			raise FileNotFoundError(f"Expected data file is missing: {file_path}")

		with file_path.open("r", encoding="utf-8") as handle:
			reader = csv.DictReader(handle)
			return list(reader)


if __name__ == "__main__":
	default_data_dir = Path(__file__).resolve().parents[3] / "data"
	loader = CairoDataLoader(default_data_dir)
	graph = loader.load_graph(include_potential_roads=True)
	print("=== CairoFlow Data Loader Demo ===")
	print(f"Nodes loaded: {len(graph.nodes)}")
	print(f"Directed: {graph.directed}")
	edge_count = sum(len(v) for v in graph.adjacency.values())
	print(f"Stored adjacency edges: {edge_count}")
	print(f"Time profiles loaded: {len(graph.time_profiles)}")
