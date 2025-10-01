import json
import requests
from bs4 import BeautifulSoup
import time
import os

def enrich_json_with_scraping(json_input_path, json_output_path):
    """
    Lee un archivo JSON con artículos, extrae el texto completo de los enlaces
    usando una estrategia de búsqueda múltiple, y guarda el resultado.
    """
    
    if os.path.exists(json_output_path):
        print(f"📄 Se encontró un archivo existente. Cargando progreso...")
        with open(json_output_path, mode='r', encoding='utf-8') as json_file:
            articles = json.load(json_file)
    else:
        print(f"📄 No se encontró progreso. Cargando desde el archivo base...")
        with open(json_input_path, mode='r', encoding='utf-8') as json_file:
            articles = json.load(json_file)

    print(f"✅ Se cargaron {len(articles)} artículos.")

    articles_processed_since_start = 0
    for i, article in enumerate(articles):
        if article.get('texto_completo') and "No se pudo encontrar" not in article.get('texto_completo', ''):
            continue

        link = article.get('Link')
        if not link:
            article['texto_completo'] = "No se encontró link."
            continue

        print(f"🔎 Procesando artículo ID {article.get('id', i+1)}: {article.get('Title', 'Sin Título')[:40]}...")

        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
            response = requests.get(link, headers=headers, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            
            # --- ¡NUEVA LÓGICA DE BÚSQUEDA EN CASCADA! ---
            article_body = None

            # Intento 1: El selector original (el más común hasta ahora)
            article_body = soup.find('div', class_='j-article-body')

            # Intento 2: El selector específico que descubriste
            if not article_body:
                article_body = soup.find('section', attrs={'aria-label': 'Article content'})

            # Intento 3: El selector más general como último recurso
            if not article_body:
                article_body = soup.find('article')
            
            if article_body:
                article['texto_completo'] = article_body.get_text(separator='\n', strip=True)
                print("  -> ✅ Texto extraído y guardado en memoria.")
            else:
                article['texto_completo'] = "No se pudo encontrar el cuerpo del artículo en la página."

        except requests.exceptions.RequestException as e:
            print(f"❌ Error al acceder al link para el artículo ID {article.get('id', i+1)}: {e}")
            article['texto_completo'] = "Error al intentar conectar con la URL."
        
        articles_processed_since_start += 1
        time.sleep(1)

        if articles_processed_since_start > 0 and articles_processed_since_start % 10 == 0:
            print(f"💾 Guardando progreso en disco... ({i+1}/{len(articles)})")
            with open(json_output_path, mode='w', encoding='utf-8') as json_file:
                json.dump(articles, json_file, indent=4, ensure_ascii=False)

    print("\n🎉 ¡Proceso completado! Guardando archivo final...")
    with open(json_output_path, mode='w', encoding='utf-8') as json_file:
        json.dump(articles, json_file, indent=4, ensure_ascii=False)
    print(f"✅ Se ha guardado toda la información en '{json_output_path}'.")

# --- Uso del script ---
json_base = 'salida.json' 
json_enriquecido = 'datos_texto_completo.json' 

enrich_json_with_scraping(json_base, json_enriquecido)