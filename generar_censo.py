import csv
import requests
import time
import os
from secrets import GOOGLE_API_KEY

# --- 1. CONFIGURACION ---

# ELCHE
ARCHIVO_MALLA = 'malla_elche.csv'
ARCHIVO_SALIDA = 'censo_restaurantes_elche.csv'

# ALICANTE
#ARCHIVO_MALLA = 'malla_alicante.csv'
#ARCHIVO_SALIDA = 'censo_restaurantes_alicante.csv'

URL_NEARBY = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

# Radio de busqueda reducido para evitar el limite de 60 resultados en zonas densas
RADIUS = 250 
TYPE = 'restaurant'

def realizar_censo():
    restaurantes_unicos = set()
    datos_basicos = {} 
    
    puntos = []
    try:
        with open(ARCHIVO_MALLA, 'r') as f:
            reader = csv.reader(f)
            next(reader) 
            for row in reader:
                puntos.append({'lat': row[0], 'lng': row[1]})
    except FileNotFoundError:
        print("Error: No encuentro 'malla_alicante.csv'. Ejecuta el script anterior primero.")
        return

    print(f"Iniciando Censo en {len(puntos)} puntos de busqueda...")

    total_puntos = len(puntos)
    
    for i, punto in enumerate(puntos):
        lat, lng = punto['lat'], punto['lng']
        print(f"Punto {i+1}/{total_puntos} ({lat}, {lng})... ", end="", flush=True)
        
        params = {
            'location': f"{lat},{lng}",
            'radius': RADIUS,
            'type': TYPE,
            'key': GOOGLE_API_KEY
        }
        
        while True:
            try:
                response = requests.get(URL_NEARBY, params=params)
                data = response.json()
                results = data.get('results', [])
                
                for sitio in results:
                    pid = sitio.get('place_id')
                    if pid:
                        restaurantes_unicos.add(pid)
                        datos_basicos[pid] = {
                            'place_id': pid,
                            'name': sitio.get('name'),
                            'lat': sitio.get('geometry', {}).get('location', {}).get('lat'),
                            'lng': sitio.get('geometry', {}).get('location', {}).get('lng'),
                            'vicinity': sitio.get('vicinity')
                        }
                
                token = data.get('next_page_token')
                if token:
                    time.sleep(2) 
                    params = {'pagetoken': token, 'key': GOOGLE_API_KEY}
                else:
                    break 
                    
            except Exception as e:
                print(f"Error: {e}")
                break
        
        print(f"Total acumulado: {len(restaurantes_unicos)}")

    print(f"\nCENSO TERMINADO. Se han encontrado {len(restaurantes_unicos)} restaurantes UNICOS.")
    
    with open(ARCHIVO_SALIDA, 'w', newline='', encoding='utf-8') as f:
        campos = ['place_id', 'name', 'lat', 'lng', 'vicinity']
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        
        for pid in restaurantes_unicos:
            writer.writerow(datos_basicos[pid])
            
    print(f"Lista guardada en '{ARCHIVO_SALIDA}'")

# --- EJECUCION ---
realizar_censo()