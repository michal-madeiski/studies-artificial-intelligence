from typing import Optional
from dataclasses import dataclass, field
import pandas as pd

@dataclass
class Edge:
    target_id: str
    route_name: str
    trip_id: Optional[str]
    departure_time: Optional[pd.Timedelta]
    arrival_time: Optional[pd.Timedelta]

@dataclass
class Node:
    stop_id: str
    name: str
    lat: float
    lon: float
    parent_station: str
    edges: list[Edge] = field(default_factory=list)
    
    def add_edge(self, edge: Edge) -> None:
        self.edges.append(edge)