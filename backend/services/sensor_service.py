import os
import sys

# 1. Obtenemos la ruta absoluta de este archivo
ruta_actual = os.path.abspath(__file__)

# 2. Subimos dos niveles para llegar a la carpeta "Backend"
ruta_backend = os.path.dirname(os.path.dirname(ruta_actual))

# 3. La agregamos al path global de Python
sys.path.append(ruta_backend)

import json
from pydantic import BaseModel
from typing import List
from datetime import datetime

# Importamos nuestra conexión segura desde el archivo de configuración
from config.database import get_db_connection

# ==========================================
# 1. MODELOS DE DATOS (PYDANTIC)
# ==========================================
class SensorMetadata(BaseModel):
    id_sensor: int
    timestamp: datetime
    ph_actual: float
    temperatura_agua_actual: float
    oxigeno_disuelto_actual: float
    dureza_actual: float

class PayloadSensor(BaseModel):
    metadata: SensorMetadata

# ==========================================
# 2. LÓGICA DE PROCESAMIENTO (Capa de Servicio)
# ==========================================
def inyectar_lecturas_bd(payloads: List[PayloadSensor]) -> dict:
    conexion = None
    try:
        # AQUÍ ESTÁ LA MAGIA: Tomamos una conexión prestada del Pool
        conexion = get_db_connection()
        
        if not conexion:
            return {"status": "error", "message": "No se pudo obtener conexión del pool."}

        if conexion.is_connected():
            with conexion.cursor(dictionary=True) as cursor:
                registros_insertados = 0

                for item in payloads:
                    datos = item.metadata

                    # PASO A: Buscar Estanque
                    query_sensor = "SELECT id_estanque_actual FROM sensores_inventario WHERE id_sensor = %s"
                    cursor.execute(query_sensor, (datos.id_sensor,))
                    resultado_sensor = cursor.fetchone()

                    if not resultado_sensor or resultado_sensor['id_estanque_actual'] is None:
                        print(f"⚠️ El sensor {datos.id_sensor} no tiene estanque asignado. Omitiendo.")
                        continue
                    
                    id_estanque = resultado_sensor['id_estanque_actual']

                    # PASO B: Inserción
                    query_insert = """
                        INSERT INTO lecturas_telemetria 
                        (fecha_hora, id_sensor, id_estanque, temperatura, oxigeno_disuelto, ph, dureza) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """
                    
                    valores = (
                        datos.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                        datos.id_sensor,
                        id_estanque,
                        datos.temperatura_agua_actual,
                        datos.oxigeno_disuelto_actual,
                        datos.ph_actual,
                        datos.dureza_actual
                    )

                    cursor.execute(query_insert, valores)
                    registros_insertados += 1

                conexion.commit()
                return {"status": "success", "insertados": registros_insertados}

    except Exception as e:
        if conexion: conexion.rollback()
        return {"status": "error", "message": str(e)}
    
    finally:
        # En el sistema de Pool, 'close()' NO destruye la conexión, 
        # simplemente la limpia y la devuelve al pool para que otro archivo la use.
        if conexion and conexion.is_connected():
            conexion.close()

# ==========================================
# 3. EJECUCIÓN PRINCIPAL (SIMULACIÓN DE CRISIS)
# ==========================================
if __name__ == "__main__":
    # Ruta de tu archivo de datos sintéticos
    RUTA_JSON = r"C:\Users\k0nn0\OneDrive\Escritorio\Misc\Tec\8vo\IA\IctioMind\mockup.json"
    
    print(f"📂 Buscando archivo en: {RUTA_JSON}")
    
    if not os.path.exists(RUTA_JSON):
        print(f"❌ Error: No se encontró el archivo JSON en la ruta especificada.")
    else:
        try:
            # Leer el archivo JSON
            with open(RUTA_JSON, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Convertir el contenido a modelos de Pydantic
            if isinstance(data, dict):
                lista_lecturas = [PayloadSensor(**data)]
            else:
                lista_lecturas = [PayloadSensor(**item) for item in data]

            # Inyectar en la BD
            print("🚀 Iniciando inyección de datos sintéticos...")
            resultado = inyectar_lecturas_bd(lista_lecturas)
            print(f"✅ Proceso terminado: {resultado}")

        except Exception as e:
            print(f"❌ Ocurrió un error inesperado: {e}")