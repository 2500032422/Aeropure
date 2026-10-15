// --------------------------------------------------
// Sidebar navigation
// --------------------------------------------------

function showSection(sectionId, clickedButton) {

    const sections = document.querySelectorAll(".content-section");

    sections.forEach(section => {
        section.classList.remove("active-section");
    });

    const selectedSection = document.getElementById(sectionId);

    if (selectedSection) {
        selectedSection.classList.add("active-section");
    }

    const navItems = document.querySelectorAll(".nav-item");

    navItems.forEach(item => {
        item.classList.remove("active");
    });

    if (clickedButton) {
        clickedButton.classList.add("active");
    }

    if (sectionId === "advanced-analysis") {
        loadAdvancedAnalysis(false);
    }

    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });
}


// --------------------------------------------------
// Load station-wise dataset
// --------------------------------------------------

async function loadStationData() {

    const stationSelect = document.getElementById("stationSelect");
    const station = stationSelect.value;

    const tableHead = document.getElementById("stationTableHead");
    const tableBody = document.getElementById("stationTableBody");
    const stationSummary = document.getElementById("stationSummary");

    if (!station) {

        tableHead.innerHTML = "";

        tableBody.innerHTML = `
            <tr>
                <td colspan="5" class="empty-state">
                    Select a station to display its dataset.
                </td>
            </tr>
        `;

        stationSummary.classList.add("hidden");

        return;
    }

    tableBody.innerHTML = `
        <tr>
            <td colspan="5" class="empty-state">
                Loading station data...
            </td>
        </tr>
    `;

    try {

        const response = await fetch(
            `/api/station/${encodeURIComponent(station)}?limit=100`
        );

        const result = await response.json();

        if (!result.success) {
            throw new Error(result.message);
        }

        // Station summary

        stationSummary.classList.remove("hidden");

        stationSummary.innerHTML = `
            <div class="summary-pill">
                Station: <strong>${result.station}</strong>
            </div>

            <div class="summary-pill">
                Total Records: <strong>${result.total_rows}</strong>
            </div>

            <div class="summary-pill">
                Displayed: <strong>${result.rows.length}</strong>
            </div>
        `;

        // Table headers

        tableHead.innerHTML = `
            <tr>
                ${result.columns.map(column => `
                    <th>${column}</th>
                `).join("")}
            </tr>
        `;

        // Table rows

        tableBody.innerHTML = "";

        result.rows.forEach(row => {

            const tableRow = document.createElement("tr");

            result.columns.forEach(column => {

                const cell = document.createElement("td");

                let value = row[column];

                if (value === null || value === undefined) {
                    value = "—";
                }

                cell.textContent = value;

                tableRow.appendChild(cell);
            });

            tableBody.appendChild(tableRow);
        });

    } catch (error) {

        tableBody.innerHTML = `
            <tr>
                <td colspan="5" class="empty-state">
                    Failed to load station data.
                </td>
            </tr>
        `;

        console.error("Station data error:", error);
    }
}


// --------------------------------------------------
// Prediction form
// --------------------------------------------------

const predictionForm = document.getElementById("predictionForm");

if (predictionForm) {

    predictionForm.addEventListener("submit", async function(event) {

        event.preventDefault();

        const formData = new FormData(predictionForm);

        const payload = {};

        formData.forEach((value, key) => {
            payload[key] = parseFloat(value);
        });

        const resultBox = document.getElementById("predictionResult");

        resultBox.classList.remove("hidden");
        resultBox.classList.remove(
            "quality-good",
            "quality-moderate",
            "quality-unhealthy",
            "quality-very-high"
        );

        resultBox.innerHTML = "Calculating prediction...";

        try {

            const response = await fetch("/predict", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(payload)
            });

            const result = await response.json();

            if (!result.success) {
                throw new Error(result.message);
            }

            const prediction = result.prediction;
            const quality = getPM25Quality(prediction);

            resultBox.innerHTML = `
                <span class="prediction-result-heading">Predicted PM2.5 Concentration</span>
                <strong>${Number(prediction).toFixed(2)} µg/m³</strong>
                <span class="prediction-quality-label">${quality.label}</span>
                <p class="prediction-quality-message">${quality.message}</p>
            `;

            resultBox.classList.remove(
                "quality-good",
                "quality-moderate",
                "quality-unhealthy",
                "quality-very-high"
            );
            resultBox.classList.add(quality.className);

            savePredictionHistory(prediction);

            displayPredictionHistory();

        } catch (error) {

            resultBox.classList.remove(
                "quality-good",
                "quality-moderate",
                "quality-unhealthy",
                "quality-very-high"
            );

            resultBox.innerHTML = `
                Prediction failed.
                <strong>${error.message}</strong>
            `;

            console.error("Prediction error:", error);
        }

    });

}


function getPM25Quality(value) {

    const pm25 = Number(value);

    if (pm25 <= 35) {
        return {
            label: "Good air quality",
            message: "PM2.5 is low. The air is considered healthy.",
            className: "quality-good"
        };
    }

    if (pm25 <= 75) {
        return {
            label: "Moderate air quality",
            message: "Air quality is acceptable for most people.",
            className: "quality-moderate"
        };
    }

    if (pm25 <= 150) {
        return {
            label: "Unhealthy air quality",
            message: "PM2.5 is elevated. Sensitive groups may experience health effects.",
            className: "quality-unhealthy"
        };
    }

    return {
        label: "Very high pollution",
        message: "PM2.5 is very high. Limit prolonged outdoor exposure where possible.",
        className: "quality-very-high"
    };
}


// --------------------------------------------------
// Save prediction history in localStorage
// --------------------------------------------------

function savePredictionHistory(prediction) {

    let history = JSON.parse(
        localStorage.getItem("airnova_prediction_history")
    ) || [];

    const record = {
        prediction: prediction,
        timestamp: new Date().toLocaleString()
    };

    history.unshift(record);

    localStorage.setItem(
        "airnova_prediction_history",
        JSON.stringify(history)
    );
}


// --------------------------------------------------
// Display prediction history
// --------------------------------------------------

function displayPredictionHistory() {

    const tableBody = document.getElementById("historyTableBody");
    const emptyHistory = document.getElementById("emptyHistory");

    if (!tableBody) {
        return;
    }

    const history = JSON.parse(
        localStorage.getItem("airnova_prediction_history")
    ) || [];

    tableBody.innerHTML = "";

    if (history.length === 0) {

        emptyHistory.classList.remove("hidden");

        return;
    }

    emptyHistory.classList.add("hidden");

    history.forEach(record => {

        const row = document.createElement("tr");

        row.innerHTML = `
            <td>${record.timestamp}</td>
            <td>
                <strong>${record.prediction} µg/m³</strong>
            </td>
        `;

        tableBody.appendChild(row);
    });
}


// --------------------------------------------------
// Clear prediction history
// --------------------------------------------------

function clearPredictionHistory() {

    const confirmation = confirm(
        "Are you sure you want to clear all prediction history?"
    );

    if (!confirmation) {
        return;
    }

    localStorage.removeItem("airnova_prediction_history");

    displayPredictionHistory();
}


// --------------------------------------------------
// Initialize history on page load
// --------------------------------------------------

document.addEventListener("DOMContentLoaded", function() {
    displayPredictionHistory();
});

// --------------------------------------------------
// Advanced analysis: K-Means, PCA and 10-fold CV
// --------------------------------------------------
let advancedAnalysisLoaded = false;
let advancedAnalysisLoading = false;

async function loadAdvancedAnalysis(forceRefresh = false) {
    if (advancedAnalysisLoading || (advancedAnalysisLoaded && !forceRefresh)) return;

    const status = document.getElementById("advancedStatus");
    const errorBox = document.getElementById("advancedError");
    const button = document.getElementById("runAdvancedAnalysis");
    if (!status) return;

    advancedAnalysisLoading = true;
    status.textContent = "Calculating K-Means, PCA and 10-fold CV. Please wait...";
    errorBox.classList.add("hidden");
    button.disabled = true;

    try {
        const response = await fetch("/api/advanced-analysis");
        const result = await response.json();
        if (!response.ok || !result.success) throw new Error(result.message || "Analysis failed.");

        renderAdvancedAnalysis(result);
        advancedAnalysisLoaded = true;
        status.textContent = "Analysis completed successfully.";
    } catch (error) {
        errorBox.textContent = "Could not calculate advanced analysis: " + error.message;
        errorBox.classList.remove("hidden");
        status.textContent = "Analysis could not be completed.";
    } finally {
        advancedAnalysisLoading = false;
        button.disabled = false;
    }
}

function renderAdvancedAnalysis(result) {
    const clusterSummary = document.getElementById("clusterSummary");
    clusterSummary.innerHTML = "";
    result.clustering.counts.forEach(item => {
        const pill = document.createElement("div");
        pill.className = "summary-pill";
        pill.textContent = `${item.cluster}: ${item.count.toLocaleString()} records`;
        clusterSummary.appendChild(pill);
    });

    document.getElementById("pcaVariance").textContent =
        `PC1 ${result.pca.pc1_variance}% · PC2 ${result.pca.pc2_variance}% · Total ${result.pca.total_variance}%`;
    drawPcaPlot(result.pca.points);

    const cv = result.cross_validation;
    document.getElementById("cvMeanR2").textContent = `${cv.mean_r2}%`;
    document.getElementById("cvMeanMae").textContent = cv.mean_mae;
    document.getElementById("cvMeanRmse").textContent = cv.mean_rmse;
    document.getElementById("cvDetails").textContent =
        `10-fold CV on ${cv.sample_size.toLocaleString()} complete sampled records · R² standard deviation: ${cv.std_r2}%`;

    const body = document.getElementById("cvTableBody");
    body.innerHTML = "";
    cv.folds.forEach(fold => {
        const row = document.createElement("tr");
        [fold.fold, `${fold.r2}%`, fold.mae, fold.rmse].forEach(value => {
            const cell = document.createElement("td");
            cell.textContent = value;
            row.appendChild(cell);
        });
        body.appendChild(row);
    });
}

function drawPcaPlot(points) {
    const canvas = document.getElementById("pcaCanvas");
    if (!canvas || !points || !points.length) return;
    const ctx = canvas.getContext("2d");
    const width = canvas.width, height = canvas.height;
    const pad = 48;
    ctx.clearRect(0, 0, width, height);
    ctx.fillStyle = "#101827";
    ctx.fillRect(0, 0, width, height);

    const xs = points.map(p => p.x), ys = points.map(p => p.y);
    const minX = Math.min(...xs), maxX = Math.max(...xs);
    const minY = Math.min(...ys), maxY = Math.max(...ys);
    const xRange = maxX - minX || 1, yRange = maxY - minY || 1;

    ctx.strokeStyle = "rgba(148,163,184,0.22)";
    ctx.lineWidth = 1;
    for (let i = 0; i <= 4; i++) {
        const x = pad + (width - pad * 2) * i / 4;
        const y = pad + (height - pad * 2) * i / 4;
        ctx.beginPath(); ctx.moveTo(x, pad); ctx.lineTo(x, height - pad); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(pad, y); ctx.lineTo(width - pad, y); ctx.stroke();
    }

    const clusterColors = ["#38bdf8", "#a78bfa", "#34d399", "#fbbf24"];
    points.forEach(p => {
        const x = pad + ((p.x - minX) / xRange) * (width - pad * 2);
        const y = height - pad - ((p.y - minY) / yRange) * (height - pad * 2);
        ctx.fillStyle = clusterColors[p.cluster % clusterColors.length];
        ctx.globalAlpha = 0.72;
        ctx.beginPath(); ctx.arc(x, y, 2.8, 0, Math.PI * 2); ctx.fill();
    });
    ctx.globalAlpha = 1;
    ctx.fillStyle = "#cbd5e1";
    ctx.font = "13px Inter, sans-serif";
    ctx.fillText("PC1", width / 2, height - 12);
    ctx.save();
    ctx.translate(15, height / 2);
    ctx.rotate(-Math.PI / 2);
    ctx.fillText("PC2", 0, 0);
    ctx.restore();
}
