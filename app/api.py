"""
API REST — endpoint FastAPI do predykcji cen nieruchomości.

Udostępnia interfejs HTTP do wykonywania wycen nieruchomości.
Uruchomienie: uvicorn app.api:app --reload --port 8000
"""

import os
import sys
import uvicorn
import webbrowser
import threading
import numpy as np
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from fastapi.responses import FileResponse
from starlette.staticfiles import StaticFiles

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import MODEL_PATH
from data.download import load_training_data
from data.preprocess import prepare_single_input, prepare_data
from model.predict import predict_price
from model.train import train_model, get_feature_importance


@asynccontextmanager
async def app_lifespan(_app: FastAPI):
    """Zarządza cyklem życia aplikacji FastAPI."""
    # pylint: disable=protected-access
    _ensure_model_exists()
    yield


app = FastAPI(
    title="Wycena Nieruchomości API",
    description="API do predykcji cen domów jednorodzinnych (regresja liniowa)",
    version="1.0.0",
    lifespan=app_lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class HouseFeatures(BaseModel):
    """Schemat danych wejściowych — cechy nieruchomości."""

    gr_liv_area: int = Field(1500, ge=300, le=5000, description="Powierzchnia mieszkalna (sq ft)")
    total_bsmt_sf: int = Field(800, ge=0, le=3000, description="Powierzchnia piwnicy (sq ft)")
    first_flr_sf: int = Field(1000, ge=300, le=4000, description="Powierzchnia parteru (sq ft)")
    second_flr_sf: int = Field(0, ge=0, le=2500, description="Powierzchnia piętra (sq ft)")
    lot_area: int = Field(8000, ge=1000, le=50000, description="Powierzchnia działki (sq ft)")
    garage_cars: int = Field(2, ge=0, le=4, description="Pojemność garażu (samochody)")
    garage_area: int = Field(400, ge=0, le=1500, description="Powierzchnia garażu (sq ft)")
    overall_qual: int = Field(6, ge=1, le=10, description="Ogólna jakość (1-10)")
    year_built: int = Field(1990, ge=1870, le=2025, description="Rok budowy")
    year_remod: int = Field(2000, ge=1870, le=2025, description="Rok remontu")
    full_bath: int = Field(2, ge=0, le=4, description="Łazienki pełne")
    half_bath: int = Field(0, ge=0, le=2, description="Łazienki połówkowe")
    bedrooms: int = Field(3, ge=0, le=6, description="Sypialnie")
    total_rooms: int = Field(7, ge=2, le=15, description="Łączna liczba pokoi")
    fireplaces: int = Field(1, ge=0, le=3, description="Kominki")
    kitchen_qual: str = Field("TA", description="Jakość kuchni (Ex/Gd/TA/Fa/Po)")
    exter_qual: str = Field("TA", description="Jakość materiałów zewnętrznych (Ex/Gd/TA/Fa/Po)")


class PredictionResponse(BaseModel):
    """Schemat odpowiedzi — wynik predykcji."""

    predicted_price_usd: float = Field(description="Przewidywana cena w USD")
    predicted_price_pln: float = Field(description="Przewidywana cena w PLN (kurs ~4.0)")
    price_range_low: float = Field(description="Dolna granica zakresu (−15%)")
    price_range_high: float = Field(description="Górna granica zakresu (+15%)")
    percentile: float = Field(description="Percentyl ceny w zbiorze danych")


class HealthResponse(BaseModel):
    """Schemat odpowiedzi — status zdrowia serwisu."""

    status: str
    model_loaded: bool


def _ensure_model_exists():
    """Trenuje model, jeśli plik nie istnieje."""
    if not os.path.exists(MODEL_PATH):
        train_model()


def _features_to_dict(features: HouseFeatures) -> dict:
    """Konwertuje schemat Pydantic na słownik cech dla modelu."""
    return {
        "Gr Liv Area": features.gr_liv_area,
        "Total Bsmt SF": features.total_bsmt_sf,
        "1st Flr SF": features.first_flr_sf,
        "2nd Flr SF": features.second_flr_sf,
        "Lot Area": features.lot_area,
        "Garage Cars": features.garage_cars,
        "Garage Area": features.garage_area,
        "Overall Qual": features.overall_qual,
        "Year Built": features.year_built,
        "Year Remod/Add": features.year_remod,
        "Full Bath": features.full_bath,
        "Half Bath": features.half_bath,
        "Bedroom AbvGr": features.bedrooms,
        "TotRms AbvGrd": features.total_rooms,
        "Fireplaces": features.fireplaces,
        "Kitchen Qual": features.kitchen_qual,
        "Exter Qual": features.exter_qual,
        "Bsmt Full Bath": 0,
        "Bsmt Half Bath": 0,
        "Wood Deck SF": 0,
        "Open Porch SF": 0,
        "Mas Vnr Area": 0,
        "Yr Sold": 2010,
    }



@app.get("/health", response_model=HealthResponse, tags=["Status"])
async def health_check():
    """Sprawdza status serwisu i dostępność modelu."""
    return HealthResponse(
        status="ok",
        model_loaded=os.path.exists(MODEL_PATH),
    )


@app.post("/predict", response_model=PredictionResponse, tags=["Predykcja"])
async def predict(features: HouseFeatures):
    """
    Generuje predykcję ceny nieruchomości.

    Przyjmuje cechy budynku i zwraca przewidywaną cenę
    wraz z zakresem szacunkowym (±15%).
    """
    try:
        input_dict = _features_to_dict(features)
        raw_data = load_training_data()
        prepared = prepare_single_input(input_dict, raw_data)
        price = predict_price(prepared)

        prices = raw_data["SalePrice"].dropna().values
        percentile = float(np.sum(prices <= price) / len(prices) * 100)

        margin = price * 0.15
        return PredictionResponse(
            predicted_price_usd=round(price, 2),
            predicted_price_pln=round(price * 4.0, 2),
            price_range_low=round(price - margin, 2),
            price_range_high=round(price + margin, 2),
            percentile=round(percentile, 1),
        )
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error

@app.post("/api/similar-houses", tags=["Predykcja"])
async def similar_houses(features: HouseFeatures):
    """Znajduje podobne domy z danych treningowych."""
    raw_data = load_training_data()

    area = features.gr_liv_area
    qual = features.overall_qual
    year = features.year_built

    filtered = raw_data[
        (raw_data["Gr Liv Area"].between(area * 0.7, area * 1.3))
        & (raw_data["Overall Qual"].between(qual - 1, qual + 1))
    ].copy()

    if len(filtered) < 3:
        filtered = raw_data[
            (raw_data["Gr Liv Area"].between(area * 0.5, area * 1.5))
        ].copy()

    filtered["distance"] = (
        abs(filtered["Gr Liv Area"] - area) / area
        + abs(filtered["Overall Qual"] - qual) / 10
        + abs(filtered["Year Built"] - year) / 100
    )
    closest = filtered.nsmallest(5, "distance")

    results = []
    for _, row in closest.iterrows():
        results.append({
            "price": int(row["SalePrice"]),
            "area": int(row["Gr Liv Area"]),
            "quality": int(row["Overall Qual"]),
            "year_built": int(row["Year Built"]),
            "neighborhood": str(row.get("Neighborhood", "N/A")),
        })

    return {"similar_houses": results}


@app.get("/api/data-stats", tags=["Dane"])
async def data_stats():
    """Zwraca statystyki zbioru danych treningowych."""
    raw_data = load_training_data()
    prices = raw_data["SalePrice"].dropna()

    hist_values, bin_edges = np.histogram(prices, bins=50)

    return {
        "count": int(len(raw_data)),
        "features_count": int(raw_data.shape[1]),
        "mean_price": float(round(prices.mean(), 0)),
        "median_price": float(round(prices.median(), 0)),
        "min_price": float(round(prices.min(), 0)),
        "max_price": float(round(prices.max(), 0)),
        "histogram": {
            "values": [int(v) for v in hist_values],
            "bin_edges": [float(round(b, 0)) for b in bin_edges],
        },
    }


@app.get("/api/model-info", tags=["Model"])
async def model_info():
    """Zwraca metryki modelu i ważność cech."""
    from model.predict import load_model
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

    raw_data = load_training_data()
    features, target = prepare_data(raw_data)

    x_train, x_test, y_train, y_test = train_test_split(
        features, target, test_size=0.2, random_state=42
    )

    pipeline = load_model()
    predictions = pipeline.predict(x_test)

    rmse = float(np.sqrt(mean_squared_error(y_test, predictions)))
    mae = float(mean_absolute_error(y_test, predictions))
    r2 = float(r2_score(y_test, predictions))

    importance = get_feature_importance(pipeline)
    top_features = dict(list(importance.items())[:15])

    return {
        "metrics": {
            "rmse": round(rmse, 2),
            "mae": round(mae, 2),
            "r2": round(r2, 4),
        },
        "feature_importance": top_features,
    }


def get_resource_path(relative_path):
    """Zwraca ścieżkę do plików, działająca w IDE i po spakowaniu do .exe"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(__file__), relative_path)

static_path = get_resource_path("static")



app.mount("/static", StaticFiles(directory=static_path), name="static")

@app.get("/")
def read_root():
    index_file = os.path.join(static_path, "index.html")
    print("Serwowanie pliku: {}".format(index_file))
    return FileResponse(index_file)


if __name__ == "__main__":
    def open_browser():
        webbrowser.open("http://127.0.0.1:8000")


    threading.Timer(1.5, open_browser).start()

    uvicorn.run(app, host="127.0.0.1", port=8000, log_config=None)
