import json
import math
import random
from datetime import datetime, timedelta

def generar_dataset_alto_estres(horas_totales=2000, archivo_salida="telemetria_sintetica_v3.json"):
    print(f"🧬 Generando Ecosistema de Alto Estrés para entrenamiento ({horas_totales} horas)...")
    
    fecha_inicio = datetime(2026, 1, 1, 0, 0, 0)
    ph_actual = 7.50
    dureza_actual = 150.0
    registros = []
    
    for hora in range(horas_totales):
        fecha_actual = fecha_inicio + timedelta(hours=hora)
        
        # Comportamiento normal (Ondas)
        temp_actual = 25.0 + 2.0 * math.sin(hora * 2 * math.pi / 24) + random.gauss(0, 0.2)
        o2_actual = 7.0 + 1.0 * math.sin((hora + 12) * 2 * math.pi / 24) + random.gauss(0, 0.15)
        
        # ==========================================================
        # EL SECRETO: INYECCIÓN MASIVA DE CRISIS (25% del tiempo)
        # Cada 200 horas, provocamos una crisis de 50 horas seguidas.
        # ==========================================================
        ciclo = hora % 200
        if 120 <= ciclo <= 170:
            horas_en_crisis = ciclo - 120
            # La temperatura sube agresivamente
            temp_actual += (horas_en_crisis * 0.1) 
            # El oxígeno se desploma brutalmente (hasta niveles de 2.0 o 1.0)
            o2_actual -= (horas_en_crisis * 0.12)
            # El pH se acidifica por mortandad
            ph_actual -= 0.02
            
        # Asegurar límites físicos realistas
        o2_actual = max(1.0, o2_actual) # Permitimos que llegue a niveles letales (1.0)
        temp_actual = min(36.0, temp_actual)
        ph_actual = max(5.0, min(9.0, ph_actual))
        dureza_actual = max(50.0, dureza_actual)

        # Tendencias a largo plazo
        ph_actual = ph_actual - 0.002 + random.gauss(0, 0.005)
        dureza_actual = dureza_actual + 0.2 + random.gauss(0, 0.5)
        
        if hora > 0 and hora % 168 == 0: # Recambio de agua semanal
            ph_actual = 7.5 + random.gauss(0, 0.1)
            dureza_actual = 150.0 + random.gauss(0, 2)

        registros.append({
            "metadata": {
                "id_estanque": 1,
                "timestamp": fecha_actual.strftime('%Y-%m-%d %H:%M:%S'),
                "ph_actual": round(ph_actual, 2),
                "temperatura_agua_actual": round(temp_actual, 2),
                "oxigeno_disuelto_actual": round(o2_actual, 2),
                "dureza_actual": round(dureza_actual, 2)
            }
        })
        
    with open(archivo_salida, 'w', encoding='utf-8') as f:
        json.dump(registros, f, indent=2)
        
    print(f"✅ ¡Éxito! Archivo generado: {archivo_salida}")

if __name__ == "__main__":
    generar_dataset_alto_estres()