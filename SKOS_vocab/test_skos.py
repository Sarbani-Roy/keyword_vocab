from flask import Flask, render_template, request, jsonify
import requests
import json

app = Flask(__name__)

finto_url = 'http://253caac3-21ac-4f4b-be0a-076655c66384.ma.bw-cloud-instance.org:9090/rest/v1/search'
json_file_path = 'data.json'

def get_finto_suggestions(user_input):
    params = {
        'unique': 'true',
        'vocab': 'stw',
        'parent': '',
        'lang': 'en',
        'query': user_input + '*',
    }

    response = requests.get(finto_url, params=params)
    print(f"Finto API Request URL: {response.url}")

    if response.status_code == 200:
        data = response.json()
        with open(json_file_path, 'w') as json_file:
            json.dump(data.get('results', []), json_file, indent=2)

        keyword_data = data.get('results', [])
        suggestions = []

        for item in keyword_data:
            term = item.get("prefLabel")
            id = item.get("localname")
            vocab = item.get("vocab")
            uri = item.get("uri")

            suggestions.append({
                "term": term,
                "id": id,
                "vocab": vocab,
                "uri": uri,
            })

        return suggestions

    else:
        print(f"Finto API Request failed with status code {response.status_code}. Response text: {response.text}")
        return []

@app.route('/')
def index():
    #return render_template('index_skos.html')
    return render_template('index.html')

@app.route('/search')
def search():
    user_input = request.args.get('termInput', '').lower()  # Adjusted to match the form input name
    matching_keywords = []

    if user_input:
        # Get suggestions from Finto API
        finto_suggestions = get_finto_suggestions(user_input)
        matching_keywords.extend(finto_suggestions)

    return jsonify(matching_keywords)

if __name__ == '__main__':
    app.run(debug=True)
