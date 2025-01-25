from flask import Flask, send_from_directory, jsonify, request
import os
import requests
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage

# Initialize Flask app
app = Flask(__name__, static_folder='../frontend/build', static_url_path='')

# Set your Sefaria API URL and LangChain model
SEFARIA_API_URL = "https://www.sefaria.org/api/texts/"
llm = ChatOpenAI(temperature=0)

# Serve React frontend
@app.route('/')
def serve_frontend():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static_files(path):
    if os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return jsonify({'error': 'Not Found'}), 404

# API endpoint to fetch a Torah passage
@app.route('/api/get_passage', methods=['GET'])
def get_passage():
    passage = request.args.get('passage')
    if not passage:
        return jsonify({'error': 'Passage is required.'}), 400

    try:
        response = requests.get(f"{SEFARIA_API_URL}{passage}?context=0")
        if response.status_code != 200:
            return jsonify({'error': 'Failed to fetch data from Sefaria API.'}), 500

        data = response.json()
        return jsonify({
            'hebrew': data.get('he', ''),
            'english': data.get('text', '')
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API endpoint to fetch commentaries and generate comparisons
@app.route('/api/get_commentaries', methods=['GET'])
def get_commentaries():
    passage = request.args.get('passage')
    if not passage:
        return jsonify({'error': 'Passage is required.'}), 400

    try:
        response = requests.get(f"{SEFARIA_API_URL}{passage}?with=links")
        if response.status_code != 200:
            return jsonify({'error': 'Failed to fetch data from Sefaria API.'}), 500

        data = response.json()
        links = data.get('links', [])
        commentaries = [
            link for link in links if link.get('category') == 'Commentary' and 'source_text' in link
        ]

        if not commentaries:
            return jsonify({'message': 'No commentaries available for this passage.'}), 200

        # Prepare text for LangChain
        commentary_texts = "\n\n".join(
            f"{c.get('source_title')}: {c.get('source_text')}" for c in commentaries
        )
        messages = [
            SystemMessage(content="Compare and summarize the following Torah commentaries."),
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

# Run the app locally
if __name__ == '__main__':
    app.run(debug=True)

