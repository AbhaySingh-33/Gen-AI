from ingestion.pdf_loader import load_pdf
from ingestion.chunker import chunk_documents
from ingestion.kg_extractor import extract_kg

from database.neo4j_loader import Neo4jLoader
from database.qdrant_loader import store_vectors


docs = load_pdf("data/document.pdf")

chunks = chunk_documents(docs)

neo4j = Neo4jLoader()

for chunk in chunks:

    kg_data = extract_kg(chunk)

    neo4j.insert_graph(kg_data)

store_vectors(chunks)

print("Knowledge graph and vectors created successfully")