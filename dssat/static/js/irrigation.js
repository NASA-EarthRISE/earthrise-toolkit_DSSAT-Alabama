function loadChart(){
            const categories = JSON.parse(document.getElementById('categories-data').textContent);
            const rainfed = JSON.parse(document.getElementById('rainfed-data').textContent);
            const irrigated = JSON.parse(document.getElementById('irrigated-data').textContent);

            Highcharts.chart('container', {
                chart: {
                    type: 'column'
                },
                title: {
                    text: 'Long-Term Average'
                },
                xAxis: {
                    categories: categories,
                    title: {
                        text: null
                    }
                },
                yAxis: {
                    min: 0,
                    title: {
                        text: 'Average Yield (bu/ac)',
                        align: 'high'
                    },
                    labels: {
                        overflow: 'justify'
                    }
                },
                tooltip: {
                    valueSuffix: ' bu/ac'
                },
                plotOptions: {
                    bar: {
                        dataLabels: {
                            enabled: true
                        },
                        groupPadding: 0.1
                    }
                },
                legend: {
                    reversed: false
                },
                series: [
                    {
                        name: 'Rainfed',
                        data: rainfed,
                    },
                    {
                        name: 'Irrigated',
                        data: irrigated,
                    }
                ]
            });
            const years = JSON.parse(document.getElementById('years').textContent);
             const rainfed_year = JSON.parse(document.getElementById('rainfed-data-year').textContent);
            const irrigated_year = JSON.parse(document.getElementById('irrigated-data-year').textContent);
            Highcharts.chart('container_by_year', {
                chart: {
                    type: 'column'
                },
                title: {
                    text: 'County Corn Yields'
                },
                xAxis: {
                    categories: years,
                    title: {
                        text: null
                    }
                },
                yAxis: {
                    min: 0,
                    title: {
                        text: 'Average Yield (bu/ac)',
                        align: 'high'
                    },
                    labels: {
                        overflow: 'justify'
                    }
                },
                tooltip: {
                    valueSuffix: ' bu/ac'
                },
                plotOptions: {
                    bar: {
                        dataLabels: {
                            enabled: true
                        },
                        groupPadding: 0.1
                    }
                },
                legend: {
                    reversed: false
                },
                series: [
                      {
                        name: 'Rainfed',
                        data: rainfed_year,
                    },
                    {
                        name: 'Irrigated',
                        data: irrigated_year,
                    }
                ]
            });
        }
        loadChart();
    document.getElementById('submitBtn').addEventListener('click', function(event) {
  event.preventDefault();
        loadChart();
    });