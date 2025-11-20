function roundData(arr) {
    return arr.map(val => Math.round(val));  // Rounding to integer
}

function loadChart() {

    // -----------------------------
    //  FIRST CHART – Long-Term Avg (Distinct Green Shades)
    // -----------------------------
    const categories = JSON.parse(document.getElementById('categories-data').textContent);
    const rainfed = JSON.parse(document.getElementById('rainfed-data').textContent);
    const irrigated = JSON.parse(document.getElementById('irrigated-data').textContent);

    Highcharts.chart('container', {
        chart: { type: 'column' },
        title: { text: 'Long-Term Average Yield' },
        xAxis: { categories },
        yAxis: {
            min: 0,
            title: { text: 'Average Yield (bu/ac)' }
        },
        tooltip: { valueSuffix: ' bu/ac' },
        plotOptions: {
            column: { dataLabels: { enabled: true }, groupPadding: 0.1 }
        },
        legend: { reversed: false },
        series: [
            {
                name: 'Rainfed',
                data: roundData(rainfed),  // Rounded to integer
                color: '#A3D39C'  // Lighter green for Rainfed
            },
            {
                name: 'Irrigated',
                data: roundData(irrigated),  // Rounded to integer
                color: '#388E3C'  // Darker green for Irrigated
            }
        ]
    });

    // ----------------------------------------
    //  SECOND CHART – Yearly Rainfed/Irrigated (Shades of Green)
    // ----------------------------------------
    const years = JSON.parse(document.getElementById('years').textContent);
    const rainfed_year = JSON.parse(document.getElementById('rainfed-data-year').textContent);
    const irrigated_year = JSON.parse(document.getElementById('irrigated-data-year').textContent);

    Highcharts.chart('container_by_year', {
        chart: { type: 'column' },
        title: { text: 'County Corn Yields by Year' },
        xAxis: { categories: years },
        yAxis: {
            min: 0,
            title: { text: 'Average Yield (bu/ac)' }
        },
        tooltip: { shared: true, valueSuffix: ' bu/ac' },
        plotOptions: {
            column: { dataLabels: { enabled: true }, groupPadding: 0.1 }
        },
        legend: { reversed: false },
        series: [
            {
                name: 'Rainfed',
                data: roundData(rainfed_year),  // Rounded to integer
                color: '#A5D6A7'  // Lighter green for Rainfed
            },
            {
                name: 'Irrigated',
                data: roundData(irrigated_year),  // Rounded to integer
                color: '#388E3C'  // Darker green for Irrigated
            }
        ]
    });

    // ----------------------------------------
    //  THIRD CHART – Stacked Means Only (Swap default blue/purple colors)
    // ----------------------------------------
    const precip_mean_year = JSON.parse(document.getElementById('precipitation-mean-year').textContent);
    const irrigated_mean_year = JSON.parse(document.getElementById('irrigated-mean-year').textContent);

    Highcharts.chart('stacked_year_container', {
        chart: { type: 'column' },
        title: { text: 'Irrigated and Precipitation' },
        xAxis: { categories: years },
        yAxis: {
            min: 0,
            title: { text: 'Total Water (in)' }
        },
        tooltip: { shared: true, valueSuffix: ' in' },
        plotOptions: {
            column: {
                stacking: 'normal',
                dataLabels: { enabled: true }
            }
        },
        legend: { reversed: false },

        // Swapping default blue and purple for Rainfed and Precipitation
        series: [
            {
                name: 'Precipitation Mean',  // Now using blue for Precipitation Mean
                data: roundData(precip_mean_year),  // Rounded to integer
                color: '#4A90E2' // Blue for Precipitation (bottom)
            },
            {
                name: 'Irrigated Mean',  // Now using purple for Rainfed Mean
                data: roundData(irrigated_mean_year),  // Rounded to integer
                color: '#9B59B6'  // Purple for Rainfed (top)
            }
        ]
    });

    // ----------------------------------------
    //  FOURTH CHART – Donut Chart of Means (Swap Blue and Purple Colors)
    // ----------------------------------------

    function average(arr) {
        if (!arr.length) return 0;
        return Math.round((arr.reduce((a, b) => a + b, 0) / arr.length));  // Round to integer
    }

    const overall_precip_mean = average(precip_mean_year);
    const overall_irrigated_mean = average(irrigated_mean_year);

    Highcharts.chart('donut_means_container', {
        chart: { type: 'pie' },
        title: { text: 'Irrigated and Precipitation (All Years)' },
        legend: {
            enabled: true,
            align: 'center',
            verticalAlign: 'bottom'
        },
        plotOptions: {
            pie: {
                innerSize: '50%',
                dataLabels: {
                    enabled: true,
                    format: '{point.name}: {point.y} in'
                }
            }
        },
        tooltip: { pointFormat: '<b>{point.y} in</b>' },
        series: [
            {
                name: 'Overall Mean',
                data: [
                    {
                        name: 'Precipitation Mean',
                        y: overall_precip_mean,
                        color: '#4A90E2' // Blue for Precipitation
                    },
                    {
                        name: 'Irrigated Mean',
                        y: overall_irrigated_mean,
                        color: '#9B59B6' // Purple for Rainfed
                    }
                ]
            }
        ]
    });

}

loadChart();

document.getElementById('submitBtn').addEventListener('click', function(event) {
    event.preventDefault();
    loadChart();
});
