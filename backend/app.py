import os
import re
import requests
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from urllib.parse import unquote
from dotenv import load_dotenv

print("=== Starting Flask App with Scientific Debugging ===")

load_dotenv()

app = Flask(__name__, static_folder="build", static_url_path="")
CORS(app)

SEFARIA_API_URL = "https://www.sefaria.org/api/texts"
REQUEST_TIMEOUT = 30

# Hebrew book names mapping
HEBREW_BOOK_NAMES = {
    'בראשית': 'Genesis',
    'שמות': 'Exodus',
    'ויקרא': 'Leviticus',
    'במדבר': 'Numbers',
    'דברים': 'Deuteronomy'
}

def is_valid_reference(ref):
    """Check if the reference format is valid."""
    ref = convert_hebrew_reference(ref)
    valid_pattern = r'^[A-Za-z\s]+(?:\s+\d+(?::\d+)?)?$'
    return bool(re.match(valid_pattern, ref))

def convert_hebrew_reference(ref):
    """Convert Hebrew reference to English."""
    parts = ref.strip().split(' ')
    if not parts:
        return ref
    book = parts[0]
    rest = ' '.join(parts[1:]) if len(parts) > 1 else ''
    english_book = HEBREW_BOOK_NAMES.get(book, book)
    return f"{english_book} {rest}".strip()

FIXED_PROMPTS = {
    'Scientific': """
    Provide a scientific analysis of this biblical passage.
    Examine how it relates to modern scientific understanding, natural phenomena,
    and archaeological findings. Consider any relevant geological, biological,
    astronomical, or other scientific contexts.

    Passage: {passage}

    Scientific Analysis:""",
    
    'Theological': """
    Provide a traditional religious interpretation of this biblical passage. 
    Analyze its spiritual significance and theological meaning.

    Passage: {passage}

    Religious Commentary:""",
    
    'Philosophical': """
    Provide a philosophical analysis of this biblical passage. 
    Discuss its ethical, metaphysical, and existential implications.

    Passage: {passage}

    Philosophical Analysis:""",
    
    'Secular': """
    Provide a secular scholarly interpretation of this biblical passage. 
    Examine its historical context and literary structure.

    Passage: {passage}

    Secular Analysis:"""
}

print("Available perspectives:", list(FIXED_PROMPTS.keys()))

@app.route("/api/get_passage", methods=["GET"])
def get_passage():
    passage_ref = request.args.get("passage")
    if not passage_ref:
        return jsonify({"error": "No passage reference provided"}), 400

    if not is_valid_reference(passage_ref):
        return jsonify({
            "error": "Please provide a valid reference format, such as 'Genesis 1:1', 'Genesis 1', or 'בראשית א:א'"
        }), 400
        
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
    try:
        # Get and validate parameters
        passage_ref = request.args.get("passage")
        perspective = request.args.get("perspective", "").strip()

        print("\n=== New Commentary Request ===")
        print(f"Raw request args: {dict(request.args)}")
        print(f"Perspective received: '{perspective}'")

        # Basic validation
        if not passage_ref:
            return jsonify({"error": "No passage reference provided"}), 400
        if not perspective:
            return jsonify({"error": "No perspective provided"}), 400

        # Force case-sensitive match for Scientific
        if perspective.lower() == "scientific":
            perspective = "Scientific"
            print("Forced Scientific perspective")

        # Check if perspective is valid
        if perspective not in FIXED_PROMPTS:
            print(f"Invalid perspective: '{perspective}'")
            print(f"Available perspectives: {list(FIXED_PROMPTS.keys())}")
            return jsonify({
                "error": f"Invalid perspective: {perspective}",
                "available_perspectives": list(FIXED_PROMPTS.keys())
            }), 400

        # Get passage text
        english_ref = convert_hebrew_reference(passage_ref)
        response = requests.get(f"{SEFARIA_API_URL}/{english_ref}", timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()

        passage_text = " ".join(filter(None, data.get("text", [])))[:500]
        if not passage_text:
            return jsonify({"error": "No text found for this passage"}), 404

        # Initialize OpenAI
        llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0.7
        )

        # Get the prompt and generate commentary
        prompt_template = FIXED_PROMPTS[perspective]
        prompt = PromptTemplate(input_variables=["passage"], template=prompt_template)
        formatted_prompt = prompt.format(passage=passage_text)
        commentary = llm.predict(formatted_prompt)

        print(f"Successfully generated {perspective} commentary")
        return jsonify({
            "commentary": commentary,
            "perspective": perspective
        })

    except Exception as e:
        print(f"Error in get_ai_commentary: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)