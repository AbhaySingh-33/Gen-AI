from langchain_community.vectorstores import FAISS
from llm.models import embeddings
from config.settings import VECTOR_DB_PATH
from routing.router import route_query
from retrieval.multi_query import generate_queries
from retrieval.rrf import reciprocal_rank_fusion
from agents.query_decomposer import decompose_query
import os


def load_db(topic):
    path = f"{VECTOR_DB_PATH}/{topic}_db"

    if not os.path.exists(path):
        available_dbs = [d.replace("_db", "") for d in os.listdir(VECTOR_DB_PATH) if d.endswith("_db")]
        if not available_dbs:
            raise ValueError("No vector databases found. Please run ingestion first.")
        topic = available_dbs[0]
        path = f"{VECTOR_DB_PATH}/{topic}_db"
        print(f"Topic database not found. Using '{topic}' database instead.")

    db = FAISS.load_local(
        path,
        embeddings,
        allow_dangerous_deserialization=True
    )

    return db


def retrieve_advanced(query):
    sub_queries = decompose_query(query)
    
    if not sub_queries:
        sub_queries = [query]

    all_results = []

    for sub_query in sub_queries:
        topic = route_query(sub_query)
        db = load_db(topic)
        queries = generate_queries(sub_query)

        for q in queries:
            docs = db.similarity_search(q, k=5)
            all_results.append(docs)

    ranked_docs = reciprocal_rank_fusion(all_results)

    return ranked_docs[:8]
