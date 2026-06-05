"""
Trenowanie modelu — regresja liniowa do predykcji cen nieruchomości.

Moduł odpowiada za trenowanie modelu na przetworzonych danych,
ewaluację jego jakości oraz zapisywanie artefaktów modelu.
"""

import os
import sys
import joblib
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.pipeline import Pipeline

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.config import MODEL_PATH, MODEL_SAVED_DIR, TEST_SIZE, RANDOM_STATE
from data.download import load_training_data
from data.preprocess import prepare_data, build_preprocessing_pipeline, get_feature_columns


def train_model() -> dict:
    """
    Trenuje model regresji liniowej na danych o cenach nieruchomości.

    Proces trenowania:
    1. Ładowanie i przetwarzanie danych
    2. Podział na zbiór treningowy i testowy (80/20)
    3. Budowanie pipeline'u preprocessingu
    4. Trenowanie modelu regresji liniowej
    5. Ewaluacja na zbiorze testowym
    6. Zapisanie modelu i pipeline'u

    Returns:
        dict: Metryki ewaluacji modelu (RMSE, MAE, R²).
    """

    print("=" * 60)
    print("TRENOWANIE MODELU REGRESJI LINIOWEJ")
    print("=" * 60)

    raw_data = load_training_data()
    features, target = prepare_data(raw_data)


    x_train, x_test, y_train, y_test = train_test_split(
        features, target, test_size=TEST_SIZE, random_state=RANDOM_STATE
    )
    print("\nPodział danych:")
    print(f"  Zbiór treningowy: {x_train.shape[0]} próbek")
    print(f"  Zbiór testowy: {x_test.shape[0]} próbek")


    numeric_cols, categorical_cols = get_feature_columns()
    available_numeric = [col for col in numeric_cols if col in features.columns]
    available_categorical = [col for col in categorical_cols if col in features.columns]

    preprocessor = build_preprocessing_pipeline(available_numeric, available_categorical)


    full_pipeline = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("regressor", LinearRegression()),
    ])


    print("\nTrenowanie modelu...")
    full_pipeline.fit(x_train, y_train)
    print("Model wytrenowany pomyślnie!")


    metrics = evaluate_model(full_pipeline, x_test, y_test)


    save_model(full_pipeline)

    return metrics


def evaluate_model(pipeline: Pipeline, x_test, y_test) -> dict:
    """
    Ewaluuje model na zbiorze testowym.

    Oblicza metryki jakości predykcji: RMSE, MAE oraz R².

    Args:
        pipeline: Wytrenowany pipeline (preprocessing + model).
        x_test: Cechy zbioru testowego.
        y_test: Prawdziwe ceny zbioru testowego.

    Returns:
        dict: Słownik z metrykami ewaluacji.
    """
    predictions = pipeline.predict(x_test)

    rmse = np.sqrt(mean_squared_error(y_test, predictions))
    mae = mean_absolute_error(y_test, predictions)
    r2 = r2_score(y_test, predictions)

    metrics = {
        "rmse": round(rmse, 2),
        "mae": round(mae, 2),
        "r2": round(r2, 4),
    }

    print("\n" + "=" * 40)
    print("METRYKI EWALUACJI MODELU")
    print("=" * 40)
    print(f"  RMSE:  ${rmse:>12,.2f}")
    print(f"  MAE:   ${mae:>12,.2f}")
    print(f"  R²:    {r2:>12.4f}")
    print("=" * 40)

    return metrics


def save_model(pipeline: Pipeline) -> None:
    """
    Zapisuje wytrenowany pipeline modelu do pliku.

    Args:
        pipeline: Wytrenowany pipeline do zapisania.
    """
    os.makedirs(MODEL_SAVED_DIR, exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)
    print(f"\nModel zapisany do: {MODEL_PATH}")


def get_feature_importance(pipeline: Pipeline, _feature_names: list = None) -> dict:
    """
    Oblicza ważność cech na podstawie współczynników regresji liniowej.

    Args:
        pipeline: Wytrenowany pipeline z modelem regresji.
        feature_names: Lista nazw cech wejściowych.

    Returns:
        dict: Słownik {nazwa_cechy: ważność} posortowany malejąco.
    """
    regressor = pipeline.named_steps["regressor"]
    preprocessor = pipeline.named_steps["preprocessor"]


    transformed_names = preprocessor.get_feature_names_out()
    coefficients = regressor.coef_


    feature_importance = {}
    for name, coef in zip(transformed_names, coefficients):
        clean_name = name.replace("numeric__", "").replace("categorical__", "")
        feature_importance[clean_name] = abs(coef)


    sorted_importance = dict(
        sorted(feature_importance.items(), key=lambda item: item[1], reverse=True)
    )

    return sorted_importance


if __name__ == "__main__":

    training_metrics = train_model()
    print(f"\nWynik trenowania: {training_metrics}")
