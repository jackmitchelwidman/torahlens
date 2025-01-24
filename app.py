from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/get_passage', methods=['GET'])
def get_passage():
    passage = request. args.get('passage')
    sefaria_url = f"https://www.sefaria.org/api/texts/{passage}"
    response = requests.get(sefaria_url)
    data = response.json()
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)

