import csv

# --- 1. DEFINICION DE LA CAJA (BOUNDING BOX) PARA ELCHE ---
LAT_MIN = 38.2400  # Sur (Hospital Vinalopo / Cortijo)
LAT_MAX = 38.2900  # Norte (Universidad MH / Poligono)
LNG_MIN = -0.7400  # Oeste (Centro Comercial / Estadio)
LNG_MAX = -0.6600  # Este (Torrellano / IFA)

# --- 2. CONFIGURACION DE LA MALLA (Alta densidad) ---
STEP_LAT = 0.003 
STEP_LNG = 0.004 

def generar_malla():
    puntos = []
    
    lat = LAT_MIN
    while lat <= LAT_MAX:
        lng = LNG_MIN
        while lng <= LNG_MAX:
            puntos.append([lat, lng])
            lng += STEP_LNG
        lat += STEP_LAT
        
    return puntos

# --- 3. EJECUCION ---
lista_puntos = generar_malla()

print("Malla generada sobre Elche.")
print(f"Puntos calculados: {len(lista_puntos)}")

# --- 4. GUARDAR CSV ---
nombre_archivo = 'malla_elche.csv'
try:
    with open(nombre_archivo, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['lat', 'lng'])
        writer.writerows(lista_puntos)
        
    print(f"Archivo '{nombre_archivo}' creado correctamente.")
    coste = len(lista_puntos) * 0.032
    print(f"Coste estimado para el censo de Elche: ${coste:.2f} USD")

except Exception as e:
    print(f"Error al escribir el archivo: {e}")