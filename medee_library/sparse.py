from neural_cherche import models, retrieve
import torch

device = "cuda" if torch.cuda.is_available() else "mps"
batch_size = 32

model = models.Splade(
    model_name_or_path="raphaelsty/neural-cherche-sparse-embed",
    device=device,
)

documents = [
    {"id": "doc1", "title": "Paris", "text": "Paris is the capital of France."},
    {"id": "doc2", "title": "Montreal", "text": "Montreal is the largest city in Quebec."},
    {"id": "doc3", "title": "Bordeaux", "text": "Bordeaux in Southwestern France."},
]

retriever = retrieve.Splade(
    key="id",
    on=["title", "text"],
    model=model
)

documents_embeddings = retriever.encode_documents(
    documents=documents,
    batch_size=batch_size,
)

retriever.add(
    documents_embeddings=documents_embeddings,
)

queries = [
    "What is the capital of France?",
    "What is the largest city in Quebec?",
    "Where is Bordeaux?",
]

queries_embeddings = retriever.encode_queries(
    queries=queries,
    batch_size=batch_size,
)

scores = retriever(
    queries_embeddings=queries_embeddings,
    k=100,
)

print(scores)
