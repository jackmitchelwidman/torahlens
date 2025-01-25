from flask import Flask, jsonify, request, send_from_directory
import os
import requests

# Initialize the Flask app
app = Flask(__name__, static_folder='build', static_url_path='')

@app.route('/')
def serve_index():
    """Serve the React app's index.html file."""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/get_passage', methods=['GET'])
def get_passage():
    """API endpoint to fetch passage text."""
    passage = request.args.get('passage')
    if not passage:
        return jsonify({'error': 'Passage is required.'}), 400

    sefaria_url = f"https://www.sefaria.org/api/texts/{passage}"
    try:
        response = requests.get(sefaria_url)
        response.raise_for_status()
        data = response.json()
        hebrew_text = '<br>'.join(data.get('he', [])) or "No Hebrew text available."
        english_text = '<br>'.join(data.get('text', [])) or "No English text available."
        return jsonify({'hebrew': hebrew_text, 'english': english_text})
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f"Failed to fetch data from Sefaria API: {str(e)}"}), 500

@app.route('/api/get_commentaries', methods=['GET'])
def get_commentaries():
    """API endpoint to fetch commentaries."""
    passage = request.args.get('passage')
    if not passage:
        return jsonify({'error': 'Passage is required.'}), 400

    sefaria_url = f"https://www.sefaria.org/api/texts/{passage}?context=0&commentary=1"
    try:
        response = requests.get(sefaria_url)
        response.raise_for_status()
        data = response.json()
        commentaries = [
            {
                'commentator': commentary.get('collectiveTitle', {}).get('en', 'Unknown'),
                'text': ' '.join(commentary.get('text', [])) or "No commentary text available."
            }
            for commentary in data.get('commentary', [])
        ]
        return jsonify({'commentaries': commentaries})
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f"Failed to fetch data from Sefaria API: {str(e)}"}), 500


@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors by serving the React app."""
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    # Run the app in debug mode (only for local testing)
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

