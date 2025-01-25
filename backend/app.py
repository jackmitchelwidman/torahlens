from flask import Flask, jsonify, request, send_from_directory
import os

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

    # Mock implementation
    hebrew_text = f"Hebrew text for {passage}"
    english_text = f"English text for {passage}"
    return jsonify({'hebrew': hebrew_text, 'english': english_text})

@app.route('/api/get_commentaries', methods=['GET'])
def get_commentaries():
    """API endpoint to fetch commentaries."""
    passage = request.args.get('passage')
    if not passage:
        return jsonify({'error': 'Passage is required.'}), 400

    # Mock implementation
    commentaries = [
        {'commentator': 'Rashi', 'text': 'Commentary from Rashi.'},
        {'commentator': 'Ibn Ezra', 'text': 'Commentary from Ibn Ezra.'}
    ]
    return jsonify({'commentaries': commentaries})

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors by serving the React app."""
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

