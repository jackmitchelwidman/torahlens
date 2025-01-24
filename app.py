from flask import Flask, request, jsonify, send_from_directory
import requests
import os

app = Flask(__name__)

# Serve index.html at the root endpoint
@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/get_passage', methods=['GET'])
def get_passage():
    passage = request.args.get('passage')
    sefaria_url = f"https://www.sefaria.org/api/texts/{passage}"
    response = requests.get(sefaria_url)
    if response.status_code == 200:
        data = response.json()
        hebrew = ''.join(data.get('he', []))  # Combine Hebrew lines
        english = ' '.join(data.get('text', []))  # Combine English lines
        return jsonify({'hebrew': hebrew, 'english': english})
    else:
        return jsonify({'error': 'Unable to fetch passage. Please check your input.'}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

