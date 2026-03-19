from ingestion.crawler import crawl_docs
from ingestion.chunker import chunk_documents
from ingestion.build_vector_db import build_topic_dbs

docs = crawl_docs()

chunks = chunk_documents(docs)

build_topic_dbs(chunks)