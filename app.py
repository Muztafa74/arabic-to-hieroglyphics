from flask import Flask, request, jsonify, render_template, url_for
from googletrans import Translator
import plotly.graph_objs as go
import plotly
from PIL import Image
import pytesseract
import matplotlib.pyplot as plt
import plotly.express as px
import base64
from collections import Counter
import os
import io
import json

app = Flask(__name__)
translator = Translator()
TRANSLATED_WORDS_FILE = 'translated_words.json'


def load_translated_words():
    if os.path.exists(TRANSLATED_WORDS_FILE):
        with open(TRANSLATED_WORDS_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    return []

def create_interactive_word_frequency_chart(word_counts):
    words, counts = zip(*word_counts)

    # Create a bar chart using Plotly with dark brown color
    data = [go.Bar(x=words, y=counts, marker=dict(color='#D4AF37'))]
    
    layout = go.Layout(

        xaxis={
            'title': 'الكلمات',
            'titlefont': {'size': 18, 'family': 'Amiri, serif'},  # Change x-axis title font family
            'tickfont': {'size': 14, 'family': 'Amiri, serif'}    # Change x-axis tick font family
        },
        yaxis={
            'title': 'عدد التكرارات',
            'titlefont': {'size': 18, 'family': 'Amiri, serif'},  # Change y-axis title font family
            'tickfont': {'size': 14, 'family': 'Amiri, serif'}    # Change y-axis tick font family
        },
        plot_bgcolor='rgba(0,0,0,0)',  # Set the plot background to transparent
        paper_bgcolor='rgba(0,0,0,0)',  # Set the entire background to transparent
        font=dict(color='#D4AF37', family='Amiri, serif')  # Change overall font family
    )
    
    fig = go.Figure(data=data, layout=layout)

    # Convert the plotly figure to JSON for rendering in the template
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON

   

def save_translated_words(words):
    with open(TRANSLATED_WORDS_FILE, 'w', encoding='utf-8') as file:
        json.dump(words, file, ensure_ascii=False)


hieroglyphic_dict = {
    "a": "𓄿", "b": "𓃀", "c": "𓎢", "d": "𓂧", "e": "𓅂",
    "f": "𓆑", "g": "𓎼", "h": "𓉔", "i": "𓇋", "j": "𓆓",
    "k": "𓈎", "l": "𓃭", "m": "𓅓", "n": "𓈖", "o": "𓅱",
    "p": "𓊪", "q": "𓎡", "r": "𓂋", "s": "𓋴", "t": "𓏏",
    "u": "𓅲", "v": "𓆯", "w": "𓅃", "x": "𓇨", "y": "𓇌",
    "z": "𓊃", " ": "  "
}
@app.route('/dashboard')
def dashboard():
    translated_words = load_translated_words()
    word_counts = Counter(translated_words).most_common(10)  # Get the top 10 most common words

    # Create the interactive chart
    interactive_chart = create_interactive_word_frequency_chart(word_counts)

    return render_template('dashboard.html', interactive_chart=interactive_chart, most_common_words=word_counts)

def translate_to_hieroglyphics(english_text):
    translated_text = ''.join(hieroglyphic_dict.get(char, char) for char in english_text.lower())
    return translated_text


def create_word_frequency_chart(words):
    word_counts = Counter(words)
    most_common_words = word_counts.most_common(10)
    words, counts = zip(*most_common_words)
    
    fig = px.bar(x=words, y=counts, labels={'x': 'Words', 'y': 'Counts'}, title='Top 10 Most Frequent Words')
    
    # Convert plot to a base64 image for embedding in HTML
    buffer = io.BytesIO()
    fig.write_image(buffer, format='png')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    return image_base64


@app.route('/')
def index():
    return render_template('index.html')


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

    return jsonify({'arabic': arabic_text, 'english': english_text, 'hieroglyphics': hieroglyphic_text})



@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if not os.path.exists("uploads"):
        os.makedirs("uploads")

    if request.method == 'POST':
        file = request.files['image']
        if file:
            image_path = os.path.join("uploads", file.filename)
            file.save(image_path)

            # Use OCR to extract text from the image
            extracted_text = pytesseract.image_to_string(Image.open(image_path), lang='ara')
            print(f"Extracted text: {extracted_text}")

            # Translate the extracted text to English (you can actually use translation here)
            english_text = extracted_text  # Replace this with actual translation if needed
            hieroglyphics_text = translate_to_hieroglyphics(english_text)

            return render_template('upload.html', extracted_text=extracted_text, hieroglyphics_text=hieroglyphics_text)
    return render_template('upload.html', extracted_text="", hieroglyphics_text="")


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


if __name__ == '__main__':
    app.run(debug=True)
