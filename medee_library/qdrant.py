import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient, models

load_dotenv()

key = os.getenv("QDRANT_KEY")
url = os.getenv("QDRANT_URL")

client = QdrantClient(
    url=url,
    api_key=key
)

def is_reco_created(collection_name):
    collections = client.get_collections()
    if collection_name not in collections.collections:
        create_reco_collection(collection_name)

def create_reco_collection(collection_name):
    client.recreate_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(size=1536 if collection_name in ["reco_alibaba", "reco_stella"] else 1024, distance=models.Distance.DOT)
    )
    print("Reco collection created !")

def add_vector(collection_name, embedding, metadata, id):
    info = client.upsert(
        collection_name=collection_name,
        # wait=True,
        points=[
            models.PointStruct(
                id=id,
                vector=embedding,
                payload=metadata
            )
        ]
    )

    return info.status == models.UpdateStatus.COMPLETED

def run_query(collection_name, embedding, limit):
    results = client.search(
        collection_name=collection_name,
        query_vector=embedding,
        limit=limit
    )

    return results

def run_filter(collection_name, value, key="title"):
    results = client.scroll(
        collection_name=collection_name,
        with_vectors=True,
        scroll_filter=models.Filter(
            must=[
                models.FieldCondition(
                    key=key,
                    match=models.MatchValue(value=value),
                )
            ]
        ),
    )

    return results[0]

def get_points(collection_name, ids):
    results = client.retrieve(
        collection_name=collection_name,
        ids=ids
    )

    return results
