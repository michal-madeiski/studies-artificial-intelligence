import pandas as pd
from loguru import logger
from datetime import datetime


class GTFSLoader:
    def __init__(self, data_dir: str) -> None:
        self.data_dir = data_dir
        self.routes = None
        self.stops = None
        self.trips = None
        self.stop_times = None
        self.calendar = None
        self.calendar_dates = None

    def load_data(self) -> None:
        logger.info(f"Loading data from directory: {self.data_dir}")

        try:
            logger.info("Loading routes, stops, trips, calendar, calendar_dates...")
            self.routes = pd.read_csv(
                f"{self.data_dir}/routes.txt", dtype={"route_id": str, "agency_id": str}
            )
            self.stops = pd.read_csv(
                f"{self.data_dir}/stops.txt",
                dtype={"stop_id": str, "parent_station": str},
            )
            self.trips = pd.read_csv(
                f"{self.data_dir}/trips.txt",
                dtype={"route_id": str, "service_id": str, "trip_id": str},
            )
            self.calendar = pd.read_csv(
                f"{self.data_dir}/calendar.txt", dtype={"service_id": str}
            )
            self.calendar_dates = pd.read_csv(
                f"{self.data_dir}/calendar_dates.txt", dtype={"service_id": str}
            )

        except FileNotFoundError as e:
            logger.error(f"File not found: {e.filename}.")
            raise
        except pd.errors.EmptyDataError:
            logger.error("One of GTFS files is empty.")
            raise
        except Exception as e:
            logger.exception(f"Other error: {e}")
            raise

        try:
            logger.info("Loading stop_times...")
            self.stop_times = pd.read_csv(
                f"{self.data_dir}/stop_times.txt",
                dtype={"trip_id": str, "stop_id": str},
            )

            logger.debug("Parsing time_columns in stop_times...")
            self.stop_times["arrival_time_td"] = pd.to_timedelta(
                self.stop_times["arrival_time"]
            )
            self.stop_times["departure_time_td"] = pd.to_timedelta(
                self.stop_times["departure_time"]
            )

        except Exception as e:
            logger.exception(f"Error while parsing time columns in stop_times: {e}")
            raise

        logger.success("Data loaded and parsed successfully.")

    def get_active_services_for_date(self, target_date: datetime) -> set[str]:
        date_int = int(target_date.strftime("%Y%m%d"))
        day_name = target_date.strftime("%A").lower()
        logger.debug(
            f"Searching services for date: {target_date.strftime('%Y-%m-%d')} ({day_name})..."
        )

        try:
            base_services_conditions = (
                (self.calendar["start_date"] <= date_int)
                & (self.calendar["end_date"] >= date_int)
                & (self.calendar[day_name] == 1)
            )
            base_services = set(
                self.calendar.loc[base_services_conditions, "service_id"]
            )

            exceptions_today = self.calendar_dates[
                self.calendar_dates["date"] == date_int
            ]
            added_services = set(
                exceptions_today[exceptions_today["exception_type"] == 1]["service_id"]
            )
            removed_services = set(
                exceptions_today[exceptions_today["exception_type"] == 2]["service_id"]
            )

            active_services = (base_services | added_services) - removed_services
            logger.info(f"Searched {len(active_services)} active services.")
            return active_services

        except KeyError as e:
            logger.error(f"No column in data: {e}")
            raise
        except Exception as e:
            logger.exception(f"Error while searching active services: {e}")
            raise

    def filter_data_for_date(
        self, target_date: datetime
    ) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
        logger.info("Starting filtering data for provided date...")

        try:
            active_services = self.get_active_services_for_date(target_date)

            active_trips = self.trips[self.trips["service_id"].isin(active_services)]
            active_stop_times = self.stop_times[
                self.stop_times["trip_id"].isin(active_trips["trip_id"])
            ]

            active_trips_with_routes = active_trips.merge(
                self.routes[["route_id", "route_short_name", "route_long_name"]],
                on="route_id",
                how="left",
            )

            final_stop_times = active_stop_times.merge(
                active_trips_with_routes[["trip_id", "route_short_name"]],
                on="trip_id",
                how="left",
            )

            final_stop_times = final_stop_times.sort_values(
                by=["trip_id", "stop_sequence"]
            )

            stop_routes_df = final_stop_times.merge(
                self.trips[["trip_id", "route_id"]], on="trip_id", how="left"
            )
            stop_to_routes = (
                stop_routes_df.groupby("stop_id")["route_id"].apply(set).to_dict()
            )

            logger.success(
                f"Filtering ended. Searched {len(final_stop_times)} stop times."
            )
            return self.stops, final_stop_times, stop_to_routes

        except Exception as e:
            logger.exception("Error while merging and filtering data frames.")
            raise
