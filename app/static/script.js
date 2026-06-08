/* Nawigacja miedzy zakladkami */
document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.addEventListener('click', function () {
        document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));

        this.classList.add('active');
        const pageId = 'page-' + this.dataset.page;
        document.getElementById(pageId).classList.add('active');

        if (this.dataset.page === 'dane') loadDataStats();
        if (this.dataset.page === 'model') loadModelInfo();
    });
});

/* Formularz predykcji */
document.getElementById('predictionForm').addEventListener('submit', async function (e) {
    e.preventDefault();

    const requestData = {
        "gr_liv_area": parseInt(document.getElementById('grLivArea').value),
        "total_bsmt_sf": parseInt(document.getElementById('totalBsmtSf').value),
        "garage_cars": parseInt(document.getElementById('garageCars').value),
        "overall_qual": parseInt(document.getElementById('overallQual').value),
        "year_built": parseInt(document.getElementById('yearBuilt').value),
        "kitchen_qual": document.getElementById('kitchenQual').value,
        "first_flr_sf": parseInt(document.getElementById('firstFlrSf').value),
        "second_flr_sf": parseInt(document.getElementById('secondFlrSf').value),
        "lot_area": parseInt(document.getElementById('lotArea').value),
        "garage_area": parseInt(document.getElementById('garageArea').value),
        "year_remod": parseInt(document.getElementById('yearRemod').value),
        "full_bath": parseInt(document.getElementById('fullBath').value),
        "half_bath": parseInt(document.getElementById('halfBath').value),
        "bedrooms": parseInt(document.getElementById('bedrooms').value),
        "total_rooms": parseInt(document.getElementById('totalRooms').value),
        "fireplaces": parseInt(document.getElementById('fireplaces').value),
        "exter_qual": document.getElementById('exterQual').value
    };

    try {
        const response = await fetch('/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestData)
        });

        if (!response.ok) throw new Error('Blad serwera');

        const data = await response.json();

        document.getElementById('priceUSD').innerText =
            "Cena: $" + data.predicted_price_usd.toLocaleString('en-US');
        document.getElementById('pricePLN').innerText =
            "~ " + data.predicted_price_pln.toLocaleString('pl-PL') + " PLN";
        document.getElementById('priceRange').innerText =
            "Zakres: $" + data.price_range_low.toLocaleString('en-US') +
            " — $" + data.price_range_high.toLocaleString('en-US');

        const pct = data.percentile;
        document.getElementById('percentileText').innerText =
            pct.toFixed(1) + '% (drozsza od ' + pct.toFixed(0) + '% domow)';
        document.getElementById('percentileFill').style.width = pct + '%';
        document.getElementById('percentileMarker').style.left = pct + '%';

        document.getElementById('resultSection').classList.remove('hidden');

        loadSimilarHouses(requestData);
    } catch (error) {
        alert('Wystapil blad podczas przewidywania ceny.');
    }
});

/* Ladowanie statystyk danych */
let dataLoaded = false;
let histogramChart = null;

async function loadDataStats() {
    if (dataLoaded) return;

    try {
        const response = await fetch('/api/data-stats');
        const data = await response.json();

        document.getElementById('dataCount').innerText = data.count.toLocaleString();
        document.getElementById('dataFeatures').innerText = data.features_count;
        document.getElementById('dataMean').innerText = '$' + data.mean_price.toLocaleString('en-US');
        document.getElementById('dataMedian').innerText = '$' + data.median_price.toLocaleString('en-US');

        renderHistogram(data.histogram);
        dataLoaded = true;
    } catch (error) {
        console.error('Blad ladowania statystyk:', error);
    }
}

function renderHistogram(histogram) {
    const ctx = document.getElementById('histogramChart').getContext('2d');

    const labels = histogram.bin_edges.slice(0, -1).map((edge, i) => {
        const next = histogram.bin_edges[i + 1];
        return '$' + (edge / 1000).toFixed(0) + 'k';
    });

    if (histogramChart) histogramChart.destroy();

    histogramChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Liczba nieruchomosci',
                data: histogram.values,
                backgroundColor: 'rgba(74, 144, 217, 0.7)',
                borderColor: 'rgba(74, 144, 217, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false },
                title: { display: true, text: 'Histogram cen sprzedazy' }
            },
            scales: {
                x: { title: { display: true, text: 'Cena (USD)' } },
                y: { title: { display: true, text: 'Liczba nieruchomosci' } }
            }
        }
    });
}

/* Ladowanie informacji o modelu */
let modelLoaded = false;
let importanceChart = null;

async function loadModelInfo() {
    if (modelLoaded) return;

    try {
        const response = await fetch('/api/model-info');
        const data = await response.json();

        document.getElementById('metricRMSE').innerText =
            '$' + data.metrics.rmse.toLocaleString('en-US');
        document.getElementById('metricMAE').innerText =
            '$' + data.metrics.mae.toLocaleString('en-US');
        document.getElementById('metricR2').innerText = data.metrics.r2.toFixed(4);

        renderImportanceChart(data.feature_importance);
        modelLoaded = true;
    } catch (error) {
        console.error('Blad ladowania modelu:', error);
    }
}

/* Ladowanie podobnych domow */
async function loadSimilarHouses(requestData) {
    try {
        const response = await fetch('/api/similar-houses', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestData)
        });

        if (!response.ok) return;

        const data = await response.json();
        const tbody = document.getElementById('similarTableBody');
        tbody.innerHTML = '';

        data.similar_houses.forEach(house => {
            const row = document.createElement('tr');
            row.innerHTML =
                '<td>$' + house.price.toLocaleString('en-US') + '</td>' +
                '<td>' + house.area.toLocaleString() + ' sq ft</td>' +
                '<td>' + house.quality + '/10</td>' +
                '<td>' + house.year_built + '</td>' +
                '<td>' + house.neighborhood + '</td>';
            tbody.appendChild(row);
        });

        document.getElementById('similarSection').classList.remove('hidden');
    } catch (error) {
        console.error('Blad ladowania podobnych domow:', error);
    }
}

function renderImportanceChart(featureImportance) {
    const ctx = document.getElementById('importanceChart').getContext('2d');

    const labels = Object.keys(featureImportance).reverse();
    const values = Object.values(featureImportance).reverse();

    if (importanceChart) importanceChart.destroy();

    importanceChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Waznosc cechy',
                data: values,
                backgroundColor: labels.map((_, i) =>
                    `hsl(${120 + (i * 8)}, 60%, ${45 + (i * 2)}%)`
                ),
                borderWidth: 1
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            plugins: {
                legend: { display: false },
                title: { display: true, text: 'Top 15 najwazniejszych cech' }
            },
            scales: {
                x: { title: { display: true, text: 'Wspolczynnik wplywu (wartosc bezwzgledna)' } }
            }
        }
    });
}
