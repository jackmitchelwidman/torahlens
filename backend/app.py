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
    if not passage_ref:
        return jsonify({"error": "No passage reference provided"}), 400
    
    try:
        # Normalize passage reference
        passage_ref = passage_ref.strip()
        
        # Try different formatting options
        formatted_passages = [
            passage_ref,  # Original
            passage_ref.replace(" ", "_"),  # Replace space with underscore
            passage_ref.replace(" ", ""),  # Remove spaces
        ]
        
        for formatted_passage in formatted_passages:
            # Try commentary endpoint
            commentary_url = f"{SEFARIA_API_URL}/{formatted_passage}/commentary"
            
            response = requests.get(commentary_url, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if commentary exists
                if "commentary" in data and data["commentary"]:
                    commentaries = []
                    for comment in data["commentary"]:
                        # Extract commentator name and text
                        ref_parts = comment.get("ref", "").split(" on ")
                        commentator = ref_parts[0] if len(ref_parts) > 0 else "Unknown"
                        
                        # Handle text (could be string or list)
                        text = comment.get("text", "")
                        if isinstance(text, list):
                            text = " ".join(filter(None, text))
                        
                        # Clean text
                        text = re.sub('<[^<]+?>', '', text)  # Remove HTML tags
                        text = text.strip()
                        
                        if text:  # Only add non-empty commentaries
                            commentaries.append({
                                "commentator": commentator,
                                "text": text
                            })
                    
                    return jsonify({"commentaries": commentaries})
        
        return jsonify({"commentaries": []})
    
    except Exception as e:
        print(f"Error fetching commentaries: {e}")
        return jsonify({"error": "Unable to fetch commentaries"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
