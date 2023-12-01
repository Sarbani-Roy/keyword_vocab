import csv
from rdflib import Graph, Namespace, URIRef, Literal, RDF

# Create an RDF graph
g = Graph()

# Define the SKOS namespace
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#") 
DFGFACH = Namespace("https://www.dfg.de/dfg_profil/gremien/fachkollegien/faecher/#")

# Bind the namespaces to prefixes
g.bind("skos", SKOS)
g.bind("dfgfach", DFGFACH) 

# Create the concept scheme
concept_scheme_uri = DFGFACH["concept_scheme"]
g.add((concept_scheme_uri, RDF.type, SKOS.ConceptScheme))
g.add((concept_scheme_uri, SKOS.prefLabel, Literal("DFG Fachbezeichnung", lang="de")))
g.add((concept_scheme_uri, SKOS.prefLabel, Literal("DFG Subject Heading", lang="en")))
g.add((concept_scheme_uri, SKOS.notation, Literal("DFG")))

# Load the CSV file
csv_file = "dfg_subjects.CSV"

with open(csv_file, "r") as file:
    csv_reader = csv.DictReader(file, delimiter=";")
    latest_broad_concept_uri = None
    first_broad_concept_uri = None

    for row in csv_reader:
        concept_uri = DFGFACH[row['DFG-Fach']]  # Create a URI for the concept

        # Define the concept using RDF.type and SKOS.Concept
        g.add((concept_uri, RDF.type, SKOS.Concept))

        # Add the preferred labels
        g.add((concept_uri, SKOS.prefLabel, Literal(row['DFG Fachbezeichnung'], lang="de")))
        g.add((concept_uri, SKOS.prefLabel, Literal(row['DFG Subject Heading'], lang="en")))
        g.add((concept_uri, SKOS.inScheme, concept_scheme_uri ))

        # Check if the concept has a code with the format "101-0*" or "102-0*"
        if "-" in row['DFG-Fach']:
            narrower_uri = DFGFACH[row['DFG-Fach']]
            broader_code = row['DFG-Fach'].split('-')[0]
            broader_uri = DFGFACH[broader_code]
            g.add((concept_uri, SKOS.broader, broader_uri))
            g.add((latest_broad_concept_uri, SKOS.narrower, narrower_uri))
            g.add((concept_uri, SKOS.note, Literal('Second-level of classification', lang="en")))
            #g.add((broader_uri, SKOS.related, concept_uri))
        else:
            if latest_broad_concept_uri is not None:
                g.add((concept_uri, SKOS.related, latest_broad_concept_uri))
            if first_broad_concept_uri is None:
                first_broad_concept_uri = concept_uri
            latest_broad_concept_uri = concept_uri
            g.add((concept_uri, SKOS.topConceptOf, concept_scheme_uri))
            g.add((concept_scheme_uri, SKOS.hasTopConcept, concept_uri))
            g.add((concept_uri, SKOS.note, Literal('First-level of classification', lang="en")))
            
    g.add((first_broad_concept_uri, SKOS.related, latest_broad_concept_uri))


#print("--- printing raw triples ---")
#for s, p, o in g:
#    print((s, p, o))

# Serialize the RDF graph to a Turtle file
ttl_file = "output_skos.ttl"
g.serialize(destination=ttl_file, format="turtle")

print(f"TTL file generated: {ttl_file}")
