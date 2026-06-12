# Inteligentna Wycena Domów Jednorodzinnych

Aplikacja desktopowa do przewidywania cen nieruchomości na podstawie modelu regresji liniowej, wytrenowanego na danych z Ames, Iowa (USA).

## Spis treści

- [Opis projektu](#opis-projektu)
- [Funkcjonalności](#funkcjonalności)
- [Struktura projektu](#struktura-projektu)
- [Wymagania](#wymagania)
- [Instalacja i uruchomienie](#instalacja-i-uruchomienie)
- [Plik .exe (Windows)](#plik-exe-windows)
- [API REST](#api-rest)
- [Dane](#dane)
- [Model ML](#model-ml)
- [Jakość kodu](#jakość-kodu)
- [Autorzy](#autorzy)

## Opis projektu

Kupno albo sprzedaż domu to ważna decyzja finansowa. Pomyłka w wycenie może dużo kosztować, a profesjonalny rzeczoznawca jest drogi. Nasza aplikacja umożliwia **szybkie i bezpłatne sprawdzenie**, ile powinna kosztować nieruchomość.

Użytkownik wpisuje w formularz dane o nieruchomości (metraż, jakość, rok budowy itd.), a aplikacja zwraca **przewidywaną cenę** wraz z:
- zakresem szacunkowym (+/-15%)
- pozycją cenową na tle rynku (percentyl)
- listą 5 podobnych nieruchomości ze zbioru danych

## Funkcjonalności

- **Wycena nieruchomości** — formularz z parametrami budynku + opcje zaawansowane
- **Przegląd danych** — statystyki zbioru (liczba domów, średnia/mediana ceny) + histogram cen
- **Informacje o modelu** — metryki (RMSE, MAE, R²), wykres ważności cech, opis algorytmu
- **Porównanie z rynkiem** — percentyl cenowy i tabela podobnych domów
- **Automatyczne trenowanie** — model trenuje się przy pierwszym uruchomieniu
- **API REST** — endpointy FastAPI do integracji z innymi systemami
- **Plik .exe** — aplikacja one-click dla Windows (PyInstaller)
- **Docker** — konteneryzacja dla łatwego wdrożenia

## Struktura projektu

Projekt jest zorganizowany z rozdzieleniem logiki na trzy warstwy: **data | model | app**.

```
suml_projekt/
├── README.md
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .pylintrc
├── .gitignore
├── .dockerignore
├── run.sh
│
├── data/                        # Warstwa danych
│   ├── __init__.py
│   ├── download.py              # Ładowanie danych
│   ├── preprocess.py            # Preprocessing, inżynieria cech
│   └── raw/
│       └── train.csv            # Zbiór treningowy (Kaggle)
│
├── model/                       # Warstwa modelu ML
│   ├── __init__.py
│   ├── train.py                 # Trenowanie i ewaluacja
│   ├── predict.py               # Predykcja cen
│   └── saved/                   # Zapisany model (model.pkl)
│
├── app/                         # Warstwa aplikacji
│   ├── __init__.py
│   ├── api.py                   # FastAPI — serwer + endpointy
│   ├── config.py                # Konfiguracja (ścieżki, cechy, stałe)
│   ├── main.py                  # Streamlit UI (legacy)
│   ├── ui_components.py         # Komponenty Streamlit (legacy)
│   └── static/                  # Frontend HTML/CSS/JS
│       ├── index.html           # Główna strona z nawigacją
│       ├── script.js            # Logika frontendu + wykresy
│       ├── style.css            # Style (dark theme)
│       └── chart.min.js         # Chart.js (wykresy offline)
│
└── tests/                       # Testy jednostkowe
    ├── __init__.py
    ├── test_api.py
    ├── test_preprocess.py
    └── test_model.py
```

## Wymagania

- **Python 3.10+**
- Zależności z pliku `requirements.txt`:
  - `fastapi`, `uvicorn` — serwer HTTP + API REST
  - `pandas`, `numpy` — przetwarzanie danych
  - `scikit-learn` — model ML (regresja liniowa)
  - `matplotlib`, `seaborn` — wizualizacje (Streamlit legacy)
  - `joblib` — serializacja modelu
- **Docker** (opcjonalnie) — do uruchomienia w kontenerze

## Instalacja i uruchomienie

### Metoda 1: Standardowa (zalecana)

```bash
# Sklonuj repozytorium
git clone https://github.com/Albertjurkowski/suml_projekt.git
cd suml_projekt

# Stwórz środowisko wirtualne
python3 -m venv venv
source venv/bin/activate        # Linux/macOS
# venv\Scripts\activate         # Windows

# Zainstaluj zależności
pip install -r requirements.txt

# Uruchom aplikację
python app/api.py
```

Aplikacja uruchomi się pod adresem: **http://localhost:8000**
Przeglądarka otworzy się automatycznie.

> **Uwaga:** Przy pierwszym uruchomieniu model zostanie automatycznie wytrenowany (~5s).

### Metoda 2: Docker

```bash
docker compose up --build
```

Aplikacja dostępna pod: **http://localhost:8000**

## Plik .exe (Windows)

Aby zbudować plik wykonywalny .exe (nie wymaga Pythona u użytkownika):

```bash
pip install pyinstaller
pyinstaller --name "WycenaNieruchomosci" --windowed --add-data "app/static;static" --add-data "data;data" --add-data "model;model" app/api.py
```

Plik .exe znajdziesz w folderze `dist/WycenaNieruchomosci/`.
Uruchomienie: dwuklik na `WycenaNieruchomosci.exe` — aplikacja wystartuje serwer i otworzy przeglądarkę.

## API REST

Dokumentacja interaktywna (Swagger UI): **http://localhost:8000/docs**

### `POST /predict` — Wycena nieruchomości

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "gr_liv_area": 1500,
    "total_bsmt_sf": 800,
    "overall_qual": 7,
    "year_built": 2000,
    "garage_cars": 2,
    "kitchen_qual": "Gd"
  }'
```

Odpowiedź:
```json
{
  "predicted_price_usd": 185000.50,
  "predicted_price_pln": 740002.00,
  "price_range_low": 157250.43,
  "price_range_high": 212750.58,
  "percentile": 52.3
}
```

### `POST /api/similar-houses` — Podobne nieruchomości

Zwraca 5 najbliższych domów ze zbioru treningowego o podobnych parametrach.

### `GET /api/data-stats` — Statystyki danych

Zwraca liczbę rekordów, średnią/medianę cen oraz histogram do wizualizacji.

### `GET /api/model-info` — Metryki modelu

Zwraca RMSE, MAE, R² oraz top 15 najważniejszych cech.

### `GET /health` — Status serwisu

## Dane

### Źródło
Zestaw danych pochodzi z konkursu Kaggle:
[House Prices: Advanced Regression Techniques](https://www.kaggle.com/competitions/house-prices-advanced-regression-techniques)

### Charakterystyka
- **~2200 nieruchomości** z miasta Ames, Iowa (USA)
- **82 cechy** opisujące każdy aspekt nieruchomości
- **Zmienna docelowa:** cena sprzedaży (`SalePrice`)

### Format danych wejściowych
Użytkownik wprowadza dane przez formularz w aplikacji:
- Powierzchnie (stopy kw.): metraż mieszkalny, piwnica, garaż, działka
- Liczby całkowite: pokoje, łazienki, kominki, samochody w garażu
- Rok: budowa, remont
- Skala jakości: 1-10 (ogólna), Ex/Gd/TA/Fa/Po (materiały, kuchnia)

### Przetwarzanie danych
1. **Imputacja braków** — mediana dla cech numerycznych, stała wartość dla kategorycznych
2. **Inżynieria cech** — TotalSF, TotalBathrooms, HouseAge, IsRemodeled
3. **Kodowanie jakości** — Ex/Gd/TA/Fa/Po → 5/4/3/2/1
4. **Standaryzacja** — normalizacja cech numerycznych (StandardScaler)
5. **One-hot encoding** — kodowanie cech kategorycznych nominalnych

## Model ML

### Algorytm
**Regresja Liniowa** (Linear Regression) z biblioteki scikit-learn.

### Pipeline
```
Dane surowe → Inżynieria cech → Kodowanie jakości → [Imputacja + Standaryzacja | One-Hot] → Regresja Liniowa → Cena
```

### Metryki (zbiór testowy, 20% danych)
| Metryka | Wartość |
|---------|---------|
| RMSE    | ~$31,694 |
| MAE     | ~$19,615 |
| R²      | ~0.8103  |

### Trenowanie
- Podział danych: 80% treningowy / 20% testowy
- Model trenuje się automatycznie przy pierwszym uruchomieniu
- Wytrenowany model zapisywany do `model/saved/model.pkl`

## Jakość kodu

Projekt spełnia wymogi PEP8 i uzyskuje co najmniej 8/10 pkt w pylint.

```bash
# Uruchomienie pylint
pylint data/ model/ app/ --rcfile=.pylintrc

# Uruchomienie testów
python -m pytest tests/ -v
```

## Autorzy

Projekt realizowany w ramach przedmiotu **Środowiska Uruchomieniowe Machine Learning (SUML)**
Polsko-Japońska Akademia Technik Komputerowych, 2024/2025

| Numer indeksu |
|---------------|
| s27404        |
| s28825        |
| s27600        |
