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
