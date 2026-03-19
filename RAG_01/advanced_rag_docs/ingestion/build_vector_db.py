import os
from langchain_community.vectorstores import FAISS
from llm.models import embeddings
from ingestion.classifier import classify_chunk
from config.settings import TOPICS, VECTOR_DB_PATH


def build_topic_dbs(chunks):

    topic_chunks = {topic: [] for topic in TOPICS}

    print("Classifying chunks into topics...")

    for chunk in chunks:

        topic = classify_chunk(chunk)

        topic_chunks[topic].append(chunk)

    os.makedirs(VECTOR_DB_PATH, exist_ok=True)

    vector_dbs = {}

    for topic, docs in topic_chunks.items():

        if len(docs) == 0:
            continue

        print(f"Building DB for topic: {topic}")

        db = FAISS.from_documents(docs, embeddings)

        path = f"{VECTOR_DB_PATH}/{topic}_db"

        db.save_local(path)

        vector_dbs[topic] = db

    print("All vector databases created.")

    return vector_dbs