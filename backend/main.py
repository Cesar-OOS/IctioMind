from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import mysql.connector
from mysql.connector import Error
import os

app = FastAPI(title="IctioMind Backend", version="1.1")

class LecturaSensor(BaseModel):
    id_sensor: str
    id_estanque: int
    temperatura: float
    ph: float
    oxigeno_disuelto: float
    dureza: float

# --- 1. NUEVA FUNCIÓN: ZONA DE CONFORT COMPARTIDA ---
def obtener_limites_estanque(id_estanque: int):
    """
    Se conecta a MariaDB, busca todas las especies en el estanque y calcula 
    los límites vitales. Si hay peces con distintas necesidades, calcula 
    el rango más estricto para que todos sobrevivan.
    """
    try:
        conexion = mysql.connector.connect(
            host=os.getenv("DB_HOST", "ictiomind_db"),
            user=os.getenv("DB_USER", "ictio_admin"),
            password=os.getenv("DB_PASSWORD", "ictio_password"),
            database=os.getenv("DB_NAME", "ictiomind_db"),
            port=3306
        )
        
        if conexion.is_connected():
            with conexion.cursor(dictionary=True) as cursor:
                # Magia SQL: MAX(temp_min) asegura que no bajemos más del límite del pez más friolento
                # MIN(temp_max) asegura que no subamos más del límite del pez más caluroso
                query = """
                    SELECT 
                        MAX(c.temp_min) as temp_min_critica, 
                        MIN(c.temp_max) as temp_max_critica, 
                        MAX(c.oxigeno_min) as oxigeno_min_critico
                    FROM habitantes_estanques h
                    JOIN catalogo_especies c ON h.id_especie = c.id_especie
                    WHERE h.id_estanque = %s
                """
                cursor.execute(query, (id_estanque,))
                limites = cursor.fetchone()
                
                # Si el estanque está vacío o no existe, devolvemos límites por defecto genéricos
                if not limites or limites['temp_min_critica'] is None:
                    return {"temp_min_critica": 20.0, "temp_max_critica": 30.0, "oxigeno_min_critico": 4.0}
                
                # Convertimos valores Decimal de SQL a Float de Python
                return {
                    "temp_min_critica": float(limites['temp_min_critica']),
                    "temp_max_critica": float(limites['temp_max_critica']),
                    "oxigeno_min_critico": float(limites['oxigeno_min_critico'])
                }
    except Error as e:
        print(f"Error al consultar límites en BD: {e}")
        return {"temp_min_critica": 20.0, "temp_max_critica": 30.0, "oxigeno_min_critico": 4.0} # Fallback de seguridad
    finally:
        if 'conexion' in locals() and conexion.is_connected():
            conexion.close()

# --- FUNCIONES SIMULADAS (Clima y Alertas) ---
def obtener_pronostico_clima():
    return {"alerta": True, "descripcion": "Lluvia intensa y bajada de temperatura", "temp_esperada": 18.0}

def enviar_alerta_whatsapp(mensaje: str):
    print(f"📱 [WHATSAPP ENVIADO]: {mensaje}")

def notificar_frontend_web(mensaje: str):
    print(f"💻 [WEB SOCKET ALERT]: {mensaje}")

# --- 2. MODIFICACIÓN DEL CEREBRO (IA) ---
def evaluar_con_modelo_ia(lectura: LecturaSensor, clima: dict, limites: dict):
    """
    Ahora la IA evalúa basándose en los límites dinámicos específicos del estanque.
    """
    riesgo = False
    motivo = ""

    # Usamos los límites obtenidos de la base de datos
    temp_min_segura = limites["temp_min_critica"]
    oxigeno_min_seguro = limites["oxigeno_min_critico"]

    # Si el agua está en el límite bajo y el clima empeorará
    if lectura.temperatura <= temp_min_segura and clima["temp_esperada"] < temp_min_segura:
        riesgo = True
        motivo = f"[ESTANQUE {lectura.id_estanque}] Riesgo de hipotermia: Agua a {lectura.temperatura}°C (Límite vital: {temp_min_segura}°C) y se espera {clima['descripcion']}."
    
    # Si el oxígeno baja del límite de esa especie en particular
    elif lectura.oxigeno_disuelto < oxigeno_min_seguro:
        riesgo = True
        motivo = f"[ESTANQUE {lectura.id_estanque}] Asfixia inminente: Oxígeno a {lectura.oxigeno_disuelto} mg/L (Mínimo requerido: {oxigeno_min_seguro} mg/L)."

    return riesgo, motivo

# --- 3. AJUSTE FINAL DEL ENDPOINT ---
@app.post("/api/telemetria/ingesta")
async def recibir_datos_sensor(lectura: LecturaSensor, background_tasks: BackgroundTasks):
    try:
        # 1. Consultar el clima externo
        clima_actual = obtener_pronostico_clima()

        # 2. Obtener la "Zona de Confort" específica de los peces de ESTE estanque
        limites_estanque = obtener_limites_estanque(lectura.id_estanque)

        # 3. Pasar los datos, el clima y los límites específicos a la IA
        hay_riesgo, mensaje_alerta = evaluar_con_modelo_ia(lectura, clima_actual, limites_estanque)

        # 4. Enviar Alertas asíncronas
        if hay_riesgo:
            background_tasks.add_task(enviar_alerta_whatsapp, mensaje_alerta)
            background_tasks.add_task(notificar_frontend_web, mensaje_alerta)
            return {"status": "success", "analisis": "ALERTA DISPARADA", "detalle": mensaje_alerta}

        return {"status": "success", "analisis": f"Estanque {lectura.id_estanque} estable. Limites dinámicos respetados."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))