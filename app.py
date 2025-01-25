from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)  # Enable CORS to allow React frontend requests

# Sefaria API base URL
SEFARIA_API_BASE_URL = "https://www.sefaria.org/api/texts/"

@app.route('/api/get_passage', methods=['GET'])
def get_passage():
    """Retrieve the Hebrew and English text for a specific Torah passage."""
    passage = request.args.get('passage')
    if not passage:
        return jsonify({'error': 'Passage is required.'}), 400

    sefaria_url = f"{SEFARIA_API_BASE_URL}{passage}"
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

@app.route('/api/get_commentaries', methods=['GET'])
def get_commentaries():
    """Retrieve major commentaries for a specific Torah passage."""
    passage = request.args.get('passage')
    if not passage:
        return jsonify({'error': 'Passage is required.'}), 400

    sefaria_url = f"{SEFARIA_API_BASE_URL}{passage}?commentary=1"
    try:
        response = requests.get(sefaria_url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Failed to connect to Sefaria API: {e}'}), 500

    data = response.json()
    commentaries = data.get('commentary', [])

    if not commentaries:
        return jsonify({'error': 'No commentaries found for this passage.'}), 404

    processed_commentaries = []
    for commentary in commentaries:
        # Extract the commentator's name
        collective_title = commentary.get('collectiveTitle', {})
        commentator = collective_title.get('en', 'Unknown')

        # Use the raw HTML from the text field
        text = ' '.join(commentary.get('text', []))  # Combine text lines
        processed_commentaries.append({
            'commentator': commentator,
            'text': text
        })

    return jsonify({'commentaries': processed_commentaries})


@app.route('/api/compare_commentaries', methods=['POST'])
def compare_commentaries():
    """
    Compare the major commentaries for a passage.
    This uses simple text processing for now, but can be extended with AI tools like LangChain.
    """
    data = request.json
    passage = data.get('passage')

    if not passage:
        return jsonify({'error': 'Passage is required.'}), 400

    # Fetch commentaries from the Sefaria API
    sefaria_url = f"{SEFARIA_API_BASE_URL}{passage}?commentary=1"
    response = requests.get(sefaria_url)

    if response.status_code == 200:
        data = response.json()

        # Extract and process commentaries
        commentaries = data.get('commentary', [])
        if not commentaries:
            return jsonify({'error': 'No commentaries found for this passage.'}), 404

        comparisons = []
        for commentary in commentaries:
            commentator = commentary.get('commentator', 'Unknown')
            text = ' '.join(commentary.get('text', []))  # Combine text lines
            comparisons.append({
                'commentator': commentator,
                'text': text
            })

        # Example comparison: Just list them for now (can extend with AI/analysis)
        return jsonify({'comparisons': comparisons})
    else:
        return jsonify({'error': 'Unable to fetch commentaries. Please check your input.'}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port)

