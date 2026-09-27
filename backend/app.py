import os
import re
import html
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
SEFARIA_HEADERS = {"User-Agent": "TorahLens/1.0 (+https://github.com/jackmitchelwidman/torahlens)"}

def clean_segments(text):
    """Turn Sefaria text (str or nested list) into a flat list of clean verse strings."""
    if isinstance(text, str):
        text = [text]
    if not isinstance(text, list):
        return []
    out = []
    for seg in text:
        if isinstance(seg, list):
            out.extend(clean_segments(seg))
            continue
        if not isinstance(seg, str):
            continue
        seg = re.sub(r'<i class="footnote">.*?</i>', '', seg, flags=re.S)
        seg = re.sub(r'<sup class="footnote-marker">.*?</sup>', '', seg, flags=re.S)
        seg = re.sub(r'<[^>]+>', '', seg)
        seg = html.unescape(seg).replace('\u200b', '').replace('\u00a0', ' ')
        seg = re.sub(r'\s+', ' ', seg).strip()
        if seg:
            out.append(seg)
    return out

class ReferenceNotFound(Exception):
    """Sefaria could not resolve the reference."""

def fetch_sefaria(english_ref):
    """Fetch only the requested verses (context=0) and return the parsed JSON."""
    response = requests.get(
        f"{SEFARIA_API_URL}/{english_ref}",
        params={"context": 0},
        headers=SEFARIA_HEADERS,
        timeout=REQUEST_TIMEOUT,
    )
    if response.status_code in (400, 404):
        raise ReferenceNotFound(english_ref)
    response.raise_for_status()
    data = response.json()
    if data.get("error") or not (data.get("text") or data.get("he")):
        raise ReferenceNotFound(english_ref)
    return data

_SHAPE_CACHE = {}

def chapter_lengths(book):
    """Verse count per chapter for a book, from Sefaria's shape API (cached)."""
    if book not in _SHAPE_CACHE:
        r = requests.get(f"https://www.sefaria.org/api/shape/{book}", headers=SEFARIA_HEADERS, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        shape = r.json()
        shape = shape[0] if isinstance(shape, list) else shape
        _SHAPE_CACHE[book] = shape.get("chapters") or []
    return _SHAPE_CACHE[book]

def neighbor_refs(data):
    """Compute (prev_ref, next_ref) that continue reading with a window the same size
    as the current passage. Falls back to Sefaria's chapter neighbors."""
    book = data.get("book")
    sections = data.get("sections") or []
    to_sections = data.get("toSections") or sections
    fallback = (data.get("prev"), data.get("next"))
    if data.get("textDepth") != 2 or not book or len(sections) < 2:
        return fallback
    try:
        lengths = chapter_lengths(book)
    except requests.RequestException:
        return fallback
    c1, v1 = sections[0], sections[1]
    c2, v2 = to_sections[0], to_sections[1]
    if not lengths or c1 < 1 or c2 > len(lengths):
        return fallback
    # window size in verses
    if c1 == c2:
        n = v2 - v1 + 1
    else:
        n = (lengths[c1 - 1] - v1 + 1) + sum(lengths[c1:c2 - 1]) + v2
    n = max(1, n)

    def fmt(c, a, b):
        return f"{book} {c}:{a}" if a == b else f"{book} {c}:{a}-{b}"

    nxt = None
    if v2 < lengths[c2 - 1]:
        a = v2 + 1
        nxt = fmt(c2, a, min(a + n - 1, lengths[c2 - 1]))
    elif c2 < len(lengths):
        nxt = fmt(c2 + 1, 1, min(n, lengths[c2]))

    prv = None
    if v1 > 1:
        b = v1 - 1
        prv = fmt(c1, max(1, b - n + 1), b)
    elif c1 > 1:
        b = lengths[c1 - 2]
        prv = fmt(c1 - 1, max(1, b - n + 1), b)
    return prv, nxt

RESOLVE_PROMPT = """You convert a natural-language description of a Bible passage into one citation
that the Sefaria API accepts. Use English book names (Genesis, Exodus, Leviticus, Numbers,
Deuteronomy, Joshua, Judges, I Samuel, II Samuel, I Kings, II Kings, Isaiah, Jeremiah, Ezekiel,
Hosea, Joel, Amos, Obadiah, Jonah, Micah, Nahum, Habakkuk, Zephaniah, Haggai, Zechariah, Malachi,
Psalms, Proverbs, Job, Song of Songs, Ruth, Lamentations, Ecclesiastes, Esther, Daniel, Ezra,
Nehemiah, I Chronicles, II Chronicles) and the form "Book chapter:verse-verse", "Book chapter:verse"
or "Book chapter". Choose a focused span of at most about 15 verses. For a vague description like
"the beginning of Genesis" pick the opening verses, e.g. "Genesis 1:1-5". For a named episode pick
the verses where it happens. If the description does not identify a Tanakh passage, answer UNKNOWN.
Answer with the citation only, no other words.

Description: {phrase}
Citation:"""

def resolve_with_ai(phrase):
    """Ask the model to turn a free-text phrase into a Sefaria citation, or None."""
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0,
    )
    answer = llm.predict(RESOLVE_PROMPT.format(phrase=phrase)).strip().strip('"').strip('.')
    answer = answer.replace('\u2013', '-').replace('\u2014', '-')
    print(f"AI resolved {phrase!r} -> {answer!r}")
    if not answer or answer.upper() == "UNKNOWN":
        return None
    if not re.match(r'^[A-Za-z I]+(?:\s\d+(?::\d+(?:-\d+)?)?)?$', answer):
        return None
    return answer

def resolve_passage(user_input):
    """Return (sefaria_data, ref, resolved_from). Tries the literal reference first,
    then falls back to interpreting the input as a description of a passage."""
    literal = convert_hebrew_reference(user_input)
    try:
        return fetch_sefaria(literal), literal, None
    except (ReferenceNotFound, requests.RequestException):
        pass
    guess = resolve_with_ai(user_input)
    if not guess:
        raise ReferenceNotFound(user_input)
    return fetch_sefaria(guess), guess, user_input

# Hebrew book names mapping
HEBREW_BOOK_NAMES = {
    'בראשית': 'Genesis',
    'שמות': 'Exodus',
    'ויקרא': 'Leviticus',
    'במדבר': 'Numbers',
    'דברים': 'Deuteronomy'
}

HEBREW_NUMERALS = {
    'א': 1, 'ב': 2, 'ג': 3, 'ד': 4, 'ה': 5, 'ו': 6, 'ז': 7, 'ח': 8, 'ט': 9,
    'י': 10, 'כ': 20, 'ך': 20, 'ל': 30, 'מ': 40, 'ם': 40, 'נ': 50, 'ן': 50,
    'ס': 60, 'ע': 70, 'פ': 80, 'ף': 80, 'צ': 90, 'ץ': 90, 'ק': 100, 'ר': 200,
    'ש': 300, 'ת': 400,
}

def hebrew_numeral_to_int(token):
    """Convert a Hebrew numeral like א, טו, or כ״ג to an int; return None if not one."""
    letters = token.replace('״', '').replace('"', '').replace("'", '').replace('׳', '')
    if not letters or any(ch not in HEBREW_NUMERALS for ch in letters):
        return None
    return sum(HEBREW_NUMERALS[ch] for ch in letters)

def convert_hebrew_numerals(rest):
    """Turn 'א:א-ה' into '1:1-5'; leave anything that is not Hebrew numerals alone."""
    def repl(m):
        n = hebrew_numeral_to_int(m.group(0))
        return str(n) if n is not None else m.group(0)
    return re.sub(r"[\u05d0-\u05ea\u05f3\u05f4'\"]+", repl, rest)

def convert_hebrew_reference(ref):
    """Convert Hebrew reference to English."""
    parts = ref.strip().split(' ')
    if not parts:
        return ref
    book = parts[0]
    rest = ' '.join(parts[1:]) if len(parts) > 1 else ''
    english_book = HEBREW_BOOK_NAMES.get(book, book)
    if book in HEBREW_BOOK_NAMES:
        rest = convert_hebrew_numerals(rest)
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

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/api/get_passage", methods=["GET"])
def get_passage():
    passage_ref = request.args.get("passage")
    if not passage_ref:
        return jsonify({"error": "No passage reference provided"}), 400

    try:
        data, english_ref, resolved_from = resolve_passage(passage_ref)
        sections = data.get("sections") or []
        start_verse = sections[1] if len(sections) > 1 else 1
        prev_ref, next_ref = neighbor_refs(data)
        return jsonify({
            "ref": data.get("ref", english_ref),
            "heRef": data.get("heRef", ""),
            "resolved_from": resolved_from,
            "prev_ref": prev_ref,
            "next_ref": next_ref,
            "start_verse": start_verse,
            "hebrew": clean_segments(data.get("he", "")),
            "english": clean_segments(data.get("text", ""))
        })
    except ReferenceNotFound:
        return jsonify({
            "error": "Couldn't find that passage. Try a reference like 'Genesis 1:1', 'בראשית א:א', or a description like 'the beginning of Genesis'"
        }), 404
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
        data, english_ref, _ = resolve_passage(passage_ref)

        passage_text = " ".join(clean_segments(data.get("text", "")))[:2000]
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

    except ReferenceNotFound:
        return jsonify({"error": "Couldn't find that passage"}), 404
    except Exception as e:
        print(f"Error in get_ai_commentary: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)