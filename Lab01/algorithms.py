import sys
import math
import time
import heapq
import pandas as pd
from loguru import logger
from typing import Optional, Any

from objects import Graph, Edge, Node
from settings import (PLATFORM_PLATFORM_TRANSFER_TIME, PLATFROM_STATION_TRANSFER_TIME,
                    STATION_PLATFORM_TRANSFER_TIME, PLATFORM_PLATFORM_TRANSFER_STR,
                    PLATFORM_STATION_TRANSFER_STR, STATION_PLATFORM_TRANSFER_STR,
                    EARTH_RADIUS, TRAIN_SPEED, TRAIN_MAX_DISTANCE)


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
        if optimize_for == 't' or optimize_for == 'p':
            return self.__shortest_path_engine(start_stop_id, end_stop_id, start_time_str, max_wait_time, use_astar=True, optimize_for=optimize_for)
        else:
            logger.error(f"Invalid optimize_for value: '{optimize_for}'. Only 't' and 'p' are allowed.")
            raise ValueError()

    def __shortest_path_engine(
        self, 
        start_stop_id: str, 
        end_stop_id: str, 
        start_time_str: str,
        max_wait_time: Optional[pd.Timedelta] = None,
        use_astar: bool = False,
        optimize_for: str = 't'
    ) -> tuple[Optional[list[dict]], Optional[pd.Timedelta], float]:
        
        algo_name = "A*" if use_astar else "Dijkstra"
        opt_name = "(Time) " if optimize_for == 't' else "(Transfers) "
        opt_name = opt_name if use_astar else ""
        logger.info(f"{algo_name} {opt_name}| Searching connection: {start_stop_id} -> {end_stop_id} [{start_time_str}].")

        start_calc_time = time.perf_counter()

        if start_stop_id not in self.graph.nodes or end_stop_id not in self.graph.nodes:
            logger.error("Start or end stop does not exist in the graph.")
            return None, None, time.perf_counter() - start_calc_time
        
        start_time = pd.to_timedelta(start_time_str)
        target_node = self.graph.nodes[end_stop_id]
        
        priority_queue = []
        counter = 0
        start_transfers = 0

        start_key = self.__get_node_key(start_stop_id, None, optimize_for)
        h_score = self.__heuristic(self.graph.nodes[start_stop_id], target_node, optimize_for) if use_astar else 0
        
        heapq.heappush(priority_queue, self.__build_priority_tuple(optimize_for, start_time, start_transfers, h_score, counter, start_stop_id, None))
        
        distances: dict[Any, Any] = {start_key: start_time if optimize_for == 't' else 0}
        came_from: dict[Any, tuple[Any, Edge, pd.Timedelta, pd.Timedelta]] = {}
        
        while priority_queue:
            _, _, _, current_time, current_transfers, current_node_id, current_trip_id = heapq.heappop(priority_queue)
            
            current_key = self.__get_node_key(current_node_id, current_trip_id, optimize_for)
            
            if current_node_id == end_stop_id:
                calc_time = time.perf_counter() - start_calc_time
                total_travel_time = current_time - start_time
                best_cost = self.__format_print_trip_total_time(total_travel_time) if optimize_for == 't' else current_transfers
                info = "Time" if optimize_for == 't' else "Transfers"
                logger.success(f"{algo_name} {opt_name}| Path found! {info}: {best_cost}.")
                path = self.__reconstruct_path(came_from, current_key)
                return path, total_travel_time, calc_time
                
            current_cost = current_time if optimize_for == 't' else current_transfers
            if current_cost > distances.get(current_key, pd.Timedelta.max if optimize_for == 't' else float('inf')):
                continue
                
            current_node = self.graph.nodes[current_node_id]
            
            for edge in current_node.edges:
                if edge.route_name == STATION_PLATFORM_TRANSFER_STR and current_node_id != start_stop_id:
                    continue
                if edge.route_name == PLATFORM_STATION_TRANSFER_STR and edge.target_id != end_stop_id:
                    continue

                if edge.route_name in [PLATFORM_PLATFORM_TRANSFER_STR, PLATFORM_STATION_TRANSFER_STR, STATION_PLATFORM_TRANSFER_STR]:
                    if edge.route_name == PLATFORM_PLATFORM_TRANSFER_STR: transfer_time = PLATFORM_PLATFORM_TRANSFER_TIME
                    elif edge.route_name == PLATFORM_STATION_TRANSFER_STR: transfer_time = PLATFROM_STATION_TRANSFER_TIME
                    else: transfer_time = STATION_PLATFORM_TRANSFER_TIME
                    
                    next_time = current_time + transfer_time
                    dep_time = current_time
                    new_trip_id = current_trip_id
                    new_transfers = current_transfers
                    
                else:
                    if edge.departure_time < current_time:
                        continue
                    wait_time = edge.departure_time - current_time
                    if max_wait_time is not None and wait_time > max_wait_time:
                        continue
                        
                    next_time = edge.arrival_time
                    dep_time = edge.departure_time
                    new_trip_id = edge.trip_id
                    
                    if new_trip_id != current_trip_id and current_trip_id is not None:
                        new_transfers = current_transfers + 1
                    else:
                        new_transfers = current_transfers

                next_key = self.__get_node_key(edge.target_id, new_trip_id, optimize_for)
                cost_to_compare = next_time if optimize_for == 't' else new_transfers
                best_known_cost = distances.get(next_key, pd.Timedelta.max if optimize_for == 't' else float('inf'))
                
                if cost_to_compare < best_known_cost:
                    distances[next_key] = cost_to_compare
                    came_from[next_key] = (current_key, edge, next_time, dep_time)
                    
                    h = self.__heuristic(self.graph.nodes[edge.target_id], target_node, optimize_for) if use_astar else 0
                    
                    counter += 1
                    new_tuple = self.__build_priority_tuple(optimize_for, next_time, new_transfers, h, counter, edge.target_id, new_trip_id)
                    heapq.heappush(priority_queue, new_tuple)
                    
        logger.warning(f"{algo_name} {opt_name}| No connection found.")
        return None, None, time.perf_counter() - start_calc_time
    
    @staticmethod
    def __build_priority_tuple(
        optimize_for: str, 
        current_time: pd.Timedelta, 
        transfers: int, 
        h_score: Any, 
        counter: int, 
        node_id: str, 
        trip_id: Optional[str]
    ) -> tuple:
        if optimize_for == 't':
            priority_score = current_time + h_score if h_score else current_time
            secondary_score = transfers
        else:
            priority_score = transfers + h_score if h_score else transfers
            secondary_score = current_time
            
        return (priority_score, secondary_score, counter, current_time, transfers, node_id, trip_id)
    
    @staticmethod
    def __heuristic(node1: Node, node2: Node, optimize_for: str = 't') -> pd.Timedelta | int:
        lat1, lon1 = math.radians(node1.lat), math.radians(node1.lon)
        lat2, lon2 = math.radians(node2.lat), math.radians(node2.lon)
        dLat, dLon = lat2 - lat1, lon2 - lon1

        a = math.sin(dLat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dLon / 2)**2
        c = 2 * math.asin(math.sqrt(a))
        distance_km = EARTH_RADIUS * c
        
        if optimize_for == 't':
            hours = distance_km / TRAIN_SPEED
            return pd.Timedelta(hours=hours)
        else:
            transfers = math.floor(distance_km / TRAIN_MAX_DISTANCE)
            return transfers
    
    @staticmethod
    def __get_node_key(node_id: str, trip_id: Optional[str], optimize_for: str) -> Any:
        return (node_id, trip_id) if optimize_for == 'p' else node_id

    @staticmethod
    def __reconstruct_path(came_from: dict, final_key: Any) -> list[dict]:
        path = []
        current_step = final_key
        
        while current_step in came_from:
            prev_step, edge, arr_time, dep_time = came_from[current_step]
            
            source_id = prev_step[0] if isinstance(prev_step, tuple) else prev_step
            target_id = current_step[0] if isinstance(current_step, tuple) else current_step
            
            path.append({
                'source_id': source_id,
                'target_id': target_id,
                'route_name': edge.route_name,
                'departure': dep_time,
                'arrival': arr_time,
                'trip_id': edge.trip_id,
            })
            current_step = prev_step
            
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
        if pd.isna(node.parent_station) or not node.parent_station: return "Station"
        if pd.isna(node.platform) or str(node.platform).strip() == "": return "Platform TBA"  
        return f"Platform {node.platform}"
