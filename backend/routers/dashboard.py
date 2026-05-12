import os
import sys
from fastapi import APIRouter, HTTPException

# Agregamos la ruta para que encuentre 'config'
ruta_actual = os.path.abspath(__file__)
ruta_backend = os.path.dirname(os.path.dirname(ruta_actual))
if ruta_backend not in sys.path:
    sys.path.append(ruta_backend)

from config.database import get_db_connection

# Creamos el router
router = APIRouter(
    prefix="/api/dashboard",
    tags=["Dashboard"]
)

# CORRECCIÓN: Usamos el decorador directamente sobre 'router'
@router.get("/estado-actual")
async def obtener_estado_estanques():
    """
    Obtiene la última lectura de cada estanque registrado.
    Esto es lo que React usará para mostrar las tarjetas de estado.
    """
    conexion = get_db_connection()
    if not conexion:
        raise HTTPException(status_code=500, detail="Error de conexión a la base de datos")

    try:
        with conexion.cursor(dictionary=True) as cursor:
            query = """
                SELECT t.*, e.nombre_ubicacion 
                FROM lecturas_telemetria t
                JOIN (
                    SELECT id_estanque, MAX(id_lectura) as max_id
                    FROM lecturas_telemetria
                    GROUP BY id_estanque
                ) m ON t.id_lectura = m.max_id
                JOIN estanques e ON t.id_estanque = e.id_estanque
            """
            cursor.execute(query)
            resultados = cursor.fetchall()
            return resultados
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conexion.is_connected():
            conexion.close()