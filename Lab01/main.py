from datetime import datetime
import pandas as pd

from settings import DATA_DIR
from algorithms import PathFinder
from objects import Graph
from gtfs_loader import GTFSLoader


def main():
    #test_configs
    travel_date = datetime(2026, 3, 16)
    start_stop_id = '1413213'
    end_stop_id = '1413398'
    start_time_str = '12:00:00'
    #test_configs

    loader = GTFSLoader(data_dir=DATA_DIR)
    loader.load_data()

    stops_df, active_stop_times_df = loader.filter_data_for_date(travel_date)

    graph = Graph()
    graph.build_graph(stops_df, active_stop_times_df)
    
    finder = PathFinder(graph)
    path1, total_time1, calc_time1 = finder.find_shortest_path_dijkstra(
        start_stop_id=start_stop_id,
        end_stop_id=end_stop_id,
        start_time_str=start_time_str,
        #max_wait_time=pd.Timedelta(minutes=3)
    )
    
    finder.print_trip(path1, total_time1, calc_time1)

    path2, total_time2, calc_time2 = finder.find_shortest_path_astar(
        start_stop_id=start_stop_id,
        end_stop_id=end_stop_id,
        start_time_str=start_time_str,
        #max_wait_time=pd.Timedelta(minutes=3),
        optimize_for='t'
    )
    
    finder.print_trip(path2, total_time2, calc_time2)


if __name__ == "__main__":
    main()
