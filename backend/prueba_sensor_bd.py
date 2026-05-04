import os
import json
import mysql.connector
from mysql.connector import Error
from pydantic import BaseModel
from typing import List
from datetime import datetime

# ==========================================
# 1. CONFIGURACIÓN DE RUTAS Y BD
# ==========================================
# Ruta absoluta solicitada
RUTA_JSON = r"C:\Users\k0nn0\OneDrive\Escritorio\Misc\Tec\8vo\IA\IctioMind\backend\mockup.json"

# Configuración de base de datos local
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "4p0l0123",
    "database": "IctioMind_BD",
    "port": 3306
}

# ==========================================
# 2. MODELOS DE DATOS (PYDANTIC)
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
# 3. LÓGICA DE PROCESAMIENTO
# ==========================================
def inyectar_lecturas_bd(payloads: List[PayloadSensor]) -> dict:
    conexion = None
    try:
        conexion = mysql.connector.connect(**DB_CONFIG)

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

    except Error as e:
        if conexion: conexion.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        if conexion and conexion.is_connected():
            conexion.close()

# ==========================================
# 4. EJECUCIÓN PRINCIPAL (LECTURA DE ARCHIVO)
# ==========================================
if __name__ == "__main__":
    print(f"📂 Buscando archivo en: {RUTA_JSON}")
    
    if not os.path.exists(RUTA_JSON):
        print(f"❌ Error: No se encontró el archivo JSON en la ruta especificada.")
    else:
        try:
            # Leer el archivo JSON
            with open(RUTA_JSON, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Convertir el contenido a modelos de Pydantic
            # Maneja tanto si el JSON es un objeto único como si es una lista []
            if isinstance(data, dict):
                lista_lecturas = [PayloadSensor(**data)]
            else:
                lista_lecturas = [PayloadSensor(**item) for item in data]

            # Inyectar en la BD
            resultado = inyectar_lecturas_bd(lista_lecturas)
            print(f"✅ Proceso terminado: {resultado}")

        except Exception as e:
            print(f"❌ Ocurrió un error inesperado: {e}")