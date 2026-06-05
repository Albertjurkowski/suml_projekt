"""
API REST — endpoint FastAPI do predykcji cen nieruchomości.

Udostępnia interfejs HTTP do wykonywania wycen nieruchomości.
Uruchomienie: uvicorn app.api:app --reload --port 8000
"""

import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import MODEL_PATH
from data.download import load_training_data
from data.preprocess import prepare_single_input
from model.predict import predict_price
from model.train import train_model


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

        margin = price * 0.15
        return PredictionResponse(
            predicted_price_usd=round(price, 2),
            predicted_price_pln=round(price * 4.0, 2),
            price_range_low=round(price - margin, 2),
            price_range_high=round(price + margin, 2),
        )
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error
