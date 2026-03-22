import pandas as pd

from objects import Graph
from settings import DATA_DIR
from algorithms import PathFinder
from gtfs_loader import GTFSLoader
from input_handler import parse_arguments


def main():
    args = parse_arguments()

    travel_date = args.date
    start_time_str = args.time
    max_wait_time = pd.Timedelta(minutes=args.wait) if args.wait is not None else None

    loader = GTFSLoader(data_dir=DATA_DIR)
    loader.load_data()

    stops_df, active_stop_times_df = loader.filter_data_for_date(travel_date)

    graph = Graph()
    graph.build_graph(stops_df, active_stop_times_df)
    
    finder = PathFinder(graph)
    path, total_time, calc_time = finder.find_shortest_path_astar(
        start_stop_id=args.start_stop_id,
        end_stop_id=args.end_stop_id,
        start_time_str=start_time_str,
        optimize_for=args.optimize,
        max_wait_time=max_wait_time,
    )
    finder.print_trip(path, total_time, calc_time)


if __name__ == "__main__":
    main()
