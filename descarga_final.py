import csv
import requests
import time
from secrets import GOOGLE_API_KEY

# --- 1. CONFIGURACION ---

# COMENTA Y DESCOMENTA SEGUN LA CIUDAD QUE VAYAS A DESCARGAR

# ALICANTE
#ARCHIVO_ENTRADA = 'censo_restaurantes_alicante.csv'
#ARCHIVO_RESTAURANTES = 'dataset_restaurantes_alicante.csv'
#ARCHIVO_REVIEWS = 'dataset_reviews_alicante.csv'

# ELCHE
ARCHIVO_ENTRADA = 'censo_restaurantes_elche.csv'
ARCHIVO_RESTAURANTES = 'dataset_restaurantes_elche.csv'
ARCHIVO_REVIEWS = 'dataset_reviews_elche.csv'

# VARIABLE DE CONTROL (Ponlo en False para descargar todo)
MODO_PRUEBA = False
CANTIDAD_PRUEBA = 5

URL_DETAILS = "https://maps.googleapis.com/maps/api/place/details/json"

CAMPOS = [
    'place_id', 'name', 'formatted_address', 'geometry', 'types', 
    'website', 'formatted_phone_number', 
    'rating', 'user_ratings_total', 'price_level', 'reviews', 'editorial_summary' 
]

def descargar_detalles():
    ids_a_procesar = []
    try:
        with open(ARCHIVO_ENTRADA, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                ids_a_procesar.append(row['place_id'])
    except FileNotFoundError:
        print(f"Error: No encuentro {ARCHIVO_ENTRADA}.")
        return

    if MODO_PRUEBA:
        print(f"MODO PRUEBA ACTIVADO: Solo descargaremos {CANTIDAD_PRUEBA} restaurantes.")
        ids_a_procesar = ids_a_procesar[:CANTIDAD_PRUEBA]

    print(f"Iniciando descarga detallada de {len(ids_a_procesar)} establecimientos...")
    
    cols_rest = ['place_id', 'name', 'address', 'lat', 'lng', 'types', 'rating', 
                 'user_ratings_total', 'price_level', 'website', 'phone', 'summary']
    
    cols_rev = ['place_id', 'author_name', 'rating', 'text', 'time', 'relative_time']

    with open(ARCHIVO_RESTAURANTES, 'w', newline='', encoding='utf-8-sig') as f_rest, \
         open(ARCHIVO_REVIEWS, 'w', newline='', encoding='utf-8-sig') as f_rev:
        
        writer_rest = csv.DictWriter(f_rest, fieldnames=cols_rest)
        writer_rev = csv.DictWriter(f_rev, fieldnames=cols_rev)
        
        writer_rest.writeheader()
        writer_rev.writeheader()

    count = 0
    for pid in ids_a_procesar:
        count += 1
        print(f"({count}/{len(ids_a_procesar)}) Descargando ID: {pid} ... ", end="")
        
        params = {
            'place_id': pid,
            'fields': ",".join(CAMPOS),
            'key': GOOGLE_API_KEY,
            'language': 'es'
        }
        
        try:
            response = requests.get(URL_DETAILS, params=params)
            data = response.json().get('result', {})
            
            loc = data.get('geometry', {}).get('location', {})
            
            fila_rest = {
                'place_id': data.get('place_id'),
                'name': data.get('name'),
                'address': data.get('formatted_address'),
                'lat': loc.get('lat'),
                'lng': loc.get('lng'),
                'types': ";".join(data.get('types', [])),
                'rating': data.get('rating'),
                'user_ratings_total': data.get('user_ratings_total'),
                'price_level': data.get('price_level'),
                'website': data.get('website'),
                'phone': data.get('formatted_phone_number'),
                'summary': data.get('editorial_summary', {}).get('overview') if data.get('editorial_summary') else None
            }
            
            with open(ARCHIVO_RESTAURANTES, 'a', newline='', encoding='utf-8-sig') as f_rest:
                writer_rest = csv.DictWriter(f_rest, fieldnames=cols_rest)
                writer_rest.writerow(fila_rest)
            
            reviews = data.get('reviews', [])
            with open(ARCHIVO_REVIEWS, 'a', newline='', encoding='utf-8-sig') as f_rev:
                writer_rev = csv.DictWriter(f_rev, fieldnames=cols_rev)
                for rev in reviews:
                    fila_rev = {
                        'place_id': pid, 
                        'author_name': rev.get('author_name'),
                        'rating': rev.get('rating'),
                        'text': rev.get('text', '').replace('\n', ' '), 
                        'time': rev.get('time'),
                        'relative_time': rev.get('relative_time_description')
                    }
                    writer_rev.writerow(fila_rev)
            
            print("OK")
            
        except Exception as e:
            print(f"Error: {e}")

    print("\nPROCESO COMPLETADO!")
    print(f"Datos guardados en '{ARCHIVO_RESTAURANTES}' y '{ARCHIVO_REVIEWS}'")

# --- EJECUCION ---
descargar_detalles()