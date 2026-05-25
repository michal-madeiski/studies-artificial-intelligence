import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.decomposition import PCA


def prepare_data(file_path: str):
    df = pd.read_csv(file_path)

    X = df.drop(columns=["Status", "ID", "N_Days"])
    y = df["Status"]

    le = LabelEncoder()
    y_encoded = le.fit_transform(y)

    X_train, X_val, y_train, y_val = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
    )
    print(
        f"Data split: {X_train.shape[0]} training samples, {X_val.shape[0]} validation samples"
    )

    num_cols = X_train.select_dtypes(include=["float64", "int64"]).columns
    cat_cols = X_train.select_dtypes(include=["object"]).columns

    num_imputer = SimpleImputer(strategy="median")
    X_train_num = pd.DataFrame(
        num_imputer.fit_transform(X_train[num_cols]), columns=num_cols
    )
    X_val_num = pd.DataFrame(num_imputer.transform(X_val[num_cols]), columns=num_cols)

    cat_imputer = SimpleImputer(strategy="most_frequent")
    X_train_cat = pd.DataFrame(
        cat_imputer.fit_transform(X_train[cat_cols]), columns=cat_cols
    )
    X_val_cat = pd.DataFrame(cat_imputer.transform(X_val[cat_cols]), columns=cat_cols)

    X_train_cat_encoded = pd.get_dummies(X_train_cat, drop_first=True)
    X_val_cat_encoded = pd.get_dummies(X_val_cat, drop_first=True)

    X_train_cat_encoded, X_val_cat_encoded = X_train_cat_encoded.align(
        X_val_cat_encoded, join="left", axis=1, fill_value=0
    )

    X_train_base = pd.concat([X_train_num, X_train_cat_encoded], axis=1)
    X_val_base = pd.concat([X_val_num, X_val_cat_encoded], axis=1)

    scaler = StandardScaler()
    X_train_num_scaled = pd.DataFrame(
        scaler.fit_transform(X_train_num), columns=num_cols
    )
    X_val_num_scaled = pd.DataFrame(scaler.transform(X_val_num), columns=num_cols)

    X_train_standardized = pd.concat([X_train_num_scaled, X_train_cat_encoded], axis=1)
    X_val_standardized = pd.concat([X_val_num_scaled, X_val_cat_encoded], axis=1)

    pca = PCA(n_components=0.95, random_state=42)
    X_train_pca = pd.DataFrame(pca.fit_transform(X_train_standardized))
    X_val_pca = pd.DataFrame(pca.transform(X_val_standardized))

    return {
        "y_train": y_train,
        "y_val": y_val,
        "base": (X_train_base, X_val_base),
        "standardized": (X_train_standardized, X_val_standardized),
        "pca": (X_train_pca, X_val_pca),
    }


if __name__ == "__main__":
    datasets = prepare_data("data/cirrhosis.csv")
