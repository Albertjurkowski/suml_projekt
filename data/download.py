"""
Pobieranie danych — ładowanie zestawu danych o cenach nieruchomości.

Moduł zapewnia funkcje do ładowania danych treningowych z pliku CSV.
Dane pochodzą z zestawu Kaggle 'House Prices: Advanced Regression Techniques'.
"""

import os
import sys
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.config import TRAIN_DATA_PATH, DATA_RAW_DIR


def load_training_data() -> pd.DataFrame:
    """
    Ładuje dane treningowe z pliku CSV.

    Returns:
        pd.DataFrame: Ramka danych z danymi treningowymi.

    Raises:
        FileNotFoundError: Gdy plik z danymi nie istnieje.
    """
    if not os.path.exists(TRAIN_DATA_PATH):
        raise FileNotFoundError(
            f"Nie znaleziono pliku z danymi: {TRAIN_DATA_PATH}\n"
            f"Upewnij się, że plik train.csv znajduje się w katalogu {DATA_RAW_DIR}"
        )

    dataframe = pd.read_csv(TRAIN_DATA_PATH)
    print(f"Załadowano dane: {dataframe.shape[0]} wierszy, {dataframe.shape[1]} kolumn")
    return dataframe


def get_data_summary(dataframe: pd.DataFrame) -> dict:
    """
    Generuje podsumowanie statystyczne zestawu danych.

    Args:
        dataframe: Ramka danych do podsumowania.

    Returns:
        dict: Słownik z kluczowymi statystykami danych.
    """
    summary = {
        "liczba_wierszy": dataframe.shape[0],
        "liczba_kolumn": dataframe.shape[1],
        "brakujace_wartosci": dataframe.isnull().sum().sum(),
        "procent_brakow": round(
            dataframe.isnull().sum().sum() / (dataframe.shape[0] * dataframe.shape[1]) * 100,
            2
        ),
        "typy_danych": dataframe.dtypes.value_counts().to_dict(),
    }
    return summary


if __name__ == "__main__":
    df = load_training_data()
    data_summary = get_data_summary(df)
    for key, value in data_summary.items():
        print(f"  {key}: {value}")
