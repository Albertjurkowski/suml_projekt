"""
Predykcja — ładowanie modelu i generowanie prognoz cen.

Moduł zapewnia interfejs do ładowania zapisanego modelu
i wykonywania predykcji cen nieruchomości.
"""

import os
import sys
import joblib
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.config import MODEL_PATH


def load_model():
    """
    Ładuje zapisany pipeline modelu z pliku.

    Returns:
        Pipeline: Wytrenowany pipeline (preprocessing + model).

    Raises:
        FileNotFoundError: Gdy plik modelu nie istnieje.
    """
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"Nie znaleziono pliku modelu: {MODEL_PATH}\n"
            "Uruchom najpierw trenowanie: python -m model.train"
        )
    pipeline = joblib.load(MODEL_PATH)
    return pipeline


def predict_price(features: pd.DataFrame) -> float:
    """
    Generuje predykcję ceny nieruchomości.

    Args:
        features: Ramka danych z jednym wierszem cech nieruchomości.

    Returns:
        float: Przewidywana cena nieruchomości (w USD).
    """
    pipeline = load_model()
    prediction = pipeline.predict(features)


    predicted_price = max(float(prediction[0]), 0)

    return predicted_price


def predict_prices_batch(features: pd.DataFrame) -> list:
    """
    Generuje predykcje cen dla wielu nieruchomości naraz.

    Args:
        features: Ramka danych z wieloma wierszami cech.

    Returns:
        list: Lista przewidywanych cen.
    """
    pipeline = load_model()
    predictions = pipeline.predict(features)


    return [max(float(price), 0) for price in predictions]


if __name__ == "__main__":

    from data.download import load_training_data
    from data.preprocess import prepare_data

    raw_data = load_training_data()
    X, y = prepare_data(raw_data)


    sample = X.head(5)
    predicted_prices = predict_prices_batch(sample)
    actual_prices = y.head(5).tolist()

    print("\nPorównanie predykcji z rzeczywistością:")
    print(f"{'Predykcja':>15} | {'Rzeczywista':>15} | {'Różnica':>15}")
    print("-" * 50)
    for predicted, actual in zip(predicted_prices, actual_prices):
        diff = predicted - actual
        print(f"${predicted:>13,.0f} | ${actual:>13,.0f} | ${diff:>13,.0f}")
