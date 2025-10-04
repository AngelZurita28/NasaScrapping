from neo4j import GraphDatabase

# --- USA LA MISMA CONFIGURACIÓN QUE TU SCRIPT PRINCIPAL ---
NEO4J_URI = "bolt://127.0.0.1:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "root1234"
NEO4J_DATABASE = "hackathon" 


try:
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    with driver.session() as session:
        result = session.run("RETURN 1")
        print("¡Conexión exitosa! La base de datos respondió.")
    driver.close()
except Exception as e:
    print(f"Falló la conexión: {e}")