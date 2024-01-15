from flask import Flask, render_template, request, jsonify

from rdflib import Graph, Literal
from rdflib.namespace import SKOS

app = Flask(__name__)

# Load the controlled vocabulary from the TTL file
g = Graph()
g.parse("dfgfo.ttl", format="ttl")

# Initialize the controlled vocabulary dictionary
controlled_vocabulary = {}

# Iterate through the controlled vocabulary concepts in the TTL file
for concept, _, label in g.triples((None, SKOS.prefLabel, None)):
    if isinstance(label, Literal) and "#" in concept:
        # Extract the "dfgfach" number from the URI
        number = concept.split("#")[1]
        lang = label.language  # Extract the language from the label
        if number in controlled_vocabulary:
            # If the number is already in the dictionary, append the new label and its language to it
            controlled_vocabulary[number].append((label.value, lang))
        else:
            # If the number is not in the dictionary, create a new entry with the label and its language
            controlled_vocabulary[number] = [(label.value, lang)]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search():
    user_input = request.args.get('subjectInput', '').lower()
    matching_subjects = []

    for number, labels in controlled_vocabulary.items():
        for label, lang in labels:
            if user_input in label.lower():
                matching_subjects.append((label, number, lang))

    return jsonify(matching_subjects)

if __name__ == '__main__':
    app.run(debug=True)
