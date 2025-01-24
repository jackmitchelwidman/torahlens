from flask import Flask, request, jsonify, send_from_directory
import requests
import os

app = Flask(__name__)

# Serve index.html at the root endpoint
@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/get_passage', methods=['GET'])
def get_passage():
    passage = request.args.get('passage')
    sefaria_url = f"https://www.sefaria.org/api/texts/{passage}"
    response = requests.get(sefaria_url)
    data = response.json()
    return jsonify(data)

if __name__ == '__main__':
    # Use the PORT environment variable provided by Heroku
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

