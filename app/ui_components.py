"""
Komponenty interfejsu użytkownika — wielokrotnie używane widżety Streamlit.

Moduł zawiera funkcje renderujące poszczególne sekcje aplikacji:
formularz wejściowy, wynik predykcji, ważność cech i przegląd danych.
"""

import os
import sys
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.config import QUALITY_MAPPING


def render_input_form() -> dict:
    """
    Renderuje formularz do wprowadzania danych o nieruchomości.

    Formularz zawiera pola dla najważniejszych cech wpływających
    na cenę domu. Używa widżetów Streamlit (suwaki, selectboxy).

    Returns:
        dict: Słownik z wartościami wprowadzonymi przez użytkownika.
    """
    st.subheader("📋 Dane nieruchomości")


    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("##### 📐 Wymiary i powierzchnia")
        gr_liv_area = st.slider(
            "Powierzchnia mieszkalna (stopy kw.)",
            min_value=300, max_value=5000, value=1500, step=50,
            help="Łączna powierzchnia mieszkalna nad ziemią"
        )
        total_bsmt_sf = st.slider(
            "Powierzchnia piwnicy (stopy kw.)",
            min_value=0, max_value=3000, value=800, step=50,
            help="Całkowita powierzchnia piwnicy"
        )
        first_floor_sf = st.slider(
            "Powierzchnia parteru (stopy kw.)",
            min_value=300, max_value=4000, value=1000, step=50,
        )
        second_floor_sf = st.slider(
            "Powierzchnia piętra (stopy kw.)",
            min_value=0, max_value=2500, value=0, step=50,
        )
        lot_area = st.slider(
            "Powierzchnia działki (stopy kw.)",
            min_value=1000, max_value=50000, value=8000, step=500,
        )

        st.markdown("##### 🚗 Garaż")
        garage_cars = st.selectbox("Pojemność garażu (samochody)", [0, 1, 2, 3, 4], index=2)
        garage_area = st.slider(
            "Powierzchnia garażu (stopy kw.)",
            min_value=0, max_value=1500, value=400, step=50,
        )

    with col_right:
        st.markdown("##### 🏠 Parametry budynku")
        overall_qual = st.slider(
            "Ogólna jakość (1-10)",
            min_value=1, max_value=10, value=6,
            help="1 = bardzo słaba, 10 = doskonała"
        )
        year_built = st.slider(
            "Rok budowy",
            min_value=1870, max_value=2025, value=1990,
        )
        year_remod = st.slider(
            "Rok remontu",
            min_value=1870, max_value=2025, value=2000,
        )

        st.markdown("##### 🚿 Łazienki i pokoje")
        full_bath = st.selectbox("Łazienki pełne", [0, 1, 2, 3, 4], index=2)
        half_bath = st.selectbox("Łazienki połówkowe", [0, 1, 2], index=0)
        bedrooms = st.selectbox("Sypialnie", [0, 1, 2, 3, 4, 5, 6], index=3)
        total_rooms = st.slider("Łączna liczba pokoi", min_value=2, max_value=15, value=7)
        fireplaces = st.selectbox("Kominki", [0, 1, 2, 3], index=1)

        st.markdown("##### ⭐ Jakość elementów")
        kitchen_qual = st.selectbox(
            "Jakość kuchni",
            options=list(QUALITY_MAPPING.keys()),
            index=2,
            format_func=lambda x: {
                "Ex": "Doskonała", "Gd": "Dobra",
                "TA": "Średnia", "Fa": "Dostateczna", "Po": "Słaba"
            }[x]
        )
        exter_qual = st.selectbox(
            "Jakość materiałów zewnętrznych",
            options=list(QUALITY_MAPPING.keys()),
            index=2,
            format_func=lambda x: {
                "Ex": "Doskonała", "Gd": "Dobra",
                "TA": "Średnia", "Fa": "Dostateczna", "Po": "Słaba"
            }[x]
        )


    input_data = {
        "Gr Liv Area": gr_liv_area,
        "Total Bsmt SF": total_bsmt_sf,
        "1st Flr SF": first_floor_sf,
        "2nd Flr SF": second_floor_sf,
        "Lot Area": lot_area,
        "Garage Cars": garage_cars,
        "Garage Area": garage_area,
        "Overall Qual": overall_qual,
        "Year Built": year_built,
        "Year Remod/Add": year_remod,
        "Full Bath": full_bath,
        "Half Bath": half_bath,
        "Bedroom AbvGr": bedrooms,
        "TotRms AbvGrd": total_rooms,
        "Fireplaces": fireplaces,
        "Kitchen Qual": kitchen_qual,
        "Exter Qual": exter_qual,
        "Bsmt Full Bath": 0,
        "Bsmt Half Bath": 0,
        "Wood Deck SF": 0,
        "Open Porch SF": 0,
        "Mas Vnr Area": 0,
        "Yr Sold": 2010,
    }

    return input_data


def render_prediction_result(predicted_price: float) -> None:
    """
    Wyświetla wynik predykcji ceny w atrakcyjnym formacie.

    Args:
        predicted_price: Przewidywana cena nieruchomości w USD.
    """
    st.markdown("---")
    st.subheader("💰 Wynik wyceny")


    col_price, col_info = st.columns([2, 1])

    with col_price:
        st.metric(
            label="Przewidywana cena nieruchomości",
            value=f"${predicted_price:,.0f}",
            delta=None,
        )

    with col_info:

        price_pln = predicted_price * 4.0
        st.info(f"~{price_pln:,.0f} PLN\n\n(kurs orientacyjny: 1 USD = 4 PLN)")

    margin = predicted_price * 0.15
    st.caption(
        f"Zakres szacunkowy: ${predicted_price - margin:,.0f} — "
        f"${predicted_price + margin:,.0f}"
    )


def render_feature_importance(feature_importance: dict, top_n: int = 15) -> None:
    """
    Wyświetla wykres ważności cech modelu.

    Args:
        feature_importance: Słownik {nazwa_cechy: ważność}.
        top_n: Liczba najważniejszych cech do wyświetlenia.
    """
    st.subheader("📊 Ważność cech w modelu")


    top_features = dict(list(feature_importance.items())[:top_n])


    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(
        x=list(top_features.values()),
        y=list(top_features.keys()),
        palette="viridis",
        ax=ax,
    )
    ax.set_xlabel("Współczynnik wpływu (wartość bezwzględna)")
    ax.set_ylabel("Cecha")
    ax.set_title(f"Top {top_n} najważniejszych cech")
    plt.tight_layout()

    st.pyplot(fig)
    plt.close(fig)


def render_data_overview(dataframe: pd.DataFrame) -> None:
    """
    Wyświetla przegląd statystyczny zestawu danych.

    Args:
        dataframe: Ramka danych treningowych.
    """
    st.subheader("📈 Przegląd danych")


    col_stats1, col_stats2, col_stats3, col_stats4 = st.columns(4)
    with col_stats1:
        st.metric("Liczba domów", f"{len(dataframe):,}")
    with col_stats2:
        st.metric("Liczba cech", f"{dataframe.shape[1]}")
    with col_stats3:
        st.metric("Średnia cena", f"${dataframe['SalePrice'].mean():,.0f}")
    with col_stats4:
        st.metric("Mediana ceny", f"${dataframe['SalePrice'].median():,.0f}")


    st.markdown("##### Rozkład cen nieruchomości")
    fig, ax = plt.subplots(figsize=(10, 4))
    sns.histplot(dataframe["SalePrice"], bins=50, kde=True, color="#4A90D9", ax=ax)
    ax.set_xlabel("Cena (USD)")
    ax.set_ylabel("Liczba nieruchomości")
    ax.set_title("Histogram cen sprzedaży")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)


    with st.expander("Pokaż przykładowe dane"):
        st.dataframe(dataframe.head(10), use_container_width=True)


def render_model_metrics(metrics: dict) -> None:
    """
    Wyświetla metryki jakości modelu.

    Args:
        metrics: Słownik z metrykami (RMSE, MAE, R²).
    """
    st.subheader("🎯 Metryki modelu")

    col_rmse, col_mae, col_r2 = st.columns(3)

    with col_rmse:
        st.metric(
            label="RMSE",
            value=f"${metrics['rmse']:,.0f}",
            help="Root Mean Squared Error — średni błąd kwadratowy"
        )
    with col_mae:
        st.metric(
            label="MAE",
            value=f"${metrics['mae']:,.0f}",
            help="Mean Absolute Error — średni błąd bezwzględny"
        )
    with col_r2:
        st.metric(
            label="R²",
            value=f"{metrics['r2']:.4f}",
            help="Współczynnik determinacji (1.0 = idealny model)"
        )


def render_sidebar_info() -> str:
    """
    Renderuje pasek boczny z informacjami o aplikacji.

    Returns:
        str: Nazwa wybranej strony nawigacji.
    """
    with st.sidebar:
        st.title("🏠 Menu")
        st.markdown("---")

        page = st.radio(
            "Nawigacja",
            options=["Wycena", "Dane", "Model"],
            label_visibility="collapsed",
        )

        st.markdown("---")
        st.markdown(
            """
            ### O aplikacji
            Inteligentna wycena domów jednorodzinnych
            na podstawie modelu regresji liniowej.

            **Dane:** Kaggle House Prices  
            **Model:** Linear Regression  
            **Autorzy:** s27404, s28825, s27600
            """
        )

        st.markdown("---")
        st.caption("SUML 2024/2025 — Projekt zaliczeniowy")

    return page