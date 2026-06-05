"""
Główny punkt wejścia aplikacji Streamlit.

Uruchomienie: streamlit run app/main.py

Aplikacja pozwala na:
- Wycenę nieruchomości na podstawie parametrów budynku
- Przeglądanie danych treningowych
- Podgląd metryk i ważności cech modelu
"""

import os
import sys
import numpy as np
import streamlit as st
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import PAGE_TITLE, PAGE_ICON, PAGE_LAYOUT, MODEL_PATH, TEST_SIZE, RANDOM_STATE
from app.ui_components import (
    render_input_form,
    render_prediction_result,
    render_feature_importance,
    render_data_overview,
    render_model_metrics,
    render_sidebar_info,
)
from data.download import load_training_data
from data.preprocess import prepare_data, prepare_single_input
from model.predict import predict_price, load_model
from model.train import train_model, get_feature_importance



st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout=PAGE_LAYOUT,
)


@st.cache_resource
def get_trained_model():
    """
    Ładuje lub trenuje model — wywoływane tylko raz dzięki cache.

    Returns:
        dict: Metryki modelu po trenowaniu.
    """
    if not os.path.exists(MODEL_PATH):
        st.info("🔄 Trenowanie modelu... To może zająć kilka sekund.")
        metrics = train_model()
        return metrics
    return None


@st.cache_data
def get_raw_data():
    """
    Ładuje surowe dane treningowe — cache'owane dla wydajności.

    Returns:
        pd.DataFrame: Ramka danych treningowych.
    """
    return load_training_data()


def page_prediction():
    """Renderuje stronę wyceny nieruchomości."""
    st.title("🏠 Inteligentna Wycena Nieruchomości")
    st.markdown(
        "Wypełnij formularz poniżej, aby otrzymać przewidywaną cenę domu "
        "na podstawie modelu regresji liniowej."
    )


    get_trained_model()


    input_data = render_input_form()


    st.markdown("---")
    if st.button("🔮 Wycena nieruchomości", type="primary", use_container_width=True):
        with st.spinner("Obliczanie wyceny..."):

            raw_data = get_raw_data()
            features = prepare_single_input(input_data, raw_data)


            predicted_price = predict_price(features)


            render_prediction_result(predicted_price)


def page_data():
    """Renderuje stronę przeglądu danych."""
    st.title("📊 Przegląd Danych Treningowych")

    raw_data = get_raw_data()
    render_data_overview(raw_data)


def page_model():
    """Renderuje stronę informacji o modelu."""
    st.title("🤖 Informacje o Modelu")


    metrics = get_trained_model()
    if metrics:
        render_model_metrics(metrics)
    else:
        st.info("Model załadowany z dysku.")
        raw_data = get_raw_data()
        features, target = prepare_data(raw_data)

        _, x_test, _, y_test = train_test_split(
            features, target, test_size=TEST_SIZE, random_state=RANDOM_STATE
        )
        pipeline = load_model()
        predictions = pipeline.predict(x_test)

        recalculated_metrics = {
            "rmse": round(np.sqrt(mean_squared_error(y_test, predictions)), 2),
            "mae": round(mean_absolute_error(y_test, predictions), 2),
            "r2": round(r2_score(y_test, predictions), 4),
        }
        render_model_metrics(recalculated_metrics)


    try:
        pipeline = load_model()
        raw_data = get_raw_data()
        features, _ = prepare_data(raw_data)
        importance = get_feature_importance(pipeline, list(features.columns))
        render_feature_importance(importance)
    except (FileNotFoundError, ValueError) as error:
        st.warning(f"Nie można wyświetlić ważności cech: {error}")


    st.markdown("---")
    st.subheader("📝 Opis modelu")
    st.markdown(
        """
        **Typ modelu:** Regresja Liniowa (Linear Regression)

        **Preprocessing:**
        - Imputacja braków: mediana (numeryczne), stała wartość (kategoryczne)
        - Standaryzacja cech numerycznych (StandardScaler)
        - Kodowanie one-hot dla cech kategorycznych
        - Inżynieria cech: TotalSF, TotalBathrooms, HouseAge, IsRemodeled

        **Dane:** Kaggle House Prices — Advanced Regression Techniques
        - ~2200 nieruchomości z Ames, Iowa (USA)
        - 80+ cech opisujących każdy aspekt nieruchomości
        - Zmienna docelowa: cena sprzedaży (SalePrice)

        **Podział danych:** 80% treningowy / 20% testowy
        """
    )


def main():
    """Główna funkcja aplikacji — routing między stronami."""
    selected_page = render_sidebar_info()

    if selected_page == "Wycena":
        page_prediction()
    elif selected_page == "Dane":
        page_data()
    elif selected_page == "Model":
        page_model()


if __name__ == "__main__":
    main()
