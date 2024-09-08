let typingTimer;
const doneTypingInterval = 500; // ms

document.addEventListener('DOMContentLoaded', function() {
    const arabicText = document.getElementById('arabicText');
    const hieroglyphicsText = document.getElementById('hieroglyphicsText');
    const imageUpload = document.getElementById('imageUpload');

    if (arabicText && hieroglyphicsText) {
        arabicText.addEventListener('input', function() {
            clearTimeout(typingTimer);
            if (arabicText.value) {
                typingTimer = setTimeout(translateText, doneTypingInterval);
            } else {
                hieroglyphicsText.value = '';
            }
        });
    }

    if (imageUpload) {
        imageUpload.addEventListener('change', handleImageUpload);
    }

    // Set up chart if on the dashboard page
    const chartElement = document.getElementById('chart');
    if (chartElement) {
        const chartData = JSON.parse(chartElement.getAttribute('data-chart'));
        createChart(chartData);
    }
});

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
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('hieroglyphicsText').value = 'حدث خطأ أثناء الترجمة';
    });
}

function handleImageUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('image', file);

    fetch('/ocr', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.text) {
            document.getElementById('arabicText').value = data.text;
            translateText(); // Automatically translate the extracted text
        } else {
            alert('لم يتم العثور على نص في الصورة');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('حدث خطأ أثناء معالجة الصورة');
    });
}


function createChart(chartData) {
    const words = chartData.map(item => item.word);
    const counts = chartData.map(item => item.count);

    const data = [{
        x: words,
        y: counts,
        type: 'bar',
        marker: {
            color: '#D4AF37'
        }
    }];

    const layout = {
        title: 'الكلمات الأكثر تكراراً',
        xaxis: {
            title: 'الكلمات',
            titlefont: {
                size: 18,
                family: 'Amiri, serif'
            },
            tickfont: {
                size: 14,
                family: 'Amiri, serif'
            }
        },
        yaxis: {
            title: 'عدد التكرارات',
            titlefont: {
                size: 18,
                family: 'Amiri, serif'
            },
            tickfont: {
                size: 14,
                family: 'Amiri, serif'
            }
        },
        font: {
            family: 'Amiri, serif',
            color: '#D4AF37'
        },
        plot_bgcolor: 'rgba(0,0,0,0)',
        paper_bgcolor: 'rgba(0,0,0,0)'
    };

    Plotly.newPlot('chart', data, layout);
}