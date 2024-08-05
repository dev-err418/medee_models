from neural_cherche import models, retrieve, utils

documents, queries, qrels = utils.load_beir(
    "scifact",
    split="test",
)

retriever = retrieve.BM25(
    key="id",
    on=["title", "text"],
)

documents_embeddings = retriever.encode_documents(
    documents=documents,
)

retriever = retriever.add(documents_embeddings=documents_embeddings)


queries_embeddings = retriever.encode_queries(
    queries=queries,
)

scores = retriever(
    queries_embeddings=queries_embeddings,
    k=10,
    tqdm_bar=True,
    batch_size=1024,
)

scores = utils.evaluate(
    scores=scores,
    qrels=qrels,
    queries=queries,
    metrics=["ndcg@10"] + [f"hits@{k}" for k in range(1, 10)],
)

print(scores)
