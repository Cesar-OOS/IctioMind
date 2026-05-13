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
# Modificamos la función para aceptar una lista de estanques a limpiar
def inyectar_lecturas_bd(payloads: List[PayloadSensor], estanques_a_limpiar: List[int] = None) -> dict:
    conexion = None
    try:
        # Tomamos una conexión prestada del Pool
        conexion = get_db_connection()
        
        if not conexion:
            return {"status": "error", "message": "No se pudo obtener conexión del pool."}

        if conexion.is_connected():
            with conexion.cursor(dictionary=True) as cursor:
                
                # ---------------------------------------------------------
                # NUEVO: LIMPIEZA AUTOMÁTICA ANTES DE INYECTAR
                # ---------------------------------------------------------
                if estanques_a_limpiar:
                    # Creamos la sentencia SQL dinámicamente (%s, %s)
                    placeholders = ', '.join(['%s'] * len(estanques_a_limpiar))
                    query_limpieza = f"DELETE FROM lecturas_telemetria WHERE id_estanque IN ({placeholders})"
                    cursor.execute(query_limpieza, tuple(estanques_a_limpiar))
                    print(f"🧹 Limpieza completada: Se borró el historial previo de los estanques {estanques_a_limpiar}")
                # ---------------------------------------------------------

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

            # Confirmamos tanto el borrado como la nueva inserción
            conexion.commit()
            return {"status": "success", "insertados": registros_insertados}

    except Exception as e:
        if conexion: conexion.rollback() # Si algo falla, deshace el borrado y la inserción
        return {"status": "error", "message": str(e)}
    
    finally:
        if conexion and conexion.is_connected():
            conexion.close()

# ==========================================
# 3. EJECUCIÓN PRINCIPAL (SIMULACIÓN DE CRISIS)
# ==========================================
if __name__ == "__main__":
    # Ruta de tu archivo de datos sintéticos
    RUTA_JSON = r"C:\Users\k0nn0\OneDrive\Escritorio\Misc\Tec\8vo\IA\IctioMind\anoxia.json"
    
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

            # Inyectar en la BD y decirle qué estanques resetear
            print("🚀 Iniciando limpieza e inyección de datos sintéticos...")
            
            # AQUÍ ES DONDE LE INDICAMOS LOS ESTANQUES A BORRAR (1 y 2)
            resultado = inyectar_lecturas_bd(lista_lecturas, estanques_a_limpiar=[1, 2])
            
            print(f"✅ Proceso terminado: {resultado}")

        except Exception as e:
            print(f"❌ Ocurrió un error inesperado: {e}")