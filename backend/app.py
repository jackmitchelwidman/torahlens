from flask import Flask, jsonify, request, send_from_directory
import os
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import SystemMessage, HumanMessage

# Initialize the Flask app
app = Flask(__name__, static_folder='build', static_url_path='')

# Initialize LangChain ChatOpenAI with the chat model
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

    # Call the Sefaria API to fetch the actual passage (replace 'your_sefaria_api_key' with a valid key if needed)
    try:
        response = requests.get(f"https://www.sefaria.org/api/texts/{passage}")
        data = response.json()
        if "error" in data:
            return jsonify({'error': 'Invalid passage or passage not found.'}), 400
        hebrew_text = data.get("he", "Hebrew text not available")
        english_text = data.get("text", "English text not available")
        return jsonify({'hebrew': hebrew_text, 'english': english_text})
    except Exception as e:
        return jsonify({'error': f"Error fetching passage: {str(e)}"}), 500

@app.route('/api/get_commentaries', methods=['GET'])
def get_commentaries():
    """API endpoint to fetch commentaries and generate comparisons."""
    passage = request.args.get('passage')
    if not passage:
        return jsonify({'error': 'Passage is required.'}), 400

    try:
        # Call Sefaria API to fetch commentaries
        response = requests.get(f"https://www.sefaria.org/api/texts/{passage}?context=0&commentary=1")
        data = response.json()

        if "error" in data:
            return jsonify({'error': 'Invalid passage or no commentaries found.'}), 400

        commentaries = [
            {"commentator": c["commentator"], "text": c["he"] or c["text"]}
            for c in data.get("commentary", [])
        ]

        # Generate comparisons using ChatOpenAI
        messages = [
            SystemMessage(content="You are an assistant that helps compare Jewish Torah commentaries."),
            HumanMessage(content=f"Compare the following commentaries for the passage '{passage}': {commentaries}")
        ]

        chat_response = llm(messages)
        comparisons = chat_response.content  # Get the response from the chat model

        return jsonify({'commentaries': commentaries, 'comparisons': comparisons})

    except Exception as e:
        return jsonify({'error': f"Error fetching commentaries or generating comparisons: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)

