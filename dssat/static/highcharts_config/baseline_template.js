// Global Highcharts accessibility and keyboard navigation defaults
if (typeof Highcharts !== 'undefined') {
    Highcharts.setOptions({
        accessibility: {
            enabled: true,
            keyboardNavigation: {
                enabled: true
            }
        },
        lang: {
            accessibility: {
                chartContainerLabel: 'Interactive chart. Use arrow keys to navigate data points.'
            }
        }
    });
}
