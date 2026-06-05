"""
Przetwarzanie danych — imputacja, inżynieria cech, kodowanie zmiennych.

Moduł odpowiada za czyszczenie surowych danych i przygotowanie ich
do trenowania modelu regresji liniowej. Zawiera pipeline preprocessingu
oparty na scikit-learn.
"""

import os
import sys
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.config import (
    NUMERIC_FEATURES,
    CATEGORICAL_FEATURES,
    QUALITY_MAPPING,
    QUALITY_COLUMNS,
    TARGET_COLUMN,
)


def create_engineered_features(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Tworzy nowe cechy na podstawie istniejących kolumn.

    Inżynieria cech poprawia jakość modelu poprzez łączenie
    powiązanych zmiennych w bardziej informacyjne cechy.

    Args:
        dataframe: Ramka danych z surowymi cechami.

    Returns:
        pd.DataFrame: Ramka danych z dodanymi cechami inżynierowanymi.
    """
    df_copy = dataframe.copy()


    df_copy["TotalSF"] = (
        df_copy["1st Flr SF"].fillna(0)
        + df_copy["2nd Flr SF"].fillna(0)
        + df_copy["Total Bsmt SF"].fillna(0)
    )


    df_copy["TotalBathrooms"] = (
        df_copy["Full Bath"].fillna(0)
        + 0.5 * df_copy["Half Bath"].fillna(0)
        + df_copy["Bsmt Full Bath"].fillna(0)
        + 0.5 * df_copy["Bsmt Half Bath"].fillna(0)
    )


    df_copy["HouseAge"] = df_copy["Yr Sold"].fillna(2010) - df_copy["Year Built"].fillna(1970)


    df_copy["IsRemodeled"] = (
        df_copy["Year Remod/Add"] != df_copy["Year Built"]
    ).astype(int)

    return df_copy


def encode_quality_columns(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Koduje kolumny jakościowe na wartości numeryczne.

    Zamienia opisy słowne jakości (Ex, Gd, TA, Fa, Po)
    na wartości liczbowe od 1 do 5.

    Args:
        dataframe: Ramka danych z kolumnami jakościowymi.

    Returns:
        pd.DataFrame: Ramka danych z zakodowanymi kolumnami jakości.
    """
    df_copy = dataframe.copy()
    for column in QUALITY_COLUMNS:
        if column in df_copy.columns:
            df_copy[column] = df_copy[column].map(QUALITY_MAPPING).fillna(0)
    return df_copy


def get_feature_columns() -> tuple:
    """
    Zwraca listy cech numerycznych i kategorycznych do modelu.

    Uwzględnia cechy inżynierowane oraz zakodowane kolumny jakości.
    Kolumny jakości po kodowaniu stają się numeryczne.

    Returns:
        tuple: (lista cech numerycznych, lista cech kategorycznych)
    """
    engineered = ["TotalSF", "TotalBathrooms", "HouseAge", "IsRemodeled"]

    numeric = [f for f in NUMERIC_FEATURES if f not in QUALITY_COLUMNS]
    numeric += QUALITY_COLUMNS
    numeric += engineered

    categorical = [f for f in CATEGORICAL_FEATURES if f not in QUALITY_COLUMNS]

    return numeric, categorical


def build_preprocessing_pipeline(
    numeric_features: list,
    categorical_features: list
) -> ColumnTransformer:
    """
    Buduje pipeline preprocessingu danych.

    Pipeline składa się z dwóch gałęzi:
    - Numeryczna: imputacja medianą + standaryzacja
    - Kategoryczna: imputacja stałą + one-hot encoding

    Args:
        numeric_features: Lista nazw cech numerycznych.
        categorical_features: Lista nazw cech kategorycznych.

    Returns:
        ColumnTransformer: Skonfigurowany transformer preprocessingu.
    """

    numeric_pipeline = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])


    categorical_pipeline = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="constant", fill_value="Brak")),
        ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
    ])


    preprocessor = ColumnTransformer(
        transformers=[
            ("numeric", numeric_pipeline, numeric_features),
            ("categorical", categorical_pipeline, categorical_features),
        ],
        remainder="drop",
    )

    return preprocessor


def prepare_data(dataframe: pd.DataFrame) -> tuple:
    """
    Przygotowuje dane do trenowania modelu.

    Wykonuje pełny pipeline: inżynieria cech → kodowanie jakości
    → rozdzielenie na cechy i zmienną docelową.

    Args:
        dataframe: Surowa ramka danych z pliku CSV.

    Returns:
        tuple: (cechy X jako DataFrame, zmienna docelowa y jako Series)

    Raises:
        ValueError: Gdy brakuje kolumny docelowej w danych.
    """
    if TARGET_COLUMN not in dataframe.columns:
        raise ValueError(f"Brak kolumny docelowej '{TARGET_COLUMN}' w danych.")


    df_clean = dataframe.dropna(subset=[TARGET_COLUMN]).copy()


    df_clean = create_engineered_features(df_clean)


    df_clean = encode_quality_columns(df_clean)


    numeric_cols, categorical_cols = get_feature_columns()


    available_numeric = [col for col in numeric_cols if col in df_clean.columns]
    available_categorical = [col for col in categorical_cols if col in df_clean.columns]

    feature_columns = available_numeric + available_categorical
    features = df_clean[feature_columns]
    target = df_clean[TARGET_COLUMN]


    removed_rows = len(dataframe) - len(df_clean)
    if removed_rows > 0:
        print(f"Usunięto {removed_rows} wierszy z brakującą ceną.")
    print(f"Przygotowano dane: {features.shape[0]} wierszy, {features.shape[1]} cech")
    print(f"  Cechy numeryczne: {len(available_numeric)}")
    print(f"  Cechy kategoryczne: {len(available_categorical)}")

    return features, target


def prepare_single_input(input_data: dict, dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Przygotowuje pojedyncze dane wejściowe z formularza do predykcji.

    Tworzy ramkę danych z jednym wierszem, zawierającą wszystkie
    cechy wymagane przez model (w tym inżynierowane).

    Args:
        input_data: Słownik z danymi wpisanymi przez użytkownika.
        dataframe: Przykładowa ramka danych (dla uzupełnienia brakujących kolumn).

    Returns:
        pd.DataFrame: Ramka danych gotowa do predykcji.
    """

    single_row = pd.DataFrame([input_data])


    numeric_cols, categorical_cols = get_feature_columns()
    all_base_features = NUMERIC_FEATURES + CATEGORICAL_FEATURES

    for col in all_base_features:
        if col not in single_row.columns:
            if col in dataframe.columns:

                if dataframe[col].dtype in [np.float64, np.int64]:
                    single_row[col] = dataframe[col].median()
                else:
                    mode_values = dataframe[col].mode()
                    single_row[col] = mode_values.iloc[0] if len(mode_values) > 0 else "Brak"
            else:
                single_row[col] = 0


    for col in ["Yr Sold", "Year Built", "Year Remod/Add"]:
        if col not in single_row.columns:
            if col == "Yr Sold":
                single_row[col] = 2010
            else:
                single_row[col] = single_row.get("Year Built", 1990)


    single_row = create_engineered_features(single_row)


    single_row = encode_quality_columns(single_row)


    feature_columns = numeric_cols + categorical_cols
    available_columns = [col for col in feature_columns if col in single_row.columns]
    result = single_row[available_columns]

    return result


if __name__ == "__main__":

    from data.download import load_training_data

    raw_data = load_training_data()
    X, y = prepare_data(raw_data)
    print(f"\nCechy (X): {X.shape}")
    print(f"Cel (y): {y.shape}")
    print(f"Średnia cena: ${y.mean():,.0f}")
    print(f"Mediana ceny: ${y.median():,.0f}")
