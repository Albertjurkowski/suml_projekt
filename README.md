# Inteligentna Wycena Domów Jednorodzinnych

Aplikacja desktopowa do przewidywania cen nieruchomości na podstawie modelu regresji liniowej, wytrenowanego na danych z Ames, Iowa (USA).

## 📥 Gotowe wersje do pobrania (One-Click)

Najnowsze, gotowe do uruchomienia wersje aplikacji (bez konieczności instalacji Pythona) są generowane automatycznie za pomocą GitHub Actions.

👉 **Jak pobrać aplikację:**
1. Przejdź do zakładki **[Actions](../../actions)** w tym repozytorium na GitHubie.
2. Kliknij najnowsze, udane uruchomienie o nazwie **Budowanie aplikacji (PyInstaller)**.
3. Zjedź na sam dół strony do sekcji **Artifacts**.
4. Kliknij i pobierz paczkę ZIP dla swojego systemu: `Wycena-Windows`, `Wycena-Mac` lub `Wycena-Linux`.

---

## Spis treści

- [Opis projektu](#opis-projektu)
- [Funkcjonalności](#funkcjonalności)
- [Struktura projektu](#struktura-projektu)
- [Wymagania](#wymagania)
- [Instalacja i uruchomienie](#instalacja-i-uruchomienie)
- [Budowanie własnego pliku wykonywalnego](#budowanie-własnego-pliku-wykonywalnego)
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
- **CI/CD (GitHub Actions)** — automatyczne budowanie plików `.exe`, `.app` i binarnych dla Linuksa
- **Docker** — konteneryzacja dla łatwego wdrożenia na serwerach

## Struktura projektu

Projekt jest zorganizowany z rozdzieleniem logiki na trzy główne warstwy: **data | model | app** oraz procesy automatyzacji.

```text
suml_projekt/
├── .github/                     # Automatyzacja CI/CD (GitHub Actions)
│   └── workflows/
│       └── build.yml            # Skrypt budujący gotowe paczki na Windows, macOS i Linux
│
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
