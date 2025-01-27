import os
import re
import requests
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__, static_folder="build", static_url_path="")
CORS(app)

# Initialize OpenAI model
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0.7
)

SEFARIA_API_URL = "https://www.sefaria.org/api/texts"
REQUEST_TIMEOUT = 30

# Hebrew book names mapping
HEBREW_BOOK_NAMES = {
    'בראשית': 'Genesis',
    'שמות': 'Exodus',
    'ויקרא': 'Leviticus',
    'במדבר': 'Numbers',
    'דברים': 'Deuteronomy'
    # Add more mappings as needed
}

def is_valid_reference(ref):
    """Check if the reference format is valid"""
    # Convert Hebrew reference to English if necessary
    ref = convert_hebrew_reference(ref)
    
    # Basic pattern for valid references:
    # Book name followed by optional chapter and verse
    # e.g., "Genesis", "Genesis 1", "Genesis 1:1"
    valid_pattern = r'^[A-Za-z\s]+(?:\s+\d+(?::\d+)?)?$'
    return bool(re.match(valid_pattern, ref))

def convert_hebrew_reference(ref):
    """Convert Hebrew reference to English"""
    # Split reference into book and chapter/verse
    parts = ref.strip().split(' ')
    if not parts:
        return ref
        
    book = parts[0]
    rest = ' '.join(parts[1:]) if len(parts) > 1 else ''
    
    # Convert book name if it's in Hebrew
    english_book = HEBREW_BOOK_NAMES.get(book, book)
    
    # If there's chapter/verse info, keep it; otherwise return just the book name
    return f"{english_book} {rest}".strip()

# Perspectives for commentary generation
PERSPECTIVE_PROMPTS = {
    "Philosophical": """
    Provide a deep philosophical analysis of this biblical passage. 
    Explore its underlying metaphysical, ethical, and existential implications. 
    Draw connections to broader philosophical traditions and concepts.
    
    Passage: {passage}
    
    Philosophical Analysis:""",
    
    "Theological": """
    Offer a traditional religious interpretation of this biblical passage. 
    Analyze its spiritual significance, theological meaning, and religious significance. 
    Incorporate traditional rabbinic and scriptural commentaries.
    
    Passage: {passage}
    
    Religious Commentary:""",
    
    "Secular": """
    Provide a contemporary, secular scholarly interpretation of this biblical passage. 
    Examine its historical context, literary structure, and potential societal implications. 
    Analyze the text from anthropological, linguistic, and historical perspectives.
    
    Passage: {passage}
    
    Secular Analysis:"""
}

@app.route("/")
def serve():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/<path:path>")
def serve_static(path):
    try:
        return send_from_directory(app.static_folder, path)
    except Exception:
        return send_from_directory(app.static_folder, "index.html")

@app.route("/api/get_passage", methods=["GET"])
def get_passage():
    passage_ref = request.args.get("passage")
    if not passage_ref:
        return jsonify({"error": "No passage reference provided"}), 400

    if not is_valid_reference(passage_ref):
        return jsonify({
            "error": "Please provide a valid reference format, such as 'Genesis 1:1', 'Genesis 1', or 'בראשית א:א'"
        }), 400
        
    # Convert Hebrew reference to English if necessary
    english_ref = convert_hebrew_reference(passage_ref)
    
    try:
        response = requests.get(f"{SEFARIA_API_URL}/{english_ref}", timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        return jsonify({
            "hebrew": data.get("he", ""),
            "english": data.get("text", "")
        })
    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/get_ai_commentary", methods=["GET"])
def get_ai_commentary():
    passage_ref = request.args.get("passage")
    perspective = request.args.get("perspective", "Secular")
    
    if not passage_ref:
        return jsonify({"error": "No passage reference provided"}), 400
    
    if perspective not in PERSPECTIVE_PROMPTS:
        return jsonify({"error": "Invalid perspective"}), 400
    
    try:
        # Convert Hebrew reference if necessary
        english_ref = convert_hebrew_reference(passage_ref)
        
        # First, get the passage
        response = requests.get(f"{SEFARIA_API_URL}/{english_ref}", timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        
        # Combine text if it's a list
        passage_text = data.get("text", "")
        if isinstance(passage_text, list):
            passage_text = " ".join(filter(None, passage_text))
        
        # Create prompt template
        prompt = PromptTemplate(
            input_variables=["passage"],
            template=PERSPECTIVE_PROMPTS[perspective]
        )
        
        # Generate AI commentary
        formatted_prompt = prompt.format(passage=passage_text)
        commentary = llm.predict(formatted_prompt)
        
        return jsonify({
            "commentary": commentary,
            "perspective": perspective
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
