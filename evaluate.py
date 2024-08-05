from neural_cherche import models, rank, retrieve, utils
import json

retriever = retrieve.BM25(key="id", on=["title", "text"])

with open("neural_cherche_data/documents.json", "r") as f:
    documents = json.load(f)

with open("neural_cherche_data/queries.json", "r") as f:
    queries = json.load(f)

with open("neural_cherche_data/queries_mapping.json", "r") as f:
    qrels = json.load(f)

# documents_embeddings = retriever.encode_documents(
#     documents=documents,
# )

device = "mps" # or "mps" or "conda"

documents, queries, qrels = utils.load_beir(
    "arguana",
    split="test",
)

retriever = retrieve.BM25(
    key="id",
    on=["title", "text"],
)


ranker = rank.ColBERT(
    key="id",
    on=["title", "text"],
    model=models.ColBERT(
        model_name_or_path="raphaelsty/neural-cherche-colbert",
        device=device,
    ).to(device),
)


retriever = retriever.add(
    documents_embeddings=retriever.encode_documents(
        documents=documents,
    )
)


candidates = retriever(
    queries_embeddings=retriever.encode_queries(
        queries=queries,
    ),
    k=30,
    tqdm_bar=True,
)

batch_size = 32

scores = ranker(
    documents=candidates,
    queries_embeddings=ranker.encode_queries(
        queries=queries,
        batch_size=batch_size,
        tqdm_bar=True,
    ),
    documents_embeddings=ranker.encode_candidates_documents(
        candidates=candidates,
        documents=documents,
        batch_size=batch_size,
        tqdm_bar=True,
    ),
    k=10,
)

scores = utils.evaluate(
    scores=scores,
    qrels=qrels,
    queries=queries,
    metrics=["ndcg@10"] + [f"hits@{k}" for k in range(1, 11)],
)

print(scores)
