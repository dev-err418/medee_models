from neural_cherche import retrieve, utils
import json

retriever = retrieve.BM25(key="id", on=["title", "text"])

with open("neural_cherche_data/documents.json", "r") as f:
    documents = json.load(f)

with open("neural_cherche_data/queries.json", "r") as f:
    queries = json.load(f)

with open("neural_cherche_data/queries_mapping.json", "r") as f:
    qrels = json.load(f)

documents_embeddings = retriever.encode_documents(
    documents=documents,
)

documents_embeddings = retriever.add(
    documents_embeddings=documents_embeddings,
)

queries_embeddings = retriever.encode_queries(
    queries=queries,
)

scores = retriever(
    queries_embeddings=queries_embeddings,
    k=30,
)

utils.evaluate(
    scores=scores,
    qrels=qrels,
    queries=queries,
    metrics=["map", "ndcg@10", "ndcg@100", "recall@10", "recall@100"],
)
