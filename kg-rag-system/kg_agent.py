import sys
import os

# Add app directory to path
app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app')
if app_path not in sys.path:
    sys.path.insert(0, app_path)

from database.neo4j_loader import Neo4jLoader  # type: ignore
from database.qdrant_loader import client, model  # type: ignore
from utils.mistral_client import call_mistral  # type: ignore

class KGAgent:
    def __init__(self):
        self.neo4j = Neo4jLoader()
        
    def query_kg(self, query):
        with self.neo4j.driver.session() as session:
            result = session.run(
                """
                MATCH (e:Entity)
                WHERE toLower(e.name) CONTAINS toLower($search_query)
                OPTIONAL MATCH (e)-[r:REL]->(t:Entity)
                RETURN e.name as entity, e.type as type, 
                       collect({relation: r.type, target: t.name}) as relationships
                LIMIT 10
                """,
                search_query=query
            )
            return [dict(record) for record in result]
    
    def query_vectors(self, query, limit=3):
        from qdrant_client.models import PointStruct
        vector = model.encode(query).tolist()
        results = client.query_points(
            collection_name="pdf_chunks",
            query=vector,
            limit=limit
        ).points
        return [hit.payload["text"] for hit in results]
    
    def chat(self, user_query):
        kg_results = self.query_kg(user_query)
        vector_results = self.query_vectors(user_query)
        
        kg_context = "\n".join([
            f"- {r['entity']} ({r['type']}): {', '.join([rel['relation'] + ' ' + rel['target'] for rel in r['relationships'] if rel['target']])}"
            for r in kg_results if r['relationships']
        ])
        
        vector_context = "\n\n".join(vector_results)
        
        system_prompt = """You are a helpful assistant with access to a knowledge graph and document chunks.
Use the provided context to answer questions accurately and concisely."""
        
        user_prompt = f"""Question: {user_query}

Knowledge Graph Context:
{kg_context if kg_context else 'No relevant entities found'}

Document Context:
{vector_context}

Answer:"""
        
        return call_mistral(system_prompt, user_prompt)
