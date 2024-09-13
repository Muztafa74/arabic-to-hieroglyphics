from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
from googletrans import Translator
import plotly.graph_objs as go
from flask_cors import CORS
import plotly
from PIL import Image
import pytesseract
import plotly.express as px
import traceback
from collections import Counter
import logging
import os
import json


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["https://kemet-translator.netlify.app", "http://localhost:3000"]}})
translator = Translator()
TRANSLATED_WORDS_FILE = 'translated_words.json'
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Step 1: Define allowed image extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Function to check if the uploaded file is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_file():
    # Step 2: Check if a file is present in the request
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    # Step 3: Validate that the file has a name
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Step 4: Validate the file extension
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join('temp', filename))
        return jsonify({'success': 'File successfully uploaded'}), 200
    else:
        return jsonify({'error': 'Invalid file type. Only image files are allowed.'}), 400

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

            # Check if file is a valid image
            try:
                with Image.open(filepath) as img:
                    app.logger.info(f'Image opened: {img.format}, size: {img.size}, mode: {img.mode}')
                    text = pytesseract.image_to_string(img, lang='ara+eng')
                    app.logger.info(f'OCR completed. Extracted text length: {len(text)}')
            except Exception as e:
                app.logger.error(f'Error opening image file: {str(e)}')
                return jsonify({'error': 'Error processing image file'}), 500

            os.remove(filepath)
            app.logger.info(f'Temporary file removed: {filepath}')

            return jsonify({'text': text})
        except Exception as e:
            app.logger.error(f'Error during OCR process: {str(e)}', exc_info=True)
            if os.path.exists(filepath):
                os.remove(filepath)
                app.logger.info(f'Temporary file removed after error: {filepath}')
            return jsonify({'error': str(e)}), 500



# Load hieroglyphic dictionary from JSON file
# Save translated words with their counts
def save_translated_words(words):
    if not os.path.exists(TRANSLATED_WORDS_FILE):
        with open(TRANSLATED_WORDS_FILE, 'w', encoding='utf-8') as file:
            json.dump({}, file, ensure_ascii=False)
    
    with open(TRANSLATED_WORDS_FILE, 'r+', encoding='utf-8') as file:
        existing_words = json.load(file)
        word_counter = Counter(existing_words)
        
        # Update the counts
        word_counter.update(words)
        
        file.seek(0)
        json.dump(dict(word_counter), file, ensure_ascii=False)
        file.truncate()


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
DICT_PATH = os.path.join(os.path.dirname(__file__), 'hieroglyphic_dict.json')
with open(DICT_PATH, 'r', encoding='utf-8') as f:
    hieroglyphic_dict = json.load(f)

# Translate English text to hieroglyphics
def translate_to_hieroglyphics(english_text):
    return ''.join(hieroglyphic_dict.get(char, char) for char in english_text.lower())

# Dashboard route to display word frequency chart
total_users = 500
total_uploaded_images = 200


@app.route('/translated-word-count', methods=['GET'])
def translated_word_count():
    translated_words = load_translated_words()
    word_counts = Counter(translated_words).most_common(10)
    
    word_list = [{'label': word, 'value': count} for word, count in word_counts]
    return jsonify(word_list)

@app.route('/total-translated-words', methods=['GET'])
def get_total_translated_words():
    """Retrieve the total number of translated words."""
    translated_words = load_translated_words()
    
    # حساب إجمالي الكلمات المترجمة
    total_words = sum(translated_words.values())
    
    return jsonify({'total_translated_words': total_words})

@app.route('/dashboard')
def dashboard():
    """Render the dashboard with metrics."""
    translated_words = load_translated_words()
    total_translated_words = len(translated_words)
    return render_template('dashboard.html', 
                           total_uploaded_images=total_uploaded_images, 
                           total_users=total_users, 
                           total_translated_words=total_translated_words)

def load_translated_words():
    try:
        with open(TRANSLATED_WORDS_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}
    

@app.route('/translate', methods=['POST'])
def translate_text():
    try:
        # Validate the request payload
        data = request.get_json()
        if not data or 'text' not in data:
            app.logger.error("No text provided in the request")
            return jsonify({'error': 'No text provided'}), 400
        
        arabic_text = data['text'].strip()
        app.logger.info(f"Received text for translation: {arabic_text}")

        # Translate Arabic to English
        translation = translator.translate(arabic_text, src='ar', dest='en')
        english_text = translation.text.strip()
        app.logger.info(f"Translated Arabic to English: {english_text}")

        # Translate English to Hieroglyphics
        hieroglyphic_text = translate_to_hieroglyphics(english_text)
        app.logger.info(f"Translated English to Hieroglyphics: {hieroglyphic_text}")

        # Save the translated words
        translated_words = arabic_text.split()
        save_translated_words(translated_words)
        app.logger.info("Arabic words saved successfully")

        # Return the translation result
        return jsonify({
            'arabic': arabic_text,
            'hieroglyphics': hieroglyphic_text
        })
    
    except json.JSONDecodeError as e:
        app.logger.error(f"Invalid JSON payload: {str(e)}")
        return jsonify({'error': 'Invalid JSON format'}), 400

    except AttributeError as e:
        app.logger.error(f"Translation service error: {str(e)}")
        return jsonify({'error': 'Translation service error'}), 500

    except Exception as e:
        app.logger.error(f"Unhandled exception: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/')
def home():
    return render_template('index.html')
    


if __name__ == '__main__':
    app.run(debug=True)
