import os
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__, static_folder="../frontend/build", static_url_path="")
CORS(app)

# Set up LangChain Chat Model
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

# Sefaria API configuration
SEFARIA_API_URL = "https://www.sefaria.org/api/texts"

@app.route("/")
def serve_frontend():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/<path:path>")
def serve_static_files(path):
    if os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return jsonify({"error": "Not Found"}), 404

@app.route("/api/get_passage", methods=["GET"])
def get_passage():
    passage_ref = request.args.get("passage")
    if not passage_ref:
        return jsonify({"error": "No passage reference provided"}), 400

    try:
        # Call Sefaria API to get the text
        response = requests.get(f"{SEFARIA_API_URL}/{passage_ref}")
        data = response.json()

        # Extract Hebrew and English texts
        hebrew = data.get("he", "")
        english = data.get("text", "")

        return jsonify({
            "hebrew": hebrew,
            "english": english
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/get_commentaries", methods=["GET"])
def get_commentaries():
    passage_ref = request.args.get("passage")
    if not passage_ref:
        return jsonify({"error": "No passage reference provided"}), 400

    try:
        # Get commentaries from Sefaria API
        response = requests.get(f"{SEFARIA_API_URL}/{passage_ref}?commentary=1")
        data = response.json()
        
        # Extract commentary data
        commentaries = data.get("commentary", [])
        
        # Process and format commentaries
        formatted_commentaries = []
        for commentary in commentaries:
            formatted_commentaries.append({
                "commentator": commentary.get("he_commentator", ""),
                "text": commentary.get("he", ""),
                "english": commentary.get("text", "")
            })

        return jsonify({"commentaries": formatted_commentaries})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
