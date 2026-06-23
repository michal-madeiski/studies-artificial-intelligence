from datasets import load_dataset
import pandas as pd

dataset = load_dataset("allegro/klej-polemo2-in", split="test")

df = dataset.to_pandas()

df_filtered = df[df["target"] != "__label__meta_amb"].copy()

print("--- TEST SET STATISTICS ---")

print(f"Number of samples before filtering: {len(df)}")
print(f"Number of samples after removing the ambiguous class: {len(df_filtered)}\n")

print("--- CLASS BALANCE ---")
print(df_filtered["target"].value_counts())
print("\n")

df_filtered["text_length_words"] = df_filtered["sentence"].apply(
    lambda x: len(str(x).split())
)

print("--- TEXT LENGTH IN WORDS ---")
print(df_filtered["text_length_words"].describe()[["mean", "min", "max", "50%"]])
