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
                datalabels: { // Data Labels configuration
                    color: '#000', // Text color
                    font: {
                        size: 12,
                        weight: 'bold'
                    },
                    formatter: (value) => `${value}%`
                }
            },
            responsive: true,
            maintainAspectRatio: true // Prevent resizing issues
        },
        plugins: [ChartDataLabels] // Register the plugin
    });
}
