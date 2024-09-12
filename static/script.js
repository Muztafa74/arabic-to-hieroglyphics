// Constants
const API_ENDPOINTS = {
  TRANSLATE: '/translate',
  OCR: '/ocr',
  CHART_DATA: '/api/chart-data'
};

const ELEMENTS = {
  arabicText: () => document.getElementById('arabicText'),
  hieroglyphicsText: () => document.getElementById('hieroglyphicsText'),
  imageUpload: () => document.getElementById('imageUpload'),
  translateButton: () => document.getElementById('translateButton'), // زر الترجمة
  chart: () => document.getElementById('chart')
};

// Event Listeners
document.addEventListener('DOMContentLoaded', initializeApp);

// Main Functions
function initializeApp() {
  setupTranslateButtonListener(); // تفعيل زر الترجمة
  setupImageUploadListener();
  setupChartIfOnDashboard();
}

function setupTranslateButtonListener() {
  const translateButton = ELEMENTS.translateButton();
  if (translateButton) {
    translateButton.addEventListener('click', translateText); // الترجمة عند الضغط
  }
}

function setupImageUploadListener() {
  const imageUpload = ELEMENTS.imageUpload();
  if (imageUpload) {
    imageUpload.addEventListener('change', handleImageUpload);
  }
}

function setupChartIfOnDashboard() {
  const chartElement = ELEMENTS.chart();
  if (chartElement) {
    fetchChartData();
  }
}

// API Functions
async function translateText() {
  const arabicText = ELEMENTS.arabicText().value;
  if (!arabicText) {
    ELEMENTS.hieroglyphicsText().value = '';
    return;
  }

  try {
    const response = await fetch(API_ENDPOINTS.TRANSLATE, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: arabicText })
    });
    const data = await response.json();
    ELEMENTS.hieroglyphicsText().value = data.hieroglyphics;
  } catch (error) {
    console.error('Translation error:', error);
    ELEMENTS.hieroglyphicsText().value = 'حدث خطأ أثناء الترجمة';
  }
}

async function handleImageUpload(event) {
  const file = event.target.files[0];
  if (!file) return;

  const formData = new FormData();
  formData.append('image', file);

  try {
    const response = await fetch(API_ENDPOINTS.OCR, {
      method: 'POST',
      body: formData
    });
    const data = await response.json();
    if (data.text) {
      ELEMENTS.arabicText().value = data.text;
      await translateText();
    } else {
      alert('لم يتم العثور على نص في الصورة');
    }
  } catch (error) {
    console.error('OCR error:', error);
    alert('حدث خطأ أثناء معالجة الصورة');
  }
}

async function fetchChartData() {
  try {
    const response = await fetch(API_ENDPOINTS.CHART_DATA);
    const data = await response.json();
    createChart(data);
  } catch (error) {
    console.error('Error fetching chart data:', error);
  }
}

// Chart Creation
function createChart(data) {
  const words = data.map(item => item.word);
  const counts = data.map(item => item.count);

  const chartData = [{
    x: words,
    y: counts,
    type: 'bar',
    marker: { color: '#D4AF37' }
  }];

  const layout = {
    title: 'الكلمات الأكثر تكراراً',
    xaxis: {
      title: 'الكلمات',
      titlefont: { size: 18, family: 'Amiri, serif' },
      tickfont: { size: 14, family: 'Amiri, serif' }
    },
    yaxis: {
      title: 'عدد التكرارات',
      titlefont: { size: 18, family: 'Amiri, serif' },
      tickfont: { size: 14, family: 'Amiri, serif' }
    },
    font: {
      family: 'Amiri, serif',
      color: '#D4AF37'
    },
    plot_bgcolor: 'rgba(0,0,0,0)',
    paper_bgcolor: 'rgba(0,0,0,0)'
  };

  Plotly.newPlot('chart', chartData, layout);
}
