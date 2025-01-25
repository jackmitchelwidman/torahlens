from flask import Flask, jsonify, request, send_from_directory
import os
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
import requests

# Initialize the Flask app
app = Flask(__name__, static_folder='build', static_url_path='')

# Initialize LangChain with your OpenAI API key
llm = ChatOpenAI(model="gpt-3.5-turbo", openai_api_key=os.getenv("OPENAI_API_KEY"))

SEFARIA_API_URL = "https://www.sefaria.org/api/texts/"

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

    try:
        # Fetch Hebrew and English texts from Sefaria API
        response = requests.get(f"{SEFARIA_API_URL}{passage}")
        if response.status_code != 200:
            return jsonify({'error': 'Failed to fetch passage from Sefaria API.'}), 500

        data = response.json()
        hebrew_text = data.get('he', 'No Hebrew text available.')
        english_text = data.get('text', 'No English text available.')
        return jsonify({'hebrew': hebrew_text, 'english': english_text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/get_commentaries', methods=['GET'])
def get_commentaries():
    """API endpoint to fetch commentaries and generate comparisons."""
    passage = request.args.get('passage')
    if not passage:
        return jsonify({'error': 'Passage is required.'}), 400

    try:
        # Fetch commentaries for the passage
        response = requests.get(f"{SEFARIA_API_URL}{passage}/commentary")
        if response.status_code != 200:
            return jsonify({'error': 'Failed to fetch commentaries from Sefaria API.'}), 500

        data = response.json()
        commentaries = data.get('commentary', [])
        if not commentaries:
            return jsonify({'message': 'No commentaries available for this passage.'}), 200

        # Use LangChain to summarize or compare commentaries
        commentary_texts = "\n\n".join(c.get('text', '') for c in commentaries if 'text' in c)
        messages = [
            SystemMessage(content="Summarize and compare the following Torah commentaries."),
            HumanMessage(content=commentary_texts)
        ]
        comparison = llm(messages)

        return jsonify({'commentaries': commentaries, 'comparison': comparison.content})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

