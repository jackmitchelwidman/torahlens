import os
import re
import requests
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from langchain_community.chat_models import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder="build", static_url_path="")
CORS(app)

llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

SEFARIA_API_URL = "https://www.sefaria.org/api/texts"
REQUEST_TIMEOUT = 30

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
    
    if not passage_ref:
        return jsonify({"error": "No passage reference provided"}), 400
    
    passage_variations = [
        passage_ref,
        passage_ref.replace(" ", "_"),
        passage_ref.replace(" ", "")
    ]
    
    for passage in passage_variations:
        try:
            url = f"{SEFARIA_API_URL}/{passage}/commentary"
            print(f"Attempting URL: {url}")
            
            response = requests.get(url, timeout=REQUEST_TIMEOUT)
            
            if response.status_code == 200:
                data = response.json()
                print("Full Response:", data)
                print("Keys:", data.keys())
                
                commentaries = []
                if "commentary" in data and data["commentary"]:
                    for comment in data["commentary"]:
                        commentator = comment.get("ref", "").split(" on ")[0] or "Unknown"
                        
                        text = comment.get("text", "")
                        if isinstance(text, list):
                            text = " ".join(filter(None, text))
                        
                        text = re.sub('<[^<]+?>', '', text)
                        text = text.strip()
                        
                        if text:
                            commentaries.append({
                                "commentator": commentator,
                                "text": text
                            })
                
                if commentaries:
                    return jsonify({"commentaries": commentaries})
        
        except Exception as e:
            print(f"Error fetching commentaries for {passage}: {e}")
    
    return jsonify({"commentaries": []})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
