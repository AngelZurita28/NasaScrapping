import json
import csv
import os

JSON_FILE_PATH = "embedding.json"
OUTPUT_DIR = "neo4j_import"

print("Iniciando la conversión de JSON a CSV para Neo4j...")

# Crear el directorio de salida si no existe
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Abrir los archivos CSV para escritura
with open(os.path.join(OUTPUT_DIR, 'articles.csv'), 'w', newline='', encoding='utf-8') as f_articles, \
     open(os.path.join(OUTPUT_DIR, 'chunks.csv'), 'w', newline='', encoding='utf-8') as f_chunks, \
     open(os.path.join(OUTPUT_DIR, 'entities.csv'), 'w', newline='', encoding='utf-8') as f_entities, \
     open(os.path.join(OUTPUT_DIR, 'rel_article_chunk.csv'), 'w', newline='', encoding='utf-8') as f_rel_ac, \
     open(os.path.join(OUTPUT_DIR, 'rel_article_entity.csv'), 'w', newline='', encoding='utf-8') as f_rel_ae:

    # --- Definir los escritores de CSV y escribir las cabeceras ---
    # Cabeceras especiales que Neo4j entiende
    w_articles = csv.writer(f_articles)
    w_articles.writerow(['articleId:ID(Article-ID)', 'title:string', 'link:string'])

    w_chunks = csv.writer(f_chunks)
    w_chunks.writerow(['chunkId:ID(Chunk-ID)', 'text:string', 'embedding:float[]'])

    w_entities = csv.writer(f_entities)
    w_entities.writerow(['entityId:ID(Entity-ID)', 'name:string', 'type:string'])

    w_rel_ac = csv.writer(f_rel_ac)
    w_rel_ac.writerow([':START_ID(Article-ID)', ':END_ID(Chunk-ID)'])

    w_rel_ae = csv.writer(f_rel_ae)
    w_rel_ae.writerow([':START_ID(Article-ID)', ':END_ID(Entity-ID)'])

    # --- Procesar el JSON ---
    with open(JSON_FILE_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    articles = data.get("articles", [])
    all_entities = {}
    chunk_counter = 0

    print(f"Procesando {len(articles)} artículos...")

    for article in articles:
        article_id = article.get('id')
        if not article_id:
            continue
            
        # Escribir datos del artículo
        w_articles.writerow([article_id, article.get('title'), article.get('link')])

        # Procesar y escribir chunks y sus relaciones
        for chunk in article.get('semantic_data', []):
            chunk_id = f"chunk_{chunk_counter}"
            
            # Convertir el vector a un string separado por punto y coma para el CSV
            embedding_str = ";".join(map(str, chunk.get('embedding_vector', [])))
            
            w_chunks.writerow([chunk_id, chunk.get('chunk_text'), embedding_str])
            w_rel_ac.writerow([article_id, chunk_id])
            chunk_counter += 1

        # Procesar entidades y sus relaciones
        for entity in article.get('graph_data', {}).get('nodes', []):
            entity_name = entity.get('properties', {}).get('name')
            entity_label = entity.get('label')

            if not entity_name or entity.get('id') == 'study_1':
                continue

            # Usamos un diccionario para no duplicar entidades en el CSV
            entity_unique_id = f"{entity_label}-{entity_name.lower()}"
            if entity_unique_id not in all_entities:
                all_entities[entity_unique_id] = {'name': entity_name, 'type': entity_label}
            
            w_rel_ae.writerow([article_id, entity_unique_id])

    # Escribir todas las entidades únicas al final
    print("Escribiendo entidades únicas...")
    for entity_id, entity_props in all_entities.items():
        w_entities.writerow([entity_id, entity_props['name'], entity_props['type']])
        
    print(f"\nConversión completada. Archivos guardados en la carpeta '{OUTPUT_DIR}'.")