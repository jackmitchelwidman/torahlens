from flask import Flask, request, jsonify
import os
import requests
from langchain_community.schema import SystemMessage, HumanMessage
from langchain_community.chat_models import ChatOpenAI

# Initialize Flask app
app = Flask(__name__)

# LLM setup
SEFARIA_API_URL = "https://www.sefaria.org/api/texts/"
llm = ChatOpenAI(model="gpt-3.5-turbo", openai_api_key=os.getenv("OPENAI_API_KEY"))

@app.route('/api/get_passage', methods=['GET'])
def get_passage():
    """API endpoint to fetch passage text."""
    passage = request.args.get('passage')
    if not passage:
        return jsonify({'error': 'Passage is required.'}), 400

    try:
        response = requests.get(f"{SEFARIA_API_URL}{passage}")
        if response.status_code != 200:
            return jsonify({'error': 'Failed to fetch data from Sefaria API.'}), 500

        data = response.json()
        return jsonify({
            'hebrew': data.get('he', ''),
            'english': data.get('text', '')
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/get_commentaries', methods=['GET'])
def get_commentaries():
    """API endpoint to fetch commentaries and generate comparisons."""
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

        # Combine commentaries for comparison
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

# Entry point for Gunicorn
if __name__ == "__main__":
    app.run(debug=True)

