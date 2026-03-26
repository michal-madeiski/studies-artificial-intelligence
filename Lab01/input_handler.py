import argparse
from datetime import datetime


def valid_date(s):
    try:
        return datetime.strptime(s.strip(), "%Y-%m-%d")
    except ValueError:
        msg = f"Invalid date format: '{s}'. Expected format: YYYY-MM-DD"
        raise argparse.ArgumentTypeError(msg)


def valid_time(s):
    try:
        t = datetime.strptime(s, "%H:%M")
        return t.strftime("%H:%M:%S")
    except ValueError:
        msg = f"Invalid time format: '{s}'. Expected format: HH:MM"
        raise argparse.ArgumentTypeError(msg)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="GTFS connection finder",
        epilog="Example usage: python main.py 1413213 1413210 2026-03-16 12:00 -o t -w 5",
    )

    parser.add_argument("start_stop_id", help="ID of start stop")
    parser.add_argument("end_stop_id", help="ID of end stop")
    parser.add_argument("date", type=valid_date, help="Start date (YYYY-MM-DD)")
    parser.add_argument("time", type=valid_time, help="Start time (HH:MM)")

    parser.add_argument(
        "-o",
        "--optimize",
        choices=["t", "p"],
        default="t",
        help="Optimization choice: 't' = time (default), 'p' = transfers",
    )

    parser.add_argument(
        "-w",
        "--wait",
        type=int,
        default=None,
        metavar="MINUTES",
        help="Maximum minutes of wait for transfer (optional)",
    )

    return parser.parse_args()
