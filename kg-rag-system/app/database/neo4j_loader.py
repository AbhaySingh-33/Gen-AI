from neo4j import GraphDatabase
from config.settings import settings

class Neo4jLoader:

    def __init__(self):

        self.driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
        )

    def insert_graph(self, data):

        with self.driver.session() as session:

            for entity in data["entities"]:

                session.run(
                    "MERGE (e:Entity {name:$name,type:$type})",
                    name=entity["name"],
                    type=entity["type"]
                )

            for rel in data["relationships"]:

                session.run(
                    """
                    MATCH (a:Entity {name:$source})
                    MATCH (b:Entity {name:$target})
                    MERGE (a)-[:REL {type:$rel}]->(b)
                    """,
                    source=rel["source"],
                    target=rel["target"],
                    rel=rel["relation"]
                )

    def clear_all(self):
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")