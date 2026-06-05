# 🏠 Inteligentna Wycena Domów Jednorodzinnych

Aplikacja webowa do przewidywania cen nieruchomości na podstawie modelu regresji liniowej, wytrenowanego na danych z Ames, Iowa (USA).

## 📋 Spis treści

- [Opis projektu](#opis-projektu)
- [Funkcjonalności](#funkcjonalności)
- [Struktura projektu](#struktura-projektu)
- [Wymagania](#wymagania)
- [Instalacja i uruchomienie](#instalacja-i-uruchomienie)
- [Dane](#dane)
- [Model ML](#model-ml)
- [Autorzy](#autorzy)

## Opis projektu

Kupno albo sprzedaż domu to ważna decyzja finansowa. Pomyłka w wycenie może dużo kosztować, a profesjonalny rzeczoznawca jest drogi. Nasza aplikacja umożliwia **szybkie i bezpłatne sprawdzenie**, ile powinna kosztować nieruchomość.

Użytkownik wpisuje w formularz kilka podstawowych danych, takich jak:
- metraż (powierzchnia mieszkalna, piwnicy, garażu)
- liczba pokoi i łazienek
- rok budowy i remontu
- jakość materiałów i wykończenia

Aplikacja automatycznie zwraca **przewidywaną cenę** nieruchomości na podstawie wytrenowanego modelu regresji liniowej.

> **Uwaga:** Dane pochodzą z USA (Ames, Iowa), ale po dostarczeniu nowych danych można przetrenować model i dostosować go do nowych rynków.

## Funkcjonalności

- 🔮 **Wycena nieruchomości** — formularz z parametrami budynku → przewidywana cena
- 📊 **Przegląd danych** — statystyki, histogramy i próbki zbioru treningowego
- 🤖 **Informacje o modelu** — metryki (RMSE, MAE, R²), ważność cech, opis algorytmu
- 🔄 **Automatyczne trenowanie** — model trenuje się przy pierwszym uruchomieniu
- 🌐 **API REST** — endpoint FastAPI do integracji z innymi systemami
- 🐳 **Docker** — konteneryzacja dla łatwego wdrożenia

## Struktura projektu

Projekt jest zorganizowany z rozdzieleniem logiki na trzy warstwy: **data | model | app**.

```
house-price-predictor/
├── README.md
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .pylintrc
├── .gitignore
├── .dockerignore
├── run.sh
│
├── data/
│   ├── __init__.py
│   ├── download.py
│   ├── preprocess.py
│   └── raw/
│       └── train.csv
│
├── model/
│   ├── __init__.py
│   ├── train.py
│   ├── predict.py
│   └── saved/
│
├── app/
│   ├── __init__.py
│   ├── main.py                # Streamlit UI
│   ├── api.py                 # FastAPI REST
│   ├── ui_components.py
│   └── config.py
│
└── tests/
    ├── __init__.py
    ├── test_preprocess.py
    └── test_model.py
```

## Wymagania

- **Python 3.10+**
- Zależności wymienione w pliku `requirements.txt`:
  - `streamlit` — interfejs webowy
  - `fastapi`, `uvicorn` — API REST
  - `pandas`, `numpy` — przetwarzanie danych
  - `scikit-learn` — model ML (regresja liniowa)
  - `matplotlib`, `seaborn` — wizualizacje
  - `joblib` — serializacja modelu
- **Docker** (opcjonalnie) — do uruchomienia w kontenerze

## Instalacja i uruchomienie

### Metoda 1: Automatyczna (zalecana)

```bash
# Sklonuj repozytorium
git clone <URL_REPOZYTORIUM>
cd house-price-predictor

# Uruchom skrypt (automatycznie tworzy venv i instaluje zależności)
chmod +x run.sh
./run.sh
```

### Metoda 2: Ręczna

```bash
# Sklonuj repozytorium
git clone <URL_REPOZYTORIUM>
cd house-price-predictor

# Stwórz środowisko wirtualne
python3 -m venv venv
source venv/bin/activate

# Zainstaluj zależności
pip install -r requirements.txt

# Uruchom aplikację
streamlit run app/main.py
```

### Metoda 3: Bez środowiska wirtualnego

```bash
pip install -r requirements.txt
streamlit run app/main.py
```

Aplikacja Streamlit uruchomi się pod adresem: **http://localhost:8501**

> **Uwaga:** Przy pierwszym uruchomieniu model zostanie automatycznie wytrenowany.

### Metoda 4: Docker (zalecana do wdrożeń)

```bash
# Zbuduj i uruchom kontener
docker compose up --build
```

Kontener uruchomi oba serwisy:
- **Streamlit UI:** http://localhost:8501
- **FastAPI API:** http://localhost:8000

### Uruchomienie samego API (FastAPI)

```bash
pip install -r requirements.txt
uvicorn app.api:app --reload --port 8000
```

Dokumentacja API (Swagger): **http://localhost:8000/docs**

## API REST

### `POST /predict`

Przykład żądania:
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "gr_liv_area": 1500,
    "total_bsmt_sf": 800,
    "first_flr_sf": 1000,
    "overall_qual": 7,
    "year_built": 2000,
    "full_bath": 2,
    "bedrooms": 3,
    "garage_cars": 2
  }'
```

Przykład odpowiedzi:
```json
{
  "predicted_price_usd": 185000.50,
  "predicted_price_pln": 740002.00,
  "price_range_low": 157250.43,
  "price_range_high": 212750.58
}
```

### `GET /health`

Sprawdzenie statusu serwisu i modelu.

## Dane

### Źródło
Zestaw danych pochodzi z konkursu Kaggle:  
[House Prices: Advanced Regression Techniques](https://www.kaggle.com/competitions/house-prices-advanced-regression-techniques)

### Charakterystyka
- **~2200 nieruchomości** z miasta Ames, Iowa (USA)
- **82 cechy** opisujące każdy aspekt nieruchomości
- **Zmienna docelowa:** cena sprzedaży (`SalePrice`)
- **Typ danych:** tabularne (CSV)

### Przetwarzanie danych
1. **Imputacja braków** — mediana dla cech numerycznych, stała wartość dla kategorycznych
2. **Inżynieria cech** — nowe zmienne: TotalSF, TotalBathrooms, HouseAge, IsRemodeled
3. **Kodowanie jakości** — wartości Ex/Gd/TA/Fa/Po → 5/4/3/2/1
4. **Standaryzacja** — normalizacja cech numerycznych (StandardScaler)
5. **One-hot encoding** — kodowanie cech kategorycznych nominalnych

### Format danych wejściowych
Użytkownik wprowadza dane przez formularz w aplikacji:
- Powierzchnie (stopy kwadratowe): metraż, piwnica, garaż
- Liczby całkowite: pokoje, łazienki, kominki, samochody w garażu
- Rok: budowa, remont
- Skala jakości: 1-10 (ogólna), Ex/Gd/TA/Fa/Po (materiały)

## Model ML

### Algorytm
**Regresja Liniowa** (Linear Regression) z biblioteki scikit-learn.

### Pipeline
```
Dane surowe → Inżynieria cech → Kodowanie jakości → [Imputacja + Standaryzacja | One-Hot] → Regresja Liniowa → Cena
```

### Metryki
Model jest ewaluowany na zbiorze testowym (20% danych):
- **RMSE** (Root Mean Squared Error) — błąd średniokwadratowy
- **MAE** (Mean Absolute Error) — średni błąd bezwzględny
- **R²** (Coefficient of Determination) — współczynnik determinacji

### Trenowanie
- Podział danych: 80% treningowy / 20% testowy
- Model trenuje się automatycznie przy pierwszym uruchomieniu
- Wytrenowany model jest zapisywany do `model/saved/model.pkl`

## Jakość kodu

Projekt spełnia wymogi PEP8 i uzyskuje **co najmniej 8/10 pkt** w pylint.

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

## Licencja

Projekt edukacyjny — Polsko-Japońska Akademia Technik Komputerowych.
