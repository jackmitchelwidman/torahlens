from flask import Flask, jsonify, request, send_from_directory
import os
from langchain import OpenAI

# Initialize the Flask app
app = Flask(__name__, static_folder='build', static_url_path='')

# Initialize LangChain with your API key
llm = OpenAI(model="text-davinci-003", api_key=os.getenv("LANGCHAIN_API_KEY"))

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
    """API endpoint to fetch commentaries and generate comparisons."""
    passage = request.args.get('passage')
    if not passage:
        return jsonify({'error': 'Passage is required.'}), 400

    # Mock implementation of commentaries
    commentaries = [
        {'commentator': 'Rashi', 'text': 'Commentary from Rashi.'},
        {'commentator': 'Ibn Ezra', 'text': 'Commentary from Ibn Ezra.'},
        {'commentator': 'Ramban', 'text': 'Commentary from Ramban.'}
    ]

    comparisons = []
    for i in range(len(commentaries)):
        for j in range(i + 1, len(commentaries)):
            # Generate comparison for each pair of commentaries
            commentary_1 = commentaries[i]
            commentary_2 = commentaries[j]
            prompt = f"""
            Compare these two commentaries on {passage}:
            Commentary 1 ({commentary_1['commentator']}): {commentary_1['text']}
            Commentary 2 ({commentary_2['commentator']}): {commentary_2['text']}
            Highlight their similarities, differences, and unique insights.
            """
            try:
                response = llm(prompt)
                comparisons.append({
                    'commentator_1': commentary_1['commentator'],
                    'commentator_2': commentary_2['commentator'],
                    'comparison': response.strip()
                })
            except Exception as e:
                return jsonify({'error': 'Error generating comparison', 'details': str(e)}), 500

    return jsonify({'commentaries': commentaries, 'comparisons': comparisons})

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors by serving the React app."""
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(debug=True)

