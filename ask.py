"""
Permet de poser une question et voir les 10 chunks renvoyés de qdrant
"""

from medee_library.model import create_embeddings
from medee_library.qdrant import run_query

collection_name = "reco_alibaba"

question = input("Quelle est votre question ? ")
embeddings = create_embeddings(question.lower())
results = run_query(collection_name, embeddings, 10)

for res in results:
    print("\n\n")
    print(res.id, res.score, res.payload)
