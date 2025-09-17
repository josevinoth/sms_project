// Common chart configurations
const commonChartStyles = {
    bar_chart_1: {
        backgroundColor: 'rgba(54, 162, 235, 0.5)',
        borderColor: 'rgb(54, 162, 235)',
        borderWidth: 1,
        barThickness: 50,
        maxBarThickness: 50,
    },
    bar_chart_2: {
        backgroundColor: 'rgba(255, 99, 132, 0.5)',
        borderColor: 'rgb(255, 99, 132)',
        borderWidth: 1,
        barThickness: 50,
        maxBarThickness: 50,
    },
    legendStyle: {
        display: true,
        position: 'top',
        labels: {
            font: { size: 14, weight: 'bold' },
            color: '#000',
        },
    },
    yAxisStyle: {
        beginAtZero: true,
        title: {
            display: true,
            text: 'Number of Calls',
            font: { size: 16, weight: 'bold' },
            color: '#000',
        },
        ticks: {
            font: { size: 10, weight: 'bold' },
            color: '#000',
        },
    },
    xAxisStyle: {
        ticks: {
            font: { size: 12, weight: 'bold' },
            color: '#000',
        },
    },

};
function createDonutChart(ctx, labels, data, labelText, colors) {
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                label: labelText,
                data: data,
                backgroundColor: colors,
                borderWidth: 1
            }]
        },
        options: {
            plugins: {
                legend: {
                    display: true,
                    position: 'right',
                    labels: {
                        font: {
                            size: 14,
                            weight: 'bold'
                        },
                        color: '#000'
                    }
                },
                datalabels: {
                    color: '#000', // Text color
                    font: {
                        size: 12,
                        weight: 'bold'
                    },
                    formatter: (value) => `${value}%`
                }
            },
            responsive: true,
            maintainAspectRatio: true,
        },
        plugins: [ChartDataLabels]
    });
}

// Function to convert values to lakhs

function convertToLakhs(dataArray) {
    return dataArray.map(value => value / 100000);
}

// Function to generate profit/loss colors dynamically

function getProfitLossColors(dataArray) {
    return dataArray.map(value => value >= 0 ? 'rgba(218, 227, 243, 1)' : 'rgba(218, 227, 243, 1)');
}

function getProfitLossBorderColors(dataArray) {
    return dataArray.map(value => value >= 0 ? 'rgba(218, 227, 243, 1)' : 'rgba(218, 227, 243, 1)');
}

// Function to create a bar chart

function createBarChart(ctxId, labels, datasets, yAxisTitle = "Amount (Lakhs)") {
    const ctx = document.getElementById(ctxId).getContext('2d');
    return new Chart(ctx, {
        type: 'bar',
        data: { labels: labels, datasets: datasets },
        options: {
            responsive: true,
            plugins: {
                legend: { display: true, position: 'top' },
                datalabels: {
                    anchor: 'end',
                    align: 'top',
                    color: '#000',
                    backgroundColor: 'rgba(235, 233, 234, 0.8)',
                    borderRadius: 4,
                    padding: 4,
                    borderWidth: 1,
                    borderColor: '#000',
                    font: { size: 10, weight: 'bold' },
                    formatter: function(value) {
                        return value.toFixed(2) + ' L'; // Show values in Lakhs
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    suggestedMax: Math.max(...datasets.flatMap(dataset => dataset.data)) * 1.2,
                    title: { display: true, text: yAxisTitle }
                },
                x: { title: { display: true, text: 'Categories' } }
            }
        },
        plugins: [ChartDataLabels]
    });
}
