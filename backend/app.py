from flask import Flask, jsonify, request, send_from_directory
import os
from langchain_community.chat_models import ChatOpenAI
from langchain_community.prompts import SystemMessage, HumanMessage

# Initialize the Flask app
app = Flask(__name__, static_folder='build', static_url_path='')

# Initialize LangChain with your OpenAI API key
llm = ChatOpenAI(model="gpt-3.5-turbo", openai_api_key=os.getenv("OPENAI_API_KEY"))

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

    # Example implementation to fetch Hebrew and English texts for the passage
    try:
        hebrew_text = f"Hebrew text for {passage}"  # Replace with Sefaria API call
        english_text = f"English text for {passage}"  # Replace with Sefaria API call
        return jsonify({'hebrew': hebrew_text, 'english': english_text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/get_commentaries', methods=['GET'])
def get_commentaries():
    """API endpoint to fetch commentaries and generate comparisons."""
    passage = request.args.get('passage')
    if not passage:
        return jsonify({'error': 'Passage is required.'}), 400

    messages = [
        SystemMessage(content=f"Compare commentaries for passage: {passage}"),
        HumanMessage(content="What are the main differences?")
    ]

    try:
        response = llm(messages)
        return jsonify({'comparison': response.content})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

