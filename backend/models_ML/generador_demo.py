import json
from datetime import datetime, timedelta

def generar_datos_demo():
    print("🎬 Preparando datos sintéticos para Demostración IctioMind...")
    
    ahora = datetime.now()
    registros = []

    # ====================================================================
    # MATEMÁTICAS DE LA DEMOSTRACIÓN:
    # El modelo de IA (RandomForest) calcula la inercia usando 5 lags.
    # ====================================================================

    # ESTANQUE 1: Caída libre en picada. 
    # El oxígeno actual será de 4.2 (Aún no es 4.0, el pez sigue vivo).
    # Pero la IA verá que viene cayendo a razón de -0.7 por hora y 
    # predecirá que en 1 hora estará en ~3.5 (Alerta Roja + WhatsApp).
    oxigeno_estanque_1 = [7.5, 6.8, 6.0, 5.2, 4.8, 4.2]

    # ESTANQUE 2: Fluctuación estabilizándose.
    # El oxígeno actual será de 5.1.
    # La IA verá que bajó, pero la caída se está frenando. 
    # Predecirá ~4.8 (Cae por debajo de 5.0, activa Alerta Amarilla, pero NO WhatsApp).
    oxigeno_estanque_2 = [7.0, 6.4, 5.9, 5.5, 5.2, 5.1]

    # Generamos 6 registros hacia atrás (para tener los 5 lags + el actual)
    for i in range(6):
        # Restamos horas hacia el pasado, de modo que el último registro sea el "Ahora"
        tiempo_simulado = ahora - timedelta(hours=(5 - i))
        timestamp_str = tiempo_simulado.strftime('%Y-%m-%d %H:%M:%S')

        # Insertamos Estanque 1 (Riesgo Crítico)
        registros.append({
            "metadata": {
                "id_sensor": 1,      # <--- AGREGAMOS ESTA LÍNEA
                "id_estanque": 1,
                "timestamp": timestamp_str,
                "ph_actual": 7.2,
                "temperatura_agua_actual": 25.5,
                "oxigeno_disuelto_actual": oxigeno_estanque_1[i],
                "dureza_actual": 140.0 
            }
        })

        # Insertamos Estanque 2 (Riesgo Moderado)
        registros.append({
            "metadata": {
                "id_sensor": 2,      # <--- AGREGAMOS ESTA LÍNEA
                "id_estanque": 2,
                "timestamp": timestamp_str,
                "ph_actual": 7.2, 
                "temperatura_agua_actual": 25.5, 
                "oxigeno_disuelto_actual": oxigeno_estanque_2[i],
                "dureza_actual": 140.0 
            }
        })

    # Guardamos el archivo JSON
    nombre_archivo = "anoxia.json"
    with open(nombre_archivo, "w", encoding="utf-8") as f:
        json.dump(registros, f, indent=4)
        
    print(f"✅ ¡Archivo '{nombre_archivo}' generado con éxito!")
    print("Inyecta este archivo usando tu sensor_service.py para iniciar la demostración.")

if __name__ == "__main__":
    generar_datos_demo()