"""
Konfiguracja aplikacji — ścieżki, stałe i ustawienia domyślne.

Centralne miejsce przechowywania wszystkich stałych konfiguracyjnych
używanych przez moduły data, model i app.
"""

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
MODEL_SAVED_DIR = os.path.join(BASE_DIR, "model", "saved")

TRAIN_DATA_PATH = os.path.join(DATA_RAW_DIR, "train.csv")
MODEL_PATH = os.path.join(MODEL_SAVED_DIR, "model.pkl")
PIPELINE_PATH = os.path.join(MODEL_SAVED_DIR, "pipeline.pkl")

NUMERIC_FEATURES = [
    "Overall Qual",
    "Gr Liv Area",
    "Total Bsmt SF",
    "1st Flr SF",
    "Garage Area",
    "Garage Cars",
    "Full Bath",
    "Year Built",
    "Year Remod/Add",
    "Fireplaces",
    "Lot Area",
    "Wood Deck SF",
    "Open Porch SF",
    "2nd Flr SF",
    "Half Bath",
    "Bsmt Full Bath",
    "Bsmt Half Bath",
    "TotRms AbvGrd",
    "Bedroom AbvGr",
    "Mas Vnr Area",
]

CATEGORICAL_FEATURES = [
    "Neighborhood",
    "Exter Qual",
    "Kitchen Qual",
    "Bsmt Qual",
    "Foundation",
    "Heating QC",
    "Central Air",
    "Garage Type",
    "Sale Condition",
]

ENGINEERED_FEATURES = [
    "TotalSF",
    "TotalBathrooms",
    "HouseAge",
    "IsRemodeled",
]

TARGET_COLUMN = "SalePrice"

QUALITY_MAPPING = {
    "Ex": 5,
    "Gd": 4,
    "TA": 3,
    "Fa": 2,
    "Po": 1,
}

QUALITY_COLUMNS = ["Exter Qual", "Kitchen Qual", "Bsmt Qual", "Heating QC"]

PAGE_TITLE = "Wycena Nieruchomości"
PAGE_ICON = "🏠"
PAGE_LAYOUT = "wide"

TEST_SIZE = 0.2
RANDOM_STATE = 42
