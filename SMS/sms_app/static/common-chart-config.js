// common-chart-config.js
const commonChartOptions = {
    responsive: true,
    plugins: {
        legend: {
            display: true,
            position: 'top',
            labels: {
                font: {
                    size: 14,
                    weight: 'bold'
                },
                color: '#000'
            }
        },
        datalabels: {
            anchor: 'end',
            align: 'top',
            formatter: (value) => value,
            font: {
                size: 12,
                weight: 'bold'
            },
            color: '#000',
            backgroundColor: 'rgba(235, 233, 234, 0.8)',
            borderRadius: 4,
            padding: 5,
            borderWidth: 1,
            borderColor: '#000'
        }
    },
    scales: {
        x: {
            ticks: {
                font: {
                    size: 12,
                    weight: 'bold'
                },
                color: '#000'
            }
        },
        y: {
            beginAtZero: true,
            title: {
                display: true,
                text: 'Number of Calls',
                font: {
                    size: 16,
                    weight: 'bold'
                },
                color: '#000'
            },
            ticks: {
                font: {
                    size: 10,
                    weight: 'bold'
                },
                color: '#000'
            }
        }
    }
};

// Export this configuration for reuse
export default commonChartOptions;
