function translateText() {
    const arabicText = document.getElementById('arabicText').value;

    fetch('/translate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ text: arabicText })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('hieroglyphicsText').value = data.hieroglyphics;
    })
    .catch(error => console.error('Error:', error));
}

document.addEventListener('DOMContentLoaded', function() {
    var chartData = JSON.parse('{{ chart_data | tojson | safe }}');
    
    var chart = new ej.charts.Chart({
        primaryXAxis: {
            valueType: 'Category',
            title: 'الكلمات'
        },
        primaryYAxis: {
            title: 'عدد التكرارات'
        },
        series: [{
            type: 'Column',
            dataSource: chartData,
            xName: 'word',
            yName: 'count',
            name: 'عدد التكرارات'
        }],
        title: 'الكلمات الأكثر تكراراً'
    });
    
    chart.appendTo('#chart');
});

