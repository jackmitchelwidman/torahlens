from flask import Flask, request, jsonify, send_file
import requests
import os

app = Flask(__name__)

@app.route('/')
def home():
    return send_file('index.html')  # Serve the index.html file

@app.route('/get_passage', methods=['GET'])
def get_passage():
    passage = request.args.get('passage')
    sefaria_url = f"https://www.sefaria.org/api/texts/{passage}"
    response = requests.get(sefaria_url)

    if response.status_code == 200:
        data = response.json()

        # Get Hebrew and English text arrays
        hebrew_text = data.get('he', [])
        english_text = data.get('text', [])

        # Ensure the text arrays are joined correctly
        hebrew = '<br>'.join(hebrew_text) if hebrew_text else 'No Hebrew text found.'
        english = '<br>'.join(english_text) if english_text else 'No English text found.'

        return jsonify({'hebrew': hebrew, 'english': english})
    else:
        return jsonify({'error': 'Unable to fetch passage. Please check your input.'}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

