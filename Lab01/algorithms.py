import time
import heapq
import sys
import math
import pandas as pd
from loguru import logger
from typing import Optional

from objects import Graph, Edge
from settings import (PLATFORM_PLATFORM_TRANSFER_TIME, PLATFROM_STATION_TRANSFER_TIME,
                    STATION_PLATFORM_TRANSFER_TIME, PLATFORM_PLATFORM_TRANSFER_STR,
                    PLATFORM_STATION_TRANSFER_STR, STATION_PLATFORM_TRANSFER_STR,
                    EARTH_RADIUS, TRAIN_SPEED)


class PathFinder:
    def __init__(self, graph: Graph) -> None:
        self.graph = graph

    def find_shortest_path_dijkstra(
        self,
        start_stop_id: str,
        end_stop_id: str,
        start_time_str: str,
        max_wait_time: Optional[pd.Timedelta] = None
    ) -> tuple[Optional[list[dict]], Optional[pd.Timedelta], float]:
        return self.__shortest_path_engine(start_stop_id, end_stop_id, start_time_str, max_wait_time, use_astar=False)

    def find_shortest_path_astar(
        self,
        start_stop_id: str,
        end_stop_id: str,
        start_time_str: str,
        max_wait_time: Optional[pd.Timedelta] = None,
        optimize_for: str = 't'
    ) -> tuple[Optional[list[dict]], Optional[pd.Timedelta], float]:
        if optimize_for == 't':
            return self.__shortest_path_engine(start_stop_id, end_stop_id, start_time_str, max_wait_time, use_astar=True)
        elif optimize_for == 'p':
            return self.__least_transfer_engine(start_stop_id, end_stop_id, start_time_str, max_wait_time)
        else:
            logger.error(f"Invalid optimize_for value: {optimize_for}. Only 't' and 'p' are allowed.")
            raise ValueError()

    def __shortest_path_engine(
        self, 
        start_stop_id: str, 
        end_stop_id: str, 
        start_time_str: str,
        max_wait_time: Optional[pd.Timedelta] = None,
        use_astar: bool = False
    ) -> tuple[Optional[list[dict]], Optional[pd.Timedelta], float]:
        
        algo_name = "A*" if use_astar else "Dijkstra"
        logger.info(f"{algo_name} | Searching for connection: {start_stop_id} -> {end_stop_id} [{start_time_str}].")

        start_calc_time = time.perf_counter()

        if start_stop_id not in self.graph.nodes or end_stop_id not in self.graph.nodes:
            logger.error("Start or end stop does not exist in the graph.")
            calc_time = time.perf_counter() - start_calc_time
            return None, None, calc_time
        
        start_time = pd.to_timedelta(start_time_str)
        target_node = self.graph.nodes[end_stop_id]
        
        priority_queue = []
        counter = 0

        start_h = self.__heuristic(self.graph.nodes[start_stop_id], target_node) if use_astar else pd.Timedelta(0)
        
        heapq.heappush(priority_queue, (start_time + start_h, counter, start_time, start_stop_id))
        
        distances: dict[str, pd.Timedelta] = {start_stop_id: start_time}
        came_from: dict[str, tuple[str, Edge]] = {}
        
        while priority_queue:
            _, _, current_time, current_node_id = heapq.heappop(priority_queue)
            
            if current_node_id == end_stop_id:
                calc_time = time.perf_counter() - start_calc_time
                total_travel_time = current_time - start_time
                
                logger.success(f"{algo_name} | Shortest path found.")
                path = self.__reconstruct_path(came_from, current_node_id, distances)
                
                return path, total_travel_time, calc_time
                
            if current_time > distances.get(current_node_id, pd.Timedelta('100 days')):
                continue
                
            current_node = self.graph.nodes[current_node_id]
            
            for edge in current_node.edges:
                if edge.route_name == STATION_PLATFORM_TRANSFER_STR:
                    if current_node_id != start_stop_id:
                        continue
                elif edge.route_name == PLATFORM_STATION_TRANSFER_STR:
                    if edge.target_id != end_stop_id:
                        continue

                if edge.route_name == PLATFORM_PLATFORM_TRANSFER_STR:
                    next_time = current_time + PLATFORM_PLATFORM_TRANSFER_TIME
                elif edge.route_name == PLATFORM_STATION_TRANSFER_STR:
                    next_time = current_time + PLATFROM_STATION_TRANSFER_TIME
                elif edge.route_name == STATION_PLATFORM_TRANSFER_STR:
                    next_time = current_time + STATION_PLATFORM_TRANSFER_TIME
                else:
                    if edge.departure_time < current_time:
                        continue
                    wait_time = edge.departure_time - current_time
                    if max_wait_time is not None and wait_time > max_wait_time:
                        continue
                    next_time = edge.arrival_time
                
                if next_time < distances.get(edge.target_id, pd.Timedelta('100 days')):
                    distances[edge.target_id] = next_time
                    came_from[edge.target_id] = (current_node_id, edge)

                    h_score = self.__heuristic(self.graph.nodes[edge.target_id], target_node) if use_astar else pd.Timedelta(0)
                    new_priority = next_time + h_score
                    
                    counter += 1
                    heapq.heappush(priority_queue, (new_priority, counter, next_time, edge.target_id))
                    
        calc_time = time.perf_counter() - start_calc_time
        logger.warning(f"{algo_name} | No connection found.")
        return None, None, calc_time
    
    def __least_transfer_engine(
            self, 
            start_stop_id: str, 
            end_stop_id: str, 
            start_time_str: str,
            max_wait_time: Optional[pd.Timedelta] = None
        ) -> tuple[Optional[list[dict]], Optional[pd.Timedelta], float]:
        pass
    
    @staticmethod
    def __heuristic(node1, node2) -> pd.Timedelta:
        lat1 = math.radians(node1.lat)
        lon1 = math.radians(node1.lon)
        lat2 = math.radians(node2.lat)
        lon2 = math.radians(node2.lon)

        dLat = lat2 - lat1
        dLon = lon2 - lon1

        a = math.sin(dLat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dLon / 2)**2

        rad = EARTH_RADIUS
        c = 2 * math.asin(math.sqrt(a))
        distance_km = rad * c
        
        hours = distance_km / TRAIN_SPEED
        
        return pd.Timedelta(hours=hours)

    def __reconstruct_path(
        self, 
        came_from: dict[str, tuple[str, Edge]], 
        current_node_id: str,
        distances: dict[str, pd.Timedelta]
    ) -> list[dict]:
        path = []
        while current_node_id in came_from:
            prev_node_id, edge = came_from[current_node_id]
            
            arrival_time = distances[current_node_id]

            if edge.route_name in [PLATFORM_PLATFORM_TRANSFER_STR, PLATFORM_STATION_TRANSFER_STR, STATION_PLATFORM_TRANSFER_STR]:
                departure_time = distances[prev_node_id]
            else:
                departure_time = edge.departure_time
                
            path.append({
                'source_id': prev_node_id,
                'target_id': current_node_id,
                'route_name': edge.route_name,
                'departure': departure_time,
                'arrival': arrival_time,
                'trip_id': edge.trip_id,
            })
            current_node_id = prev_node_id
            
        path.reverse()
        return path

    def print_trip(self, path: list[dict], total_time: pd.Timedelta, calc_time: float) -> None:
            info = "ROUTE DETAILS"
            decoration = "="*60
            decoration_center = "="*len(info)
            print(f"{decoration}{info}{decoration}")
            if not path:
                print("No route to display.", file=sys.stdout)
                return

            parts = []
            current_part = None

            for step in path:
                if current_part is None:
                    current_part = step.copy()
                else:
                    is_same_train = (step.get('trip_id') is not None and 
                                    step['trip_id'] == current_part.get('trip_id'))
                    if is_same_train:
                        current_part['target_id'] = step['target_id']
                        current_part['arrival'] = step['arrival']
                    else:
                        parts.append(current_part)
                        current_part = step.copy()
            if current_part: parts.append(current_part)

            for part in parts:
                src = self.graph.nodes[part['source_id']]
                tgt = self.graph.nodes[part['target_id']]
                
                src_plat = self.__format_platform(src)
                tgt_plat = self.__format_platform(tgt)
                
                dep_str = str(part['departure'])[-8:-3]
                arr_str = str(part['arrival'])[-8:-3]
                
                if part['route_name'] == PLATFORM_PLATFORM_TRANSFER_STR:
                    print(f"[MOVE] {src.name} ({src_plat}) [{dep_str}] -> {tgt.name} ({tgt_plat}) [{arr_str}] | Platform change")
                elif part['route_name'] == PLATFORM_STATION_TRANSFER_STR or part['route_name'] == STATION_PLATFORM_TRANSFER_STR:
                    start_or_end = f"End" if part['route_name'] == PLATFORM_STATION_TRANSFER_STR else f"Start"
                    print(f"[MOVE] {src.name} ({src_plat}) [{dep_str}] -> {tgt.name} ({tgt_plat}) [{arr_str}] | {start_or_end}")
                else:
                    print(f"[RIDE] {src.name} ({src_plat}) [{dep_str}] -> {tgt.name} ({tgt_plat}) [{arr_str}] | Line: {part['route_name']}")
            print(f"{decoration}{decoration_center}{decoration}")

            formatted_total_time = self.__format_print_trip_total_time(total_time)
            print(f"Total travel time: {formatted_total_time}", file=sys.stderr)
            print(f"Total calculation time: {calc_time:.3f}s", file=sys.stderr)

    @staticmethod
    def __format_print_trip_total_time(total_time: pd.Timedelta) -> str:
        str_total_time_split = str(total_time).split(' ')
        days = f"{str_total_time_split[0]}d " if str_total_time_split[0] != '0' else ''
        time_split = str_total_time_split[2].split(':')
        hours = time_split[0]
        minutes = time_split[1]
        return f"{days}{hours}h {minutes}m"
    
    @staticmethod
    def __format_platform(node) -> str:
        if pd.isna(node.parent_station) or not node.parent_station:
            return "Station"
        
        if pd.isna(node.platform) or str(node.platform).strip() == "":
            return "Platform TBA"
            
        return f"Platform {node.platform}"
