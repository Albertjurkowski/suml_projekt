document.getElementById('predictionForm').addEventListener('submit', async function(e) {
    e.preventDefault(); // Zapobiega przeładowaniu strony

    // Zbieranie danych z formularza
    const requestData = {
        "gr_liv_area": parseInt(document.getElementById('grLivArea').value),
        "total_bsmt_sf": parseInt(document.getElementById('totalBsmtSf').value),
        "garage_cars": parseInt(document.getElementById('garageCars').value),
        "overall_qual": parseInt(document.getElementById('overallQual').value),
        "year_built": parseInt(document.getElementById('yearBuilt').value),
        "kitchen_qual": document.getElementById('kitchenQual').value,

        // Domyślne wartości zdefiniowane w Twoim schemacie Pydantic
        "first_flr_sf": 1000,
        "second_flr_sf": 0,
        "lot_area": 8000,
        "garage_area": 400,
        "year_remod": 2000,
        "full_bath": 2,
        "half_bath": 0,
        "bedrooms": 3,
        "total_rooms": 7,
        "fireplaces": 1,
        "exter_qual": "TA"
    };

    try {
        // Wysłanie danych do API (używamy lokalnej ścieżki /predict)
        const response = await fetch('/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });

        if (!response.ok) {
            throw new Error('Błąd sieci lub serwera');
        }

        const data = await response.json();

        // Wyświetlanie wyniku
        const resultSection = document.getElementById('resultSection');
        const priceUSD = document.getElementById('priceUSD');
        const pricePLN = document.getElementById('pricePLN');

        // Pobieramy wartość predykcji. Zakładam, że Twoje API zwraca JSON np. {"prediction": 200000}
        // Dostosuj słowo 'prediction' do tego, co dokładnie zwraca Twój plik api.py
        const predictedPrice = data.predicted_price_usd;
        const predictedPLN = data.predicted_price_pln;
        // Formatowanie liczb
        priceUSD.innerText = "Cena: $ " + predictedPrice.toLocaleString('en-US');
        pricePLN.innerText = "~ " + predictedPLN.toLocaleString('pl-PL') + " PLN";

        resultSection.classList.remove('hidden');

    } catch (error) {
        console.error('Wystąpił błąd:', error);
        alert('Wystąpił błąd podczas przewidywania ceny. Sprawdź konsolę.');
    }
});