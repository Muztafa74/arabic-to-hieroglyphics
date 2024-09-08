from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
from googletrans import Translator
import plotly.graph_objs as go
import plotly
from PIL import Image
import pytesseract
import os
import json
from collections import Counter
import logging

app = Flask(__name__)
translator = Translator()
TRANSLATED_WORDS_FILE = 'translated_words.json'



#pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# Set up logging
logging.basicConfig(level=logging.DEBUG)
# Ensure the 'temp' directory exists
os.makedirs('temp', exist_ok=True)
@app.route('/ocr', methods=['POST'])
def ocr():
    if 'image' not in request.files:
        app.logger.error('No image file provided')
        return jsonify({'error': 'No image file provided'}), 400

    file = request.files['image']
    if file.filename == '':
        app.logger.error('No selected file')
        return jsonify({'error': 'No selected file'}), 400

    if file:
        try:
            filename = secure_filename(file.filename)
            filepath = os.path.join('temp', filename)
            file.save(filepath)
            app.logger.info(f'File saved to {filepath}')

            image = Image.open(filepath)
            app.logger.info(f'Image opened: {image.format}, size: {image.size}, mode: {image.mode}')

            text = pytesseract.image_to_string(image, lang='ara+eng')
            app.logger.info(f'OCR completed. Extracted text length: {len(text)}')

            os.remove(filepath)
            app.logger.info(f'Temporary file removed: {filepath}')

            return jsonify({'text': text})
        except Exception as e:
            app.logger.error(f'Error during OCR process: {str(e)}', exc_info=True)
            if os.path.exists(filepath):
                os.remove(filepath)
                app.logger.info(f'Temporary file removed after error: {filepath}')
            return jsonify({'error': str(e)}), 500

# Load translated words from file
def load_translated_words():
    if os.path.exists(TRANSLATED_WORDS_FILE):
        with open(TRANSLATED_WORDS_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    return []

# Save translated words to file
def save_translated_words(words):
    with open(TRANSLATED_WORDS_FILE, 'w', encoding='utf-8') as file:
        json.dump(words, file, ensure_ascii=False)

# Create a bar chart with Plotly for word frequency
def create_interactive_word_frequency_chart(word_counts):
    words, counts = zip(*word_counts)

    # Customize the appearance of the bar chart
    data = [go.Bar(x=words, y=counts, marker=dict(color='#D4AF37'))]
    layout = go.Layout(
        xaxis={
            'title': 'الكلمات',
            'titlefont': {'size': 18, 'family': 'Amiri, serif'},
            'tickfont': {'size': 14, 'family': 'Amiri, serif'}
        },
        yaxis={
            'title': 'عدد التكرارات',
            'titlefont': {'size': 18, 'family': 'Amiri, serif'},
            'tickfont': {'size': 14, 'family': 'Amiri, serif'}
        },
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#D4AF37', family='Amiri, serif')
    )

    fig = go.Figure(data=data, layout=layout)
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON




# Load hieroglyphic dictionary from JSON file
with open('hieroglyphic_dict.json', 'r', encoding='utf-8') as f:
    hieroglyphic_dict = json.load(f)

# Translate English text to hieroglyphics
def translate_to_hieroglyphics(english_text):
    translated_text = ''.join(hieroglyphic_dict.get(char, char) for char in english_text.lower())
    return translated_text


# Dashboard route to display word frequency chart
total_users = 500
total_uploaded_images = 200

@app.route('/dashboard')
def dashboard():
    """Render the dashboard with metrics."""
    translated_words = load_translated_words()
    total_translated_words = len(translated_words)
    return render_template('dashboard.html', 
                           total_uploaded_images=total_uploaded_images, 
                           total_users=total_users, 
                           total_translated_words=total_translated_words)



# Home route
@app.route('/')
def index():
    return render_template('index.html')

# Route for translating Arabic text to English and hieroglyphics
@app.route('/translate', methods=['POST'])
def translate_text():
    data = request.json
    arabic_text = data.get('text')

    # Step 1: Translate Arabic to English
    translation = translator.translate(arabic_text, src='ar', dest='en')
    english_text = translation.text

    # Step 2: Translate English to Hieroglyphics
    hieroglyphic_text = translate_to_hieroglyphics(english_text)

    # Save the Arabic words
    translated_words = load_translated_words()
    translated_words.extend(arabic_text.split())
    save_translated_words(translated_words)

    return jsonify({'arabic': arabic_text,  'hieroglyphics': hieroglyphic_text})


@app.route('/api/chart-data')
def get_chart_data():
    """API endpoint to get chart data for word frequency."""
    translated_words = load_translated_words()
    word_counts = Counter(translated_words).most_common(10)  # Top 10 words
    
    chart_data = [
        {
            'word': word,
            'count': count
        }
        for word, count in word_counts
    ]
    
    return jsonify(chart_data)


# Run the Flask app
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
