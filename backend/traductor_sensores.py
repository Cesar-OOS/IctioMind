import os
import mysql.connector
from mysql.connector import Error
from pydantic import BaseModel
from typing import List
from datetime import datetime

# ==========================================
# 1. MODELOS DE DATOS (PYDANTIC)
# ==========================================
# Estos modelos validan y "traducen" el JSON entrante automáticamente

class SensorMetadata(BaseModel):
    id_sensor: int
    timestamp: datetime
    ph_actual: float
    temperatura_agua_actual: float
    oxigeno_disuelto_actual: float
    dureza_actual: float

class PayloadSensor(BaseModel):
    # Esto le dice a Python que el JSON tiene una llave "metadata" que contiene los datos
    metadata: SensorMetadata

# ==========================================
# 2. LÓGICA DE BASE DE DATOS (EL TRADUCTOR)
# ==========================================
def inyectar_lecturas_bd(payloads: List[PayloadSensor]) -> dict:
    """
    Recibe una lista de lecturas del sensor, busca el estanque de cada sensor,
    y guarda la información traducida en la tabla lecturas_telemetria.
    """
    conexion = None
    try:
        # 1. Conexión a la BD (Usando variables de entorno para Docker)
        conexion = mysql.connector.connect(
            host=os.getenv("DB_HOST", "ictiomind_db"),
            user=os.getenv("DB_USER", "ictio_admin"),
            password=os.getenv("DB_PASSWORD", "ictio_password"),
            database=os.getenv("DB_NAME", "ictiomind_db"),
            port=3306
        )

        if conexion.is_connected():
            with conexion.cursor(dictionary=True) as cursor:
                registros_insertados = 0

                # Recorremos la lista del JSON (por si el sensor envía varias lecturas de golpe)
                for item in payloads:
                    datos = item.metadata

                    # --- PASO A: DESCUBRIR EL ESTANQUE ---
                    query_sensor = "SELECT id_estanque_actual FROM sensores_inventario WHERE id_sensor = %s"
                    cursor.execute(query_sensor, (datos.id_sensor,))
                    resultado_sensor = cursor.fetchone()

                    # Si el sensor no está registrado o no tiene estanque asignado, evitamos que la BD colapse
                    if not resultado_sensor or resultado_sensor['id_estanque_actual'] is None:
                        print(f"⚠️ Alerta: El sensor {datos.id_sensor} no está asignado a ningún estanque. Omitiendo lectura.")
                        continue
                    
                    id_estanque = resultado_sensor['id_estanque_actual']

                    # --- PASO B: TRADUCCIÓN E INYECCIÓN ---
                    # Preparamos la tupla mapeando los nombres del JSON con las columnas de tu BD
                    query_insert = """
                        INSERT INTO lecturas_telemetria 
                        (fecha_hora, id_sensor, id_estanque, temperatura, oxigeno_disuelto, ph, dureza) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """
                    
                    valores = (
                        datos.timestamp.strftime('%Y-%m-%d %H:%M:%S'), # Formato DATETIME estricto
                        datos.id_sensor,
                        id_estanque,                      # Obtenido en el PASO A
                        datos.temperatura_agua_actual,    # Traducido
                        datos.oxigeno_disuelto_actual,    # Traducido
                        datos.ph_actual,                  # Traducido
                        datos.dureza_actual               # Traducido
                    )

                    cursor.execute(query_insert, valores)
                    registros_insertados += 1

                # Confirmamos los cambios en la BD
                conexion.commit()
                return {"status": "success", "insertados": registros_insertados}

    except Error as e:
        # Si ocurre un error, hacemos rollback para no dejar datos a medias
        if conexion:
            conexion.rollback()
        raise Exception(f"Fallo en la inyección SQL: {e}")
        
    finally:
        # Siempre cerramos la conexión
        if conexion and conexion.is_connected():
            conexion.close()