from database.neo4j_loader import Neo4jLoader
from database.qdrant_loader import clear_vectors

neo4j = Neo4jLoader()
neo4j.clear_all()
clear_vectors()

print("All knowledge graphs and vectors deleted successfully")
