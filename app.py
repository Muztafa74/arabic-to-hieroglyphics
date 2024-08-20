from flask import Flask, request, jsonify, render_template
from googletrans import Translator

app = Flask(__name__)
translator = Translator()

# Dictionary mapping English letters to Hieroglyphic symbols
hieroglyphic_dict = {
    "a": "𓄿", "b": "𓃀", "c": "𓎢", "d": "𓂧", "e": "𓅂",
    "f": "𓆑", "g": "𓎼", "h": "𓉔", "i": "𓇋", "j": "𓆓",
    "k": "𓈎", "l": "𓃭", "m": "𓅓", "n": "𓈖", "o": "𓅱",
    "p": "𓊪", "q": "𓎡", "r": "𓂋", "s": "𓋴", "t": "𓏏",
    "u": "𓅲", "v": "𓆯", "w": "𓅃", "x": "𓇨", "y": "𓇌",
    "z": "𓊃", " " : "𓐍"
}


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

    return jsonify({'arabic': arabic_text, 'english': english_text, 'hieroglyphics': hieroglyphic_text})

def translate_to_hieroglyphics(english_text):
    translated_text = ''.join(hieroglyphic_dict.get(char, char) for char in english_text.lower())
    return translated_text

if __name__ == '__main__':
    app.run(debug=True)
