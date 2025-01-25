import os
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from langchain_community.chat_models import ChatOpenAI
from dotenv import load_dotenv
import requests

load_dotenv()

app = Flask(__name__, static_folder="build", static_url_path="")
CORS(app)

llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

SEFARIA_API_URL = "https://www.sefaria.org/api/texts"
REQUEST_TIMEOUT = 30  # Increased timeout

@app.route("/")
def serve_frontend():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/<path:path>")
def serve_static_files(path):
    if os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return jsonify({"error": "Not Found"}), 404

@app.route("/api/get_passage", methods=["GET"])
def get_passage():
    passage_ref = request.args.get("passage")
    if not passage_ref:
        return jsonify({"error": "No passage reference provided"}), 400
    try:
        response = requests.get(f"{SEFARIA_API_URL}/{passage_ref}", timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        return jsonify({
            "hebrew": data.get("he", ""),
            "english": data.get("text", "")
        })
    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/get_commentaries", methods=["GET"])
def get_commentaries():
    passage_ref = request.args.get("passage")
    print(f"DEBUG: Received passage: {passage_ref}")
    
    if not passage_ref:
        return jsonify({"error": "No passage reference provided"}), 400
    
    try:
        # Format passage for API
        passage = passage_ref.replace(" ", "_")
        url = f"{SEFARIA_API_URL}/{passage}/he/commentary"
        print(f"DEBUG: Full URL: {url}")
        
        response = requests.get(url, timeout=15)
        print(f"DEBUG: Response status code: {response.status_code}")
        
        response.raise_for_status()
        
        data = response.json()
        print(f"DEBUG: Data keys: {data.keys()}")
        print(f"DEBUG: Commentary present: {'commentary' in data}")
        
        commentaries = []
        seen = set()
        
        # Limit to first 5 comments for performance
        if "commentary" in data:
            print(f"DEBUG: Total commentaries found: {len(data['commentary'])}")
            for comment in data["commentary"][:5]:
                text = comment.get("text", "")
                print(f"DEBUG: Individual comment text: {text}")
                
                # Rest of the existing code remains the same
                ...

        return jsonify({"commentaries": commentaries})
    except requests.Timeout:
        print("DEBUG: Request timed out")
        return jsonify({"error": "Request timed out"}), 504
    except Exception as e:
        print(f"DEBUG: Comprehensive error in get_commentaries: {str(e)}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
