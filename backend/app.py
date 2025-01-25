@app.route('/api/get_commentaries', methods=['GET'])
def get_commentaries():
    """API endpoint to fetch commentaries and generate comparisons."""
    passage = request.args.get('passage')
    if not passage:
        return jsonify({'error': 'Passage is required.'}), 400

    try:
        response = requests.get(f"{SEFARIA_API_URL}{passage}?with=links")
        if response.status_code != 200:
            return jsonify({'error': 'Failed to fetch data from Sefaria API.'}), 500

        data = response.json()
        links = data.get('links', [])
        commentaries = [
            link for link in links if link.get('category') == 'Commentary' and 'source_text' in link
        ]

        if not commentaries:
            return jsonify({'message': 'No commentaries available for this passage.'}), 200

        # Debugging: Print the raw commentaries for inspection
        print("Raw commentaries:", commentaries)

        commentary_texts = "\n\n".join(
            f"{c.get('source_title')}: {c.get('source_text')}" for c in commentaries
        )

        messages = [
            SystemMessage(content="Compare and summarize the following Torah commentaries."),
            HumanMessage(content=commentary_texts)
        ]
        comparison = llm(messages)

        return jsonify({
            'commentaries': [
                {'source': c.get('source_title'), 'text': c.get('source_text')}
                for c in commentaries
            ],
            'comparison': comparison.content
        })
    except Exception as e:
        # Debugging: Print the error to logs
        print("Error fetching commentaries:", str(e))
        return jsonify({'error': str(e)}), 500

