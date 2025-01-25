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

# Perspectives for commentary generation
PERSPECTIVE_PROMPTS = {
    "Philosophical": """
    Provide a deep philosophical analysis of this biblical passage. 
    Explore its underlying metaphysical, ethical, and existential implications. 
    Draw connections to broader philosophical traditions and concepts.
    
    Passage: {passage}
    
    Philosophical Analysis:""",
    
    "Religious": """
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

@app.route("/api/get_ai_commentary", methods=["GET"])
def get_ai_commentary():
    passage_ref = request.args.get("passage")
    perspective = request.args.get("perspective", "Secular")
    
    if not passage_ref:
        return jsonify({"error": "No passage reference provided"}), 400
    
    if perspective not in PERSPECTIVE_PROMPTS:
        return jsonify({"error": "Invalid perspective"}), 400
    
    try:
        # First, get the passage
        response = requests.get(f"{SEFARIA_API_URL}/{passage_ref}", timeout=REQUEST_TIMEOUT)
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

