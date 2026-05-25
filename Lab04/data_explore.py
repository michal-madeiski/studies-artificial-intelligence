import pandas as pd


def explore_cirrhosis_data(file_path: str) -> None:
    print("========== LOADING DATA ==========")
    try:
        df = pd.read_csv(file_path)
        print(f"Data successfully loaded from: {file_path}")
        print(f"Rows: {df.shape[0]}")
        print(f"Columns: {df.shape[1]}\n")
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return

    print("========== DATASET INFO ==========")
    df.info()
    print("\n")

    print("========== DATASET DESCRIBE ==========")
    print(df.describe())
    print("\n")

    print("========== DISTRIBUTION ==========")
    if "Status" in df.columns:
        print("Distribution for the target: 'Status':")
        print(df["Status"].value_counts(dropna=False))

    categorical_cols = ["Drug", "Sex", "Edema", "Ascites", "Hepatomegaly", "Spiders"]
    for col in categorical_cols:
        if col in df.columns:
            print(f"\nDistribution for '{col}':")
            print(df[col].value_counts(dropna=False))
    print("\n")

    print("========== MISSING VALUES ==========")
    missing_data = df.isna().sum()
    missing_data = missing_data[missing_data > 0]

    if not missing_data.empty:
        print("Columns with missing values:")
        print(missing_data.sort_values(ascending=False))

        print("\nPercentage of missing values:")
        missing_percentage = (missing_data / len(df)) * 100
        print(missing_percentage.round(2).astype(str) + " %")
    else:
        print("No missing values found")


if __name__ == "__main__":
    explore_cirrhosis_data("data/cirrhosis.csv")
