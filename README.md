# Inteligentna Wycena Domów Jednorodzinnych

Aplikacja webowa do wyceny nieruchomości na podstawie modelu regresji liniowej, wytrenowanego na danych z Ames, Iowa (USA). Projekt realizowany w ramach przedmiotu **Środowiska Uruchomieniowe Machine Learning (SUML)**.

---

## Szybki start

Najprostszym sposobem na uruchomienie aplikacji jest skorzystanie ze skryptu `run.sh`, który automatycznie utworzy środowisko wirtualne, zainstaluje zależności i uruchomi serwer:

```bash
chmod +x run.sh
./run.sh
```

Aplikacja będzie dostępna pod adresem: **[http://localhost:8000](http://localhost:8000)** (przeglądarka otworzy się automatycznie).

---

## Gotowe aplikacje (bez instalacji)

Najnowsze wersje aplikacji są budowane automatycznie przez GitHub Actions i nie wymagają instalacji Pythona:
1. Przejdź do zakładki **[Actions](../../actions)**.
2. Wybierz najnowsze uruchomienie **Budowanie aplikacji (PyInstaller)**.
3. W sekcji **Artifacts** na dole strony pobierz paczkę dla swojego systemu.
4. Rozpakuj i uruchom plik wykonywalny (np. `WycenaNieruchomosci.exe` na Windowsie).

---

## Funkcjonalności

- **Wycena nieruchomości** – intuicyjny formularz z parametrami budynku.
- **Porównanie z rynkiem** – wyliczanie percentyla ceny i lista 5 podobnych domów ze zbioru treningowego.
- **Analiza danych** – statystyki zbioru danych z interaktywnym histogramem cen.
- **Informacje o modelu** – prezentacja metryk jakości oraz wykres ważności cech.
- **API REST** – dokumentacja Swagger UI dostępna pod adresem **[http://localhost:8000/docs](http://localhost:8000/docs)**.

---

## Dane i Model ML

- **Dane:** Zbiór [Ames Housing Dataset](https://www.kaggle.com/competitions/house-prices-advanced-regression-techniques) (~2200 domów, 82 cechy).
- **Algorytm:** Regresja Liniowa (`scikit-learn`) z preprocessingiem (imputacja braków, inżynieria cech, standaryzacja, one-hot encoding).
- **Metryki (zbiór testowy):**
  - **R²:** ~0.81
  - **MAE:** ~$19,615
  - **RMSE:** ~$31,694

---

## Jakość kodu i testy

Uruchomienie analizy statycznej (linter):
```bash
pylint data/ model/ app/ --rcfile=.pylintrc
```

Uruchomienie testów jednostkowych:
```bash
python -m pytest tests/ -v
```

---

## Autorzy (PJATK 2024/2025)

| Numer indeksu |
|---------------|
| s27404        |
| s28825        |
| s27600        |
