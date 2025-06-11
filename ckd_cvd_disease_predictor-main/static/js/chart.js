function renderRiskChart([lowRiskPercent, highRiskPercent]) {
    const ctx = document.getElementById("riskChart").getContext("2d");

    if (window.riskChartInstance) {
        window.riskChartInstance.destroy();
    }

    window.riskChartInstance = new Chart(ctx, {
        type: "doughnut",
        data: {
            labels: ["Low Risk", "High Risk"],
            datasets: [{
                data: [lowRiskPercent, highRiskPercent],
                backgroundColor: ["#4caf50", "#f44336"],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: "bottom" },
                title: {
                    display: true,
                    text: "Risk Prediction Chart"
                }
            }
        }
    });
}
window.renderRiskChart = renderRiskChart;
