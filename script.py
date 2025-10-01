import csv
import json

def convert_csv_to_json(csv_file_path, json_file_path):
    """
    Lee un archivo CSV con columnas 'Titulo' y 'Link', lo convierte a JSON
    y añade un ID único a cada registro.
    """
    json_data = []
    try:
        with open(csv_file_path, mode='r', encoding='utf-8') as csv_file:
            # DictReader leerá la primera fila como encabezados y manejará las comillas
            csv_reader = csv.DictReader(csv_file)
            
            # Asignamos un ID a cada fila y la agregamos a la lista
            for i, row in enumerate(csv_reader):
                row['id'] = i + 1
                json_data.append(row)

        with open(json_file_path, mode='w', encoding='utf-8') as json_file:
            # Escribimos la lista de diccionarios en un archivo JSON con formato legible
            json.dump(json_data, json_file, indent=4, ensure_ascii=False)
            
        print(f"✅ ¡Éxito! Se ha convertido el archivo '{csv_file_path}' a '{json_file_path}'.")

    except FileNotFoundError:
        print(f"❌ Error: El archivo '{csv_file_path}' no fue encontrado.")
    except Exception as e:
        print(f"❌ Ocurrió un error inesperado: {e}")

# --- Uso del script ---
# 1. Asegúrate de tener un archivo CSV llamado 'datos.csv' en la misma carpeta.
# 2. Reemplaza los nombres si es necesario.
csv_input = 'datos.csv'
json_output = 'salida.json'

convert_csv_to_json(csv_input, json_output)