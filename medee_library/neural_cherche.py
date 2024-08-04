from medee_library.qdrant import get_points
import json

collection_name = "reco_alibaba"

def create_documents_file(nombre_points):
    """
    Output format

    [
        {
            "id": "document_0",
            "title": "title 0",
            "text": "text 0",
        },
        {
            "id": "document_1",
            "title": "title 1",
            "text": "text 1",
        },
        ...
        {
            "id": "document_n",
            "title": "title n",
            "text": "text n",
        },
    ]
    """

    documents = []

    for i in range(nombre_points):
        results = get_points(collection_name, [i])
        point = results[0].payload
        id = "document_" + str(i)

        doc = {
            "id": id,
            "title": point["path"],
            "text": point["content"]
        }

        documents.append(doc)
        print(id, "ok")

    with open("neural_cherche_data/documents.json", "w") as f:
        json.dump(documents, f, indent=4)


def create_queries_file():
    """
    Output format

    [
        "first query",
        "second query",
        "third query",
        "fourth query",
        "fifth query",
    ]
    """

    with open("sparse_triplet.json", "r") as f:
        data = json.load(f)

    queries = []
    queries_mapping_file = {}

    i = 0
    for triplet in data:
        queries.append(triplet["anchor"])
        id = "document_" + str(i)
        queries_mapping_file[triplet["anchor"]] = { id: 1 }

        i += 1

    with open("neural_cherche_data/queries.json", "w") as f:
        json.dump(queries, f, indent=4)

    create_queries_mapping_file(queries_mapping_file)



def create_queries_mapping_file(content):
    """
    Output format

    {
        "first query": {"document_0": 1},
        "second query": {"document_10": 1},
        "third query": {"document_5": 1},
        "fourth query": {"document_22": 1},
        "fifth query": {"document_23": 1, "document_0": 1},
    }
    """

    with open("neural_cherche_data/queries_mapping.json", "w") as f:
        json.dump(content, f, indent=4)
