import json
from neo4j import GraphDatabase

# --- CONFIGURACIÓN DE LA CONEXIÓN ---
NEO4J_URI = "bolt://127.0.0.1:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "root1234"
NEO4J_DATABASE = "hackathon" 
JSON_FILE_PATH = "embedding.json" 

class Neo4jUploader:
    def __init__(self, uri, user, password, db):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.database = db

    def close(self):
        self.driver.close()

    def load_article_data(self, article_data):
        with self.driver.session(database=self.database) as session:
            session.execute_write(self._create_article_graph, article_data)

    @staticmethod
    def _create_article_graph(tx, article):
        query = """
        MERGE (a:Article {id: $article_id})
        SET a.title = $title, a.link = $link
        WITH a
        UNWIND $chunks as chunk_data
        CREATE (c:Chunk {text: chunk_data.chunk_text, embedding: chunk_data.embedding_vector})
        MERGE (a)-[:HAS_CHUNK]->(c)
        WITH a
        UNWIND $entities as entity_data
        MERGE (e:Entity {name: entity_data.properties.name, type: entity_data.label})
        MERGE (a)-[:MENTIONS]->(e)
        """
        
        graph_data = article.get('graph_data', {})
        entities = graph_data.get('nodes', [])
        
        # ▼▼▼ LÍNEA CORREGIDA ▼▼▼
        # Ahora filtramos las entidades que no tienen nombre (valor nulo o vacío)
        # y también el nodo 'study_1'.
        filtered_entities = [
            node for node in entities 
            if node.get('id') != 'study_1' and node.get('properties', {}).get('name')
        ]

        tx.run(query, 
               article_id=article.get('id'),
               title=article.get('title'),
               link=article.get('link'),
               chunks=article.get('semantic_data', []),
               entities=filtered_entities
        )

def main():
    uploader = Neo4jUploader(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, NEO4J_DATABASE)
    try:
        with open(JSON_FILE_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        articles = data.get("articles", [])
        print(f"Se encontraron {len(articles)} artículos en el archivo JSON.")

        for i, article in enumerate(articles):
            print(f"({i+1}/{len(articles)}) Cargando artículo: '{article.get('title', 'Sin Título')}' en la BD '{NEO4J_DATABASE}'...")
            uploader.load_article_data(article)
        
        print(f"\n¡Carga de datos en '{NEO4J_DATABASE}' completada exitosamente!")

    except Exception as e:
        print(f"Ocurrió un error: {e}")
    finally:
        uploader.close()
        print("Conexión con Neo4j cerrada.")

if __name__ == "__main__":
    main()