import mysql.connector
from mysql.connector import Error
import os

# Esta función ahora es segura, maneja sus propias conexiones y usa variables de entorno
def analizar_tendencia_estanque(id_estanque):
    conexion = None
    try:
        # Extraemos las credenciales de las variables de entorno (Configuradas en Docker)
        conexion = mysql.connector.connect(
            host=os.getenv("DB_HOST", "ictiomind_db"), # 'ictiomind_db' es el default en Docker
            user=os.getenv("DB_USER", "ictio_admin"),
            password=os.getenv("DB_PASSWORD", "ictio_password"),
            database=os.getenv("DB_NAME", "ictiomind_db"),
            port=3306
        )

        if conexion.is_connected():
            # Usamos un bloque 'with' para asegurar que el cursor se cierre pase lo que pase
            with conexion.cursor(dictionary=True) as cursor:
                query = """
                    SELECT fecha_hora, temperatura, oxigeno_disuelto, ph, dureza 
                    FROM lecturas_telemetria 
                    WHERE id_estanque = %s 
                    ORDER BY fecha_hora DESC 
                    LIMIT 6
                """
                cursor.execute(query, (id_estanque,))
                resultados = cursor.fetchall() 

            # Validación de historial mínimo
            if len(resultados) < 6:
                print(f"Acumulando historial del estanque {id_estanque}. Datos actuales: {len(resultados)}/6")
                return None
            
            # Asignación lógica
            actual = resultados[0]          
            anterior_inmediato = resultados[1] 
            hace_una_hora = resultados[5]      
            
            # Cálculo de deltas y promedios (La lógica matemática original se mantiene intacta)
            diccionario_tendencias = {
                "estanque": id_estanque,
                "fecha_analisis": str(actual['fecha_hora']),
                
                # Temperatura
                "temperatura_actual": float(actual['temperatura']),
                "delta_temperatura_10m": round(float(actual['temperatura'] - anterior_inmediato['temperatura']), 2),
                "delta_temperatura_1h": round(float(actual['temperatura'] - hace_una_hora['temperatura']), 2),
                "promedio_temperatura_1h": round(sum(float(fila['temperatura']) for fila in resultados) / len(resultados), 2),

                # Oxígeno
                "oxigeno_disuelto_actual": float(actual['oxigeno_disuelto']),
                "delta_oxigeno_disuelto_10m": round(float(actual['oxigeno_disuelto'] - anterior_inmediato['oxigeno_disuelto']), 2),
                "delta_oxigeno_disuelto_1h": round(float(actual['oxigeno_disuelto'] - hace_una_hora['oxigeno_disuelto']), 2),
                "promedio_oxigeno_disuelto_1h": round(sum(float(fila['oxigeno_disuelto']) for fila in resultados) / len(resultados), 2),
                
                # pH
                "ph_actual": float(actual['ph']),
                "delta_ph_10m": round(float(actual['ph'] - anterior_inmediato['ph']), 2),
                "delta_ph_1h": round(float(actual['ph'] - hace_una_hora['ph']), 2),
                "promedio_ph_1h": round(sum(float(fila['ph']) for fila in resultados) / len(resultados), 2),

                # Dureza
                "dureza_actual": float(actual['dureza']),
                "delta_dureza_10m": round(float(actual['dureza'] - anterior_inmediato['dureza']), 2),
                "delta_dureza_1h": round(float(actual['dureza'] - hace_una_hora['dureza']), 2),
                "promedio_dureza_1h": round(sum(float(fila['dureza']) for fila in resultados) / len(resultados), 2)
            }

            return diccionario_tendencias

    except Error as e:
        print(f"Error crítico al conectar con MariaDB: {e}")
        return None
        
    finally:
        # Esto asegura que la conexión siempre se cierre, liberando memoria del servidor
        if conexion is not None and conexion.is_connected():
            conexion.close()

# Bloque de prueba (Solo se ejecuta si corres este archivo directamente)
if __name__ == "__main__":
    import json
    
    # Para probar en tu computadora ANTES de subirlo a Docker, tendrías que definir temporalmente:
    # os.environ["DB_HOST"] = "localhost"
    
    resultados = analizar_tendencia_estanque(1)
    
    if resultados:
        print("--- CARACTERÍSTICAS PARA IA GENERADAS EXITOSAMENTE ---")
        print(json.dumps(resultados, indent=4))