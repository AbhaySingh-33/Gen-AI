from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from sentence_transformers import SentenceTransformer
from config.settings import settings

model = SentenceTransformer("all-MiniLM-L6-v2")

client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)

def store_vectors(chunks):
    # Create collection if it doesn't exist
    if not client.collection_exists("pdf_chunks"):
        client.create_collection(
            collection_name="pdf_chunks",
            vectors_config=VectorParams(size=384, distance=Distance.COSINE)
        )

    points = []

    for i, chunk in enumerate(chunks):

        vector = model.encode(chunk.page_content).tolist()

        points.append({
            "id": i,
            "vector": vector,
            "payload": {"text": chunk.page_content}
        })

    client.upsert(
        collection_name="pdf_chunks",
        points=points
    )

def clear_vectors():
    if client.collection_exists("pdf_chunks"):
        client.delete_collection("pdf_chunks")