import os
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from langchain_community.chat_models import ChatOpenAI
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__, static_folder="build", static_url_path="")
CORS(app)

# Set up LangChain Chat Model
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

# Sefaria API configuration
SEFARIA_API_URL = "https://www.sefaria.org/api/texts"
REQUEST_TIMEOUT = 10  # seconds

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
        response = requests.get(f"{SEFARIA_API_URL}/{passage_ref}", timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        hebrew = data.get("he", "")
        english = data.get("text", "")
        return jsonify({"hebrew": hebrew, "english": english})
    except requests.Timeout:
        return jsonify({"error": "Request to Sefaria API timed out"}), 504
    except requests.RequestException as e:
        return jsonify({"error": f"Error fetching passage: {str(e)}"}), 500

       @app.route("/api/get_commentaries", methods=["GET"])
def get_commentaries():
    passage_ref = request.args.get("passage")
    if not passage_ref:
        return jsonify({"error": "No passage reference provided"}), 400

    try:
        # Request English text and commentaries
        url = f"https://www.sefaria.org/api/texts/{passage_ref}?commentary=1&context=0&language=en"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if not data:
            return jsonify({"commentaries": [], "error": "No commentaries found"}), 200

        commentaries = []
        seen_commentators = set()  # Track unique commentators
        
        for comm in data.get("commentary", []):
            # Get commentator name, preferring English
            commentator = comm.get("commentator", "Unknown Commentator")
            english_text = comm.get("text", "")
            
            # Skip empty commentaries or duplicates
            if not english_text or (commentator, english_text) in seen_commentators:
                continue
                
            commentaries.append({
                "commentator": commentator,
                "english": english_text,
                "sourceRef": comm.get("ref", "")
            })
            seen_commentators.add((commentator, english_text))

        return jsonify({"commentaries": commentaries})
        
    except requests.RequestException as e:
        print("Error fetching commentaries:", str(e))
        return jsonify({"error": f"Error fetching commentaries: {str(e)}"}), 500 
    except requests.RequestException as e:
        print("Error fetching commentaries:", str(e))
        return jsonify({"error": f"Error fetching commentaries: {str(e)}"}), 500
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
