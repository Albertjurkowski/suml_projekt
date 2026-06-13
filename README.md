# Inteligentna Wycena Domów Jednorodzinnych

Aplikacja webowa do wyceny nieruchomości na podstawie modelu regresji liniowej, wytrenowanego na danych z Ames, Iowa (USA). Projekt realizowany w ramach przedmiotu **Środowiska Uruchomieniowe Machine Learning (SUML)**.

---

## Szybki start

Aby uruchomić aplikację, wykonaj następujące kroki:

1. **Otwórz Terminal** (na macOS możesz go znaleźć np. przez Spotlight `Cmd + Spacja` i wpisując "Terminal").
2. **Przejdź do katalogu projektu**:
   Wpisz w terminalu komendę `cd` (ze spacją na końcu), a następnie przeciągnij i upuść folder z projektem z Findera do okna terminala i wciśnij `Enter`. Ścieżka uzupełni się automatycznie, np.:
   ```bash
   cd /sciezka/do/projektu/house-price-predictor
   ```
3. **Nadaj uprawnienia do uruchomienia skryptu** (wymagane tylko raz na macOS/Linux):
   ```bash
   chmod +x run.sh
   ```
4. **Uruchom aplikację**:
   ```bash
   ./run.sh
   ```

Skrypt automatycznie utworzy środowisko wirtualne Python, zainstaluje niezbędne biblioteki oraz uruchomi serwer.

Po pomyślnym uruchomieniu przeglądarka otworzy się automatycznie. Jeśli tak się nie stanie, otwórz przeglądarkę ręcznie i przejdź pod adres: **[http://localhost:8000](http://localhost:8000)**.

---

## Gotowe aplikacje (bez instalacji)

Najnowsze wersje aplikacji są budowane automatycznie przez GitHub Actions i nie wymagają instalowania Pythona ani żadnych zależności.

### 1. Pobranie paczki
1. Na górnym pasku tego repozytorium GitHub kliknij zakładkę **[Actions](../../actions)**.
2. Na liście po lewej stronie wybierz przepływ **Budowanie aplikacji (PyInstaller)**.
3. Kliknij na najnowsze uruchomienie na liście (oznaczone zielonym symbolem powodzenia).
4. Przewiń stronę na sam dół do sekcji **Artifacts** i kliknij nazwę paczki przeznaczonej dla Twojego systemu operacyjnego, aby pobrać plik `.zip`:
   - `Wycena-Windows` (dla Windowsa)
   - `Wycena-Mac` (dla macOS)
   - `Wycena-Linux` (dla Linuksa)

### 2. Uruchomienie na komputerze

Rozpakuj pobrane archiwum `.zip` i wykonaj poniższe kroki w zależności od systemu:

#### Windows
1. Wejdź do rozpakowanego folderu.
2. Kliknij dwukrotnie w plik **`WycenaNieruchomosci.exe`**.
3. Otworzy się okno konsoli uruchamiające serwer, a po chwili w przeglądarce automatycznie otworzy się strona aplikacji pod adresem `http://localhost:8000`.

#### macOS
1. Otwórz **Terminal** (np. poprzez wyszukiwarkę Spotlight: `Cmd + Spacja` i wpisanie "Terminal").
2. Wpisz komendę `cd` (ze spacją na końcu).
3. Przeciągnij i upuść rozpakowany folder z aplikacji Finder do okna Terminala, a następnie wciśnij klawisz `Enter`.
4. (Opcjonalnie) Jeśli macOS zablokuje uruchomienie aplikacji od niezidentyfikowanego twórcy (z powodu kwarantanny), usuń flagę kwarantanny komendą:
   ```bash
   xattr -cr .
   ```
   *Alternatywnie, możesz podać pełną ścieżkę do pobranego katalogu, na przykład:*
   ```bash
   xattr -cr /Users/username/Downloads/Wycena-Mac/
   ```
5. Uruchom program, wpisując komendę:
   ```bash
   ./WycenaNieruchomosci
   ```

#### Linux
1. Otwórz terminal wewnątrz rozpakowanego katalogu.
2. Nadaj plikowi uprawnienia do uruchomienia:
   ```bash
   chmod +x WycenaNieruchomosci
   ```
3. Uruchom aplikację komendą:
   ```bash
   ./WycenaNieruchomosci
   ```

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

Aplikacja spełnia wysokie standardy jakości kodu:
- **Ocena pylint:** **9.68/10**
- **Testy jednostkowe:** **26/26 zaliczonych**

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

| Numer indeksu | Wkład |
|---------------|-------|
| s27404        |       |
| s28825        |       |
| s27600        | Rozbudowa frontendu (nawigacja zakładkowa, dark theme, opcje zaawansowane w formularzu), interaktywne wykresy Chart.js (histogram cen, ważność cech), nowe endpointy API (statystyki danych, metryki modelu, podobne nieruchomości, percentyl cenowy) |
