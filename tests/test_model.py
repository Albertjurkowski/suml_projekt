"""
Testy jednostkowe — moduł modelu.

Testuje trenowanie modelu, zapisywanie/ładowanie,
oraz poprawność predykcji.
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import MODEL_PATH
from model.train import train_model
from model.predict import load_model, predict_price, predict_prices_batch
from data.download import load_training_data
from data.preprocess import prepare_data


class TestTrainModel:
    """Testy trenowania modelu."""

    def test_training_completes_successfully(self):
        """Sprawdza czy trenowanie kończy się bez błędów."""
        metrics = train_model()

        assert isinstance(metrics, dict)
        assert "rmse" in metrics
        assert "mae" in metrics
        assert "r2" in metrics

    def test_model_file_is_saved(self):
        """Sprawdza czy plik modelu został zapisany po trenowaniu."""
        train_model()
        assert os.path.exists(MODEL_PATH)

    def test_r2_score_is_positive(self):
        """Sprawdza czy R² jest dodatnie (model lepszy niż losowy)."""
        metrics = train_model()
        assert metrics["r2"] > 0, f"R² powinno być > 0, ale wynosi {metrics['r2']}"

    def test_rmse_is_reasonable(self):
        """Sprawdza czy RMSE jest w rozsądnym zakresie."""
        metrics = train_model()
        assert metrics["rmse"] < 100000, f"RMSE za wysokie: {metrics['rmse']}"


class TestLoadModel:
    """Testy ładowania modelu."""

    def test_model_loads_successfully(self):
        """Sprawdza czy model ładuje się poprawnie."""
        train_model()
        pipeline = load_model()
        assert pipeline is not None

    def test_raises_error_when_no_model(self):
        """Sprawdza czy rzuca błąd gdy brak pliku modelu."""
        from app import config
        original_path = config.MODEL_PATH
        config.MODEL_PATH = "/tmp/nonexistent_model.pkl"

        from model import predict as predict_module
        predict_module.MODEL_PATH = config.MODEL_PATH

        with pytest.raises(FileNotFoundError):
            load_model()

        config.MODEL_PATH = original_path
        predict_module.MODEL_PATH = original_path


class TestPrediction:
    """Testy predykcji."""

    def test_prediction_returns_positive_float(self):
        """Sprawdza czy predykcja zwraca dodatnią liczbę zmiennoprzecinkową."""
        train_model()

        raw_data = load_training_data()
        features, _ = prepare_data(raw_data)
        sample = features.head(1)

        price = predict_price(sample)

        assert isinstance(price, float)
        assert price > 0, f"Cena powinna być > 0, ale wynosi {price}"

    def test_batch_prediction_returns_list(self):
        """Sprawdza czy predykcja wsadowa zwraca listę cen."""
        train_model()

        raw_data = load_training_data()
        features, _ = prepare_data(raw_data)
        sample = features.head(5)

        prices = predict_prices_batch(sample)

        assert isinstance(prices, list)
        assert len(prices) == 5
        assert all(price > 0 for price in prices)

    def test_prediction_varies_with_input(self):
        """Sprawdza czy predykcje różnią się dla różnych danych."""
        train_model()

        raw_data = load_training_data()
        features, _ = prepare_data(raw_data)

        price_cheap = predict_price(features.head(1))
        price_expensive = predict_price(features.tail(1))

        assert price_cheap != price_expensive


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
