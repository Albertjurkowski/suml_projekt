"""
Testy jednostkowe — moduł przetwarzania danych.

Testuje poprawność imputacji, inżynierii cech i kodowania
zmiennych jakościowych.
"""

import os
import sys
import pytest
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.preprocess import (
    create_engineered_features,
    encode_quality_columns,
    get_feature_columns,
    prepare_data,
    build_preprocessing_pipeline,
)


def create_sample_dataframe() -> pd.DataFrame:
    """Tworzy przykładową ramkę danych do testów."""
    return pd.DataFrame({
        "1st Flr SF": [1000, 1200, 800],
        "2nd Flr SF": [500, 0, 400],
        "Total Bsmt SF": [800, 1000, 600],
        "Full Bath": [2, 1, 2],
        "Half Bath": [1, 0, 1],
        "Bsmt Full Bath": [1, 0, 0],
        "Bsmt Half Bath": [0, 1, 0],
        "Year Built": [1990, 2005, 1975],
        "Year Remod/Add": [2000, 2005, 1995],
        "Yr Sold": [2010, 2010, 2010],
        "Exter Qual": ["Gd", "TA", "Ex"],
        "Kitchen Qual": ["TA", "Gd", "Ex"],
        "Bsmt Qual": ["Gd", "TA", None],
        "Heating QC": ["Ex", "Gd", "TA"],
        "Overall Qual": [7, 6, 8],
        "Gr Liv Area": [1500, 1200, 1200],
        "Garage Area": [400, 300, 500],
        "Garage Cars": [2, 1, 2],
        "Fireplaces": [1, 0, 2],
        "Lot Area": [8000, 10000, 7000],
        "Wood Deck SF": [100, 0, 200],
        "Open Porch SF": [50, 0, 100],
        "Mas Vnr Area": [0, 100, 200],
        "TotRms AbvGrd": [7, 6, 8],
        "Bedroom AbvGr": [3, 2, 4],
        "Neighborhood": ["NAmes", "OldTown", "NridgHt"],
        "Foundation": ["PConc", "CBlock", "PConc"],
        "Central Air": ["Y", "Y", "N"],
        "Garage Type": ["Attchd", "Detchd", "Attchd"],
        "Sale Condition": ["Normal", "Normal", "Abnorml"],
        "SalePrice": [200000, 150000, 250000],
    })


class TestCreateEngineeredFeatures:
    """Testy tworzenia cech inżynierowanych."""

    def test_total_sf_is_calculated(self):
        """Sprawdza czy TotalSF jest poprawnie obliczone."""
        df = create_sample_dataframe()
        result = create_engineered_features(df)

        expected_first_row = 1000 + 500 + 800
        assert result["TotalSF"].iloc[0] == expected_first_row

    def test_total_bathrooms_is_calculated(self):
        """Sprawdza czy TotalBathrooms jest poprawnie obliczone."""
        df = create_sample_dataframe()
        result = create_engineered_features(df)

        expected_first_row = 2 + 0.5 * 1 + 1 + 0.5 * 0
        assert result["TotalBathrooms"].iloc[0] == expected_first_row

    def test_house_age_is_calculated(self):
        """Sprawdza czy HouseAge jest poprawnie obliczony."""
        df = create_sample_dataframe()
        result = create_engineered_features(df)

        expected_first_row = 2010 - 1990
        assert result["HouseAge"].iloc[0] == expected_first_row

    def test_is_remodeled_flag(self):
        """Sprawdza czy flaga IsRemodeled jest poprawna."""
        df = create_sample_dataframe()
        result = create_engineered_features(df)

        assert result["IsRemodeled"].iloc[0] == 1
        assert result["IsRemodeled"].iloc[1] == 0

    def test_handles_missing_values(self):
        """Sprawdza obsługę brakujących wartości w inżynierii cech."""
        df = create_sample_dataframe()
        df.loc[0, "1st Flr SF"] = np.nan
        df.loc[0, "Total Bsmt SF"] = np.nan

        result = create_engineered_features(df)

        expected = 0 + 500 + 0
        assert result["TotalSF"].iloc[0] == expected


class TestEncodeQualityColumns:
    """Testy kodowania kolumn jakościowych."""

    def test_quality_values_are_encoded(self):
        """Sprawdza czy wartości jakości są zamienione na liczby."""
        df = create_sample_dataframe()
        result = encode_quality_columns(df)

        assert result["Exter Qual"].iloc[0] == 4
        assert result["Exter Qual"].iloc[1] == 3
        assert result["Exter Qual"].iloc[2] == 5

    def test_missing_quality_filled_with_zero(self):
        """Sprawdza czy brakujące wartości jakości → 0."""
        df = create_sample_dataframe()
        result = encode_quality_columns(df)

        assert result["Bsmt Qual"].iloc[2] == 0


class TestGetFeatureColumns:
    """Testy listy cech do modelu."""

    def test_returns_two_lists(self):
        """Sprawdza czy zwraca krotę z dwoma listami."""
        numeric, categorical = get_feature_columns()
        assert isinstance(numeric, list)
        assert isinstance(categorical, list)

    def test_numeric_contains_engineered(self):
        """Sprawdza czy cechy inżynierowane są w liście numerycznych."""
        numeric, _ = get_feature_columns()
        assert "TotalSF" in numeric
        assert "TotalBathrooms" in numeric
        assert "HouseAge" in numeric

    def test_no_overlap_between_lists(self):
        """Sprawdza brak duplikatów między listami numerycznymi i kategorycznymi."""
        numeric, categorical = get_feature_columns()
        overlap = set(numeric) & set(categorical)
        assert len(overlap) == 0, f"Duplikaty: {overlap}"


class TestPrepareData:
    """Testy pełnego pipeline'u przygotowania danych."""

    def test_returns_features_and_target(self):
        """Sprawdza czy zwraca cechy i zmienną docelową."""
        df = create_sample_dataframe()
        features, target = prepare_data(df)

        assert len(features) == 3
        assert len(target) == 3

    def test_target_column_not_in_features(self):
        """Sprawdza czy zmienna docelowa nie jest w cechach."""
        df = create_sample_dataframe()
        features, _ = prepare_data(df)

        assert "SalePrice" not in features.columns

    def test_raises_error_without_target(self):
        """Sprawdza czy rzuca błąd gdy brak kolumny docelowej."""
        df = create_sample_dataframe().drop(columns=["SalePrice"])

        with pytest.raises(ValueError, match="Brak kolumny docelowej"):
            prepare_data(df)


class TestBuildPreprocessingPipeline:
    """Testy pipeline'u preprocessingu."""

    def test_pipeline_fits_and_transforms(self):
        """Sprawdza czy pipeline poprawnie dopasowuje i transformuje dane."""
        df = create_sample_dataframe()
        df = create_engineered_features(df)
        df = encode_quality_columns(df)

        numeric_cols, categorical_cols = get_feature_columns()
        available_numeric = [c for c in numeric_cols if c in df.columns]
        available_categorical = [c for c in categorical_cols if c in df.columns]

        pipeline = build_preprocessing_pipeline(available_numeric, available_categorical)
        feature_cols = available_numeric + available_categorical
        result = pipeline.fit_transform(df[feature_cols])

        assert result.shape[0] == 3
        assert result.shape[1] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
