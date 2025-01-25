from flask import Flask, jsonify, request, send_from_directory
import os

# Initialize the Flask app
app = Flask(__name__, static_folder='../frontend/build', static_url_path='')

@app.route('/')
def index():
    """
    Serve the React app's main index.html file.
    """
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/get_passage', methods=['GET'])
def get_passage():
    """
    API endpoint to retrieve Hebrew and English text for a specific Torah passage.
    """
    passage = request.args.get('passage')
    if not passage:
        return jsonify({'error': 'Passage is required.'}), 400

    # Example implementation (replace with your actual logic)
    hebrew_text = f'Hebrew text for {passage}'
    english_text = f'English text for {passage}'

    return jsonify({'hebrew': hebrew_text, 'english': english_text})

@app.route('/api/get_commentaries', methods=['GET'])
def get_commentaries():
    """
    API endpoint to retrieve commentaries for a specific Torah passage.
    """
    passage = request.args.get('passage')
    if not passage:
        return jsonify({'error': 'Passage is required.'}), 400

    # Example implementation (replace with your actual logic)
    commentaries = [
        {
            'commentator': 'Rashi',
            'text': '<b>Commentary from Rashi:</b> This is an example of commentary.'
        },
        {
            'commentator': 'Ibn Ezra',
            'text': '<i>Commentary from Ibn Ezra:</i> This is another example.'
        }
    ]

    return jsonify({'commentaries': commentaries})

@app.errorhandler(404)
def not_found(e):
    """
    Catch-all route to serve React frontend files for any unknown route.
    """
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    # Define the port and start the Flask server
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)

