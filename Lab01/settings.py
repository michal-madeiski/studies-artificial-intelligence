import pandas as pd


DATA_DIR = "data"

PLATFORM_PLATFORM_TRANSFER_STR = 'platform_platform_transfer'
PLATFORM_STATION_TRANSFER_STR = 'platform_station_transfer'
STATION_PLATFORM_TRANSFER_STR = 'station_platform_transfer'

PLATFORM_PLATFORM_TRANSFER_TIME = pd.Timedelta(pd.Timedelta(minutes=2))
PLATFROM_STATION_TRANSFER_TIME = STATION_PLATFORM_TRANSFER_TIME = pd.Timedelta(pd.Timedelta(minutes=1))

EARTH_RADIUS = 6371.0
TRAIN_SPEED = 150
TRAIN_MAX_DISTANCE = 200
