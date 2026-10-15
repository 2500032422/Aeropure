// Smooth scroll to forecast section
function scrollToForecast() {
    document.getElementById("forecast").scrollIntoView({
        behavior: "smooth"
    });
}


// Sample forecast data
const hours = [
    "Now",
    "1 PM",
    "2 PM",
    "3 PM",
    "4 PM",
    "5 PM",
    "6 PM",
    "7 PM",
    "8 PM",
    "9 PM",
    "10 PM",
    "11 PM"
];

const values = [
    86, 82, 79, 75, 72, 78,
    85, 94, 101, 108, 112, 118
];


// Create chart
const ctx = document
    .getElementById("forecastChart")
    .getContext("2d");

const forecastChart = new Chart(ctx, {

    type: "line",

    data: {

        labels: hours,

        datasets: [{
            label: "PM2.5 (µg/m³)",

            data: values,

            borderWidth: 3,

            tension: 0.4,

            fill: true
        }]

    },

    options: {

        responsive: true,

        plugins: {
            legend: {
                display: false
            }
        },

        scales: {

            y: {
                beginAtZero: true,

                title: {
                    display: true,
                    text: "PM2.5 (µg/m³)"
                }
            },

            x: {
                title: {
                    display: true,
                    text: "Time"
                }
            }

        }

    }

});


// Generate forecast
function generateForecast() {

    const station =
        document.getElementById("station").value;

    const period =
        document.getElementById("period").value;

    document.getElementById("selectedStation").innerText =
        station + " • " + period;


    // Temporary demo prediction
    const prediction =
        Math.floor(70 + Math.random() * 60);

    document.getElementById("predictionValue").innerText =
        prediction;


    document.getElementById("currentPM").innerText =
        prediction;


    // Generate new sample values
    const newValues = values.map(() =>
        Math.floor(60 + Math.random() * 80)
    );


    forecastChart.data.datasets[0].data =
        newValues;

    forecastChart.update();

}