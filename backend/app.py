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
        url = f"{SEFARIA_API_URL}/{passage_ref}?commentary=1"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        commentaries = []
        seen_refs = set()

        for comment in data.get("commentary", []):
            if not comment:
                continue
                
            ref = comment.get("sourceRef", "")
            if ref in seen_refs:
                continue

            english_text = comment.get("text", "")
            if isinstance(english_text, list):
                english_text = " ".join(str(text) for text in english_text if text)

            commentator = (comment.get("ref", "").split(" on ")[0] or 
                         comment.get("sourceRef", "").split(" on ")[0] or 
                         "Unknown")

            english_text = (english_text.replace("<small>", "")
                                     .replace("</small>", "")
                                     .replace("<sup>", "")
                                     .replace("</sup>", "")
                                     .replace("<i>", "")
                                     .replace("</i>", "")
                                     .replace("<br>", " ")
                                     .replace("<b>", "")
                                     .replace("</b>", ""))
                
            if not english_text:
                continue
                
            seen_refs.add(ref)
            commentaries.append({
                "commentator": commentator,
                "text": english_text
            })

        return jsonify({"commentaries": commentaries})
        
    except requests.Timeout:
        return jsonify({"error": "Request timed out. Please try again."}), 504
    except Exception as e:
        print("Error in get_commentaries:", str(e))
        return jsonify({"error": f"Error fetching commentaries: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
