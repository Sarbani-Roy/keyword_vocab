from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# Wikidata endpoint URL for fetching subjects
wikidata_endpoint = "https://www.wikidata.org/w/api.php"

# Function to fetch suggestions from Wikidata API
def get_wikidata_suggestions(user_input):
    params = {
        'action': 'wbsearchentities',
        'format': 'json',
        'search': user_input,
        'language': 'en',  # Add the language parameter
    }

    response = requests.get(wikidata_endpoint, params=params)

    print(f"API Request URL: {response.url}")  # Print the API request URL for debugging

    if response.status_code == 200:
        data = response.json()
        print(f"API Response Data: {data}")  # Print the API response data for debugging
        return [(result['label'], result['id']) for result in data.get('search', [])]
    else:
        print(f"API Request failed with status code {response.status_code}. Response text: {response.text}")
        return []

@app.route('/')
def index():
    return render_template('index_wiki.html')

@app.route('/search')
def search():
    user_input = request.args.get('keywordInput', '').lower()
    matching_keywords = []

    if user_input:
        # Get suggestions from Wikidata API
        suggestions = get_wikidata_suggestions(user_input)

        # Map suggestions to the format expected by the frontend
        matching_keywords = [(label, qid) for label, qid in suggestions]

    return jsonify(matching_keywords)

if __name__ == '__main__':
    app.run(debug=True)
