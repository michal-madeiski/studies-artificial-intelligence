from datetime import datetime

from settings import DATA_DIR
from gtfs_loader import GTFSLoader


def main():
    loader = GTFSLoader(data_dir=DATA_DIR)

    loader.load_data()

    travel_date = datetime(2026, 3, 15) 

    stops_df, active_stop_times_df = loader.filter_data_for_date(travel_date)

    print(f"Stops: {len(stops_df)}")
    print(f"Departures: {len(active_stop_times_df)}")

if __name__ == "__main__":
    main()