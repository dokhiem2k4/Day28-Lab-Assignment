# Local fallback: embed using random vectors (replace with real Kaggle embeddings later)
import os, random
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

qdrant = QdrantClient(host="localhost", port=6333)

try:
    qdrant.delete_collection("documents")
except Exception:
    pass

qdrant.create_collection(
    collection_name="documents",
    vectors_config=VectorParams(size=384, distance=Distance.COSINE)
)

records = [
    {"id": "doc_001", "text": "AI platform integration test"},
    {"id": "doc_002", "text": "Kafka to Delta pipeline"},
    {"id": "doc_003", "text": "Vector search with Qdrant"},
    {"id": "doc_004", "text": "Feature store with Redis and Feast"},
]

points = [
    PointStruct(
        id=i,
        vector=[random.uniform(-1, 1) for _ in range(384)],
        payload=rec
    )
    for i, rec in enumerate(records)
]

qdrant.upsert(collection_name="documents", points=points)
print(f"Integration 5 OK: {len(points)} vectors stored in Qdrant (local random embeddings)")
print("NOTE: Replace with real Kaggle embeddings by running 05_embed_to_qdrant.py after setting EMBED_NGROK_URL")
