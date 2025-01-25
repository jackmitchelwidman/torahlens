import os
from flask import Flask, jsonify, request, send_from_directory
from langchain_openai import ChatOpenAI  # Updated import for langchain
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__, static_folder="../frontend/build", static_url_path="")

# Set up LangChain Chat Model
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

# Sefaria API configuration
SEFARIA_API_URL = "https://www.sefaria.org/api/texts"

@app.route("/")
def serve_frontend():
    # Serve React's index.html
    return send_from_directory(app.static_folder, "index.html")

@app.route("/<path:path>")
def serve_static_files(path):
    # Serve other static files from the React build directory
    if os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return jsonify({"error": "Not Found"}), 404

@app.route("/api/get_passage", methods=["GET"])
def get_passage():
    # Fetch passage and its translations from Sefaria API
    passage_ref = request.args.get("passage")
    if not passage_ref:
        return jsonify({"error": "No passage reference provided"}), 400

    try:
        response = requests.get(f"{SEFARIA_API_URL}/{passage_ref}")
        response.raise_for_status()
        passage_data = response.json()
        return jsonify(passage_data)
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Failed to fetch passage", "details": str(e)}), 500

@app.route("/api/generate_commentary", methods=["POST"])
def generate_commentary():
    # Generate commentary using LangChain
    data = request.json
    passage_ref = data.get("passage")
    user_input = data.get("user_input")

    if not passage_ref or not user_input:
        return jsonify({"error": "Missing required parameters"}), 400

    try:
        prompt = f"Provide a detailed commentary on the Torah passage '{passage_ref}' based on the following user input: {user_input}"
        commentary = llm(prompt)
        return jsonify({"commentary": commentary})
    except Exception as e:
        return jsonify({"error": "Failed to generate commentary", "details": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

