import pandas as pd
from loguru import logger
from typing import Optional
from dataclasses import dataclass, field

from settings import PLATFORM_PLATFORM_TRANSFER_STR, PLATFORM_STATION_TRANSFER_STR, STATION_PLATFORM_TRANSFER_STR


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
    platform: str
    edges: list[Edge] = field(default_factory=list)
    
    def add_edge(self, edge: Edge) -> None:
        self.edges.append(edge)

class Graph:
    def __init__(self) -> None:
        self.nodes: dict[str, Node] = {}

    def build_graph(self, stops_df: pd.DataFrame, stop_times_df: pd.DataFrame) -> None:
        logger.debug("Building graph...")

        self.__build_nodes(stops_df)
        self.__build_trip_edges(stop_times_df)
        self.__build_transfer_edges(stops_df)
        
        edge_count = sum(len(node.edges) for node in self.nodes.values())
        logger.success(f"Graph built successfully: {len(self.nodes)} nodes, {edge_count} edges.")

    def __build_nodes(self, stops_df: pd.DataFrame) -> None:
        logger.debug("Building nodes...")

        for row in stops_df.itertuples():

            node = Node(
                stop_id=str(row.stop_id),
                name=str(row.stop_name),
                lat=float(row.stop_lat),
                lon=float(row.stop_lon),
                parent_station=str(row.parent_station) if pd.notna(row.parent_station) else "",
                platform=str(row.platform_code) if pd.notna(row.platform_code) else ""
            )
            self.nodes[row.stop_id] = node

    def __build_trip_edges(self, stop_times_df: pd.DataFrame) -> None:
        logger.debug("Building trip edges...")
        
        for trip_id, group in stop_times_df.groupby('trip_id'):
            stops = group.to_dict('records')

            for i in range(len(stops) - 1):
                current_stop = stops[i]
                next_stop = stops[i + 1]

                edge = Edge(
                    target_id=str(next_stop['stop_id']),
                    route_name=str(current_stop.get('route_short_name', 'unknown')),
                    trip_id=str(trip_id),
                    departure_time=current_stop['departure_time_td'],
                    arrival_time=next_stop['arrival_time_td']
                )

                if str(current_stop['stop_id']) in self.nodes:
                    self.nodes[str(current_stop['stop_id'])].add_edge(edge)

    def __build_transfer_edges(self, stops_df: pd.DataFrame) -> None:
        logger.debug("Building transfer edges...")
        
        platforms = stops_df.dropna(subset="parent_station")

        for parent_id, group in platforms.groupby('parent_station'):
            platform_ids = group['stop_id'].tolist()
            parent_str = str(parent_id)

            for platform_from in platform_ids:
                for platform_to in platform_ids:
                    if platform_from != platform_to and platform_from in self.nodes:
                        transfer_edge = Edge(
                            target_id=str(platform_to),
                            route_name=PLATFORM_PLATFORM_TRANSFER_STR,
                            trip_id=None,
                            departure_time=None,
                            arrival_time=None
                        )
                        self.nodes[str(platform_from)].add_edge(transfer_edge)

            if parent_str in self.nodes:
                for plat_id in platform_ids:
                    if str(plat_id) in self.nodes:
                        enter_edge = Edge(
                            target_id=str(plat_id),
                            route_name=STATION_PLATFORM_TRANSFER_STR,
                            trip_id=None,
                            departure_time=None,
                            arrival_time=None
                        )
                        self.nodes[parent_str].add_edge(enter_edge)
                        
                        exit_edge = Edge(
                            target_id=parent_str,
                            route_name=PLATFORM_STATION_TRANSFER_STR,
                            trip_id=None,
                            departure_time=None,
                            arrival_time=None
                        )
                        self.nodes[str(plat_id)].add_edge(exit_edge)
