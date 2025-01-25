from flask import Flask, jsonify, request, send_from_directory
import os
from langchain_openai import OpenAI

# Initialize the Flask app
app = Flask(__name__, static_folder='build', static_url_path='')

# Initialize LangChain with your API key
llm = OpenAI(model="text-davinci-003", openai_api_key=os.getenv("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"))

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
        # Generate passage details using LangChain
        query = f"Provide the Hebrew and English text for the passage {passage}."
        response = llm.predict(query)
        # Assuming the response contains JSON-like structure
        result = response.split("||")
        hebrew_text = result[0].strip()
        english_text = result[1].strip()

        return jsonify({'hebrew': hebrew_text, 'english': english_text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/get_commentaries', methods=['GET'])
def get_commentaries():
    """API endpoint to fetch commentaries."""
    passage = request.args.get('passage')
    if not passage:
        return jsonify({'error': 'Passage is required.'}), 400

    try:
        # Generate commentaries using LangChain
        query = f"Provide key Jewish commentaries for the passage {passage}."
        response = llm.predict(query)
        # Process the response to extract individual commentaries
        commentaries = []
        for line in response.split("\n"):
            if ":" in line:
                commentator, text = line.split(":", 1)
                commentaries.append({'commentator': commentator.strip(), 'text': text.strip()})

        return jsonify({'commentaries': commentaries})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/get_comparisons', methods=['GET'])
def get_comparisons():
    """API endpoint to fetch natural language comparisons between commentaries."""
    passage = request.args.get('passage')
    if not passage:
        return jsonify({'error': 'Passage is required.'}), 400

    try:
        # Fetch commentaries first
        query = f"Provide key Jewish commentaries for the passage {passage}."
        commentary_response = llm.predict(query)
        commentaries = []
        for line in commentary_response.split("\n"):
            if ":" in line:
                commentator, text = line.split(":", 1)
                commentaries.append({'commentator': commentator.strip(), 'text': text.strip()})

        # Generate comparisons between the commentaries
        comparison_query = f"Compare the following commentaries for the passage {passage}:\n"
        for commentary in commentaries:
            comparison_query += f"{commentary['commentator']}: {commentary['text']}\n"
        comparison_query += "Provide a detailed comparison."

        comparison_response = llm.predict(comparison_query)
        comparisons = comparison_response.strip()

        return jsonify({
            'commentaries': commentaries,
            'comparisons': comparisons
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Start the Flask app
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

