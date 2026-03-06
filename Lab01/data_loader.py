import pandas as pd
import os

data_dir_path = "path"

data = {}

def load_data(data_dir_path):
    print("Loading started...")

    for filename in os.listdir(data_dir_path):
        if filename.endswith(".txt"):
            dict_key = filename.replace(".txt", "")
            file_path = os.path.join(data_dir_path, filename)
            dict_value = pd.read_csv(file_path, dtype=str)
            data[dict_key] = dict_value

            print(f"Loaded: {filename}")
    pass

