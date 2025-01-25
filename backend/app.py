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
        # Fetch data from Sefaria API
        response = requests.get(f"{SEFARIA_API_URL}{passage}?with=links")
        if response.status_code != 200:
            return jsonify({'error': 'Failed to fetch data from Sefaria API.'}), 500

        data = response.json()
        links = data.get('links', [])
        commentaries = [
            link for link in links if link.get('category') == 'Commentary' and 'text' in link
        ]

        if not commentaries:
            return jsonify({'message': 'No commentaries available for this passage.'}), 200

        # Process commentaries and generate a comparison
        commentary_texts = "\n\n".join(
            f"{c.get('source_text')} (by {c.get('source_title')})"
            for c in commentaries
            if 'source_text' in c and 'source_title' in c
        )

        # Use LangChain to generate a comparison
        messages = [
            SystemMessage(content="Summarize and compare the following Torah commentaries:"),
            HumanMessage(content=commentary_texts)
        ]
        comparison = llm(messages)

        return jsonify({
            'commentaries': [
                {'source': c.get('source_title'), 'text': c.get('source_text')}
                for c in commentaries
            ],
            'comparison': comparison.content
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

