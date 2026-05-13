from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Importación de nuestros servicios (Las piezas del rompecabezas)
from services.clima_service import obtener_pronostico_evaluado
from services.alerta_service import enviar_alerta_whatsapp
from services.ia_service import evaluar_estanque_con_ia
from routers.dashboard import router as dashboard_router
from config.database import get_db_connection # Asegúrate de importar esto arriba

from datetime import datetime, timedelta

# ==========================================
# 1. CONFIGURACIÓN DE LA APP
# ==========================================
app = FastAPI(
    title="IctioMind: Cerebro Predictivo",
    description="API Central para la gestión predictiva de acuicultura local.",
    version="2.0.0"
)

# Configuración de seguridad CORS para conectar con React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluimos el router del dashboard que ya teníamos
app.include_router(dashboard_router)

# ==========================================
# 2. RUTA MAESTRA (EL ORQUESTADOR)
# ==========================================
@app.get("/api/v1/analisis-integral/{id_estanque}")
async def obtener_analisis_completo(id_estanque: int, background_tasks: BackgroundTasks):
    """
    Este es el endpoint que llamará tu Frontend.
    Realiza el flujo completo: IA + CLIMA + ALERTAS.
    """
    try:
        # PASO 1: Ejecutar el Cerebro Predictivo (IA)
        # Esto ya trae las últimas 5 lecturas de la BD y predice las 4 variables
        analisis_ia = evaluar_estanque_con_ia(id_estanque)
        
        if "error" in analisis_ia:
            raise HTTPException(status_code=500, detail=analisis_ia["error"])
        
        if analisis_ia.get("status") == "info":
            return analisis_ia # Retorna mensaje de que faltan lecturas

        # PASO 2: Consultar el Clima de Zacatepec
        analisis_clima = obtener_pronostico_evaluado()

        # PASO 3: Gestión de Alertas Críticas (Twilio)
        # Usamos BackgroundTasks para que el usuario no tenga que esperar a que el 
        # mensaje se envíe para ver los datos en pantalla.
        if analisis_ia.get("disparar_whatsapp"):
            mensaje_alerta = f"ESTANQUE {id_estanque}: {analisis_ia['estado']}. {analisis_ia['recomendacion_ia']}"
            background_tasks.add_task(enviar_alerta_whatsapp, mensaje_alerta)

        # PASO 4: Empaquetar todo para el Frontend (React)
        return {
            "id_estanque": id_estanque,
            "especies": analisis_ia.get("especies", "Sin datos"), # <-- AGREGADO
            "timestamp_analisis": analisis_ia.get("timestamp_servidor"),
            "diagnostico_ia": {
                "estado_salud": analisis_ia["estado"],
                "porcentaje_salud": analisis_ia["salud_porcentaje"],
                "color_sugerido": analisis_ia["color_grafica"],
                "recomendacion": analisis_ia["recomendacion_ia"],
                "predicciones_futuras": analisis_ia["predicciones"],
                "historial_grafica": analisis_ia.get("historial_grafica", []) # <-- LA PIEZA FALTANTE DE LA GRÁFICA
            },
            "meteorologia": {
                "alerta_climatica": analisis_clima["alerta_activa"],
                "resumen_5_dias": analisis_clima["pronostico_5_dias"]
            },
            "status": "success"
        }

    except Exception as e:
        print(f"❌ Error en el Orquestador: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
# ==========================================
# 3. RUTA PARA OBTENER EL DASHBOARD COMPLETO (TODOS LOS ESTANQUES)
# ==========================================
# Asegúrate de que BackgroundTasks esté importado arriba en tu main.py:
# from fastapi import FastAPI, HTTPException, BackgroundTasks

historial_alertas_whatsapp = {}

@app.get("/api/v1/dashboard-general")
async def obtener_dashboard_completo(background_tasks: BackgroundTasks):
    """
    Escanea la base de datos para ver cuántos estanques hay,
    devuelve el análisis de IA para todos ellos y dispara alertas si es necesario.
    """
    conexion = get_db_connection()
    if not conexion:
        raise HTTPException(status_code=500, detail="Sin conexión a BD")

    try:
        with conexion.cursor(dictionary=True) as cursor:
            # Descubrimos todos los estanques registrados
            cursor.execute("SELECT id_estanque, nombre_ubicacion FROM estanques")
            estanques_db = cursor.fetchall()

        resultados_totales = []
        for estanque in estanques_db:
            id_est = estanque['id_estanque']
            analisis = evaluar_estanque_con_ia(id_est)
            
            if "error" not in analisis and analisis.get("status") != "info":
                analisis['nombre_ubicacion'] = estanque['nombre_ubicacion']
                resultados_totales.append(analisis)

                # ======================================================
                # EL GATILLO DE WHATSAPP CON COOLDOWN
                # ======================================================
                if analisis.get("disparar_whatsapp"):
                    ahora = datetime.now()
                    ultima_vez_enviado = historial_alertas_whatsapp.get(id_est)

                    # REGLA: Si nunca se ha enviado, o si ya pasó 1 HORA desde el último mensaje
                    if not ultima_vez_enviado or (ahora - ultima_vez_enviado) > timedelta(minutes=60):
                        
                        mensaje_alerta = f"🚨 ALERTA GENERAL - ESTANQUE {id_est} 🚨\n{analisis['estado']}.\nAcción requerida: {analisis['recomendacion_ia']}"
                        
                        def disparar_y_loguear(msj):
                            respuesta = enviar_alerta_whatsapp(msj)
                            print(f"📱 Estado Twilio: {respuesta}")

                        background_tasks.add_task(disparar_y_loguear, mensaje_alerta)
                        
                        # Registramos la hora de este envío para bloquear futuros spams
                        historial_alertas_whatsapp[id_est] = ahora
                    else:
                        minutos_restantes = 60 - int((ahora - ultima_vez_enviado).total_seconds() / 60)
                        print(f"⏳ Alerta para Estanque {id_est} silenciada. Siguiente aviso en {minutos_restantes} min.")

        return {"status": "success", "estanques": resultados_totales}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conexion.is_connected():
            conexion.close()

# ==========================================
# 4. RUTA DE INICIO
# ==========================================
@app.get("/")
def home():
    return {
        "mensaje": "IctioMind Backend está Online",
        "docs": "/docs",
        "endpoints_clave": [
            "/api/v1/analisis-integral/{id_estanque}",
            "/api/v1/dashboard-general"
        ]
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)