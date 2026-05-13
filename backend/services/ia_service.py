import os
import sys
import joblib
import numpy as np
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

# Configuración de rutas
ruta_actual = os.path.abspath(__file__)
ruta_backend = os.path.dirname(os.path.dirname(ruta_actual))
if ruta_backend not in sys.path:
    sys.path.append(ruta_backend)

from config.database import get_db_connection

# IMPORTANTE: Asegúrate de que el nombre coincida con tu nuevo archivo exportado
RUTA_MODELO = os.path.join(ruta_backend, "models_ML", "modelo_ictiomind_v3.joblib")

# 1. CARGA DEL MODELO EN MEMORIA
modelo_ia = None
try:
    print("🧠 Cargando Cerebro Predictivo Multi-Output (RandomForestRegressor)...")
    modelo_ia = joblib.load(RUTA_MODELO)
    print("✅ Modelo Predictivo Integral cargado exitosamente.")
except Exception as e:
    print(f"⚠️ Advertencia: Falló la carga del modelo. Detalles: {e}")


def evaluar_estanque_con_ia(id_estanque: int) -> dict:
    if modelo_ia is None:
        return {"error": "Modelo no disponible"}

    conexion = get_db_connection()
    if not conexion:
        return {"error": "Sin conexión a Base de Datos"}

    try:
        with conexion.cursor(dictionary=True) as cursor:
            # A. Obtener Especies y sus LÍMITES BIOLÓGICOS (Dinámico)
            # Usamos MAX() y MIN() para proteger al pez más delicado si hay varias especies
            query_especies = """
                SELECT 
                    GROUP_CONCAT(c.nombre_comun SEPARATOR ', ') as peces,
                    MAX(c.oxigeno_min) as oxigeno_critico,
                    MAX(c.temp_min) as temp_minima,
                    MIN(c.temp_max) as temp_maxima,
                    MAX(c.ph_min) as ph_minimo,
                    MIN(c.ph_max) as ph_maximo
                FROM habitantes_estanques h
                JOIN catalogo_especies c ON h.id_especie = c.id_especie
                WHERE h.id_estanque = %s
            """
            cursor.execute(query_especies, (id_estanque,))
            biologia = cursor.fetchone()
            
            especies_texto = biologia['peces'] if biologia and biologia['peces'] else "Desconocida"
            
            # Valores por defecto en caso de que un estanque no tenga peces registrados aún
            limite_o2 = float(biologia['oxigeno_critico']) if biologia and biologia['oxigeno_critico'] else 4.0
            limite_temp_min = float(biologia['temp_minima']) if biologia and biologia['temp_minima'] else 20.0
            limite_temp_max = float(biologia['temp_maxima']) if biologia and biologia['temp_maxima'] else 32.0
            limite_ph_min = float(biologia['ph_minimo']) if biologia and biologia['ph_minimo'] else 6.5
            limite_ph_max = float(biologia['ph_maximo']) if biologia and biologia['ph_maximo'] else 8.5

            # B. Obtener las últimas 8 lecturas
            query_lecturas = """
                SELECT fecha_hora, oxigeno_disuelto, temperatura, ph, dureza 
                FROM lecturas_telemetria 
                WHERE id_estanque = %s 
                ORDER BY fecha_hora DESC 
                LIMIT 8
            """
            cursor.execute(query_lecturas, (id_estanque,))
            lecturas = cursor.fetchall()

        if len(lecturas) < 5:
            return {"status": "info", "mensaje": f"Se necesitan 5 lecturas. Hay {len(lecturas)}."}

        # C. Construir Lags
        o2_lags = [float(l['oxigeno_disuelto']) for l in lecturas[:5]]
        temp_lags = [float(l['temperatura']) for l in lecturas[:5]]
        ph_lags = [float(l['ph']) for l in lecturas[:5]]
        dur_lags = [float(l['dureza']) for l in lecturas[:5]]

        fila_datos = o2_lags + temp_lags + ph_lags + dur_lags
        features = np.array([fila_datos])
        predicciones = modelo_ia.predict(features)[0]
        
        o2_predicho = round(float(predicciones[0]), 2)
        temp_predicha = round(float(predicciones[1]), 2)
        ph_predicho = round(float(predicciones[2]), 2)
        dureza_predicha = round(float(predicciones[3]), 2)

        # D. Construir el Historial para la Gráfica
        historial_grafica = []
        for lec in reversed(lecturas):
            hora_formateada = lec['fecha_hora'].strftime("%H:%M")
            historial_grafica.append({
                "hora": hora_formateada,
                "temp": float(lec['temperatura']),
                "oxigeno": float(lec['oxigeno_disuelto']),
                "ph": float(lec['ph'])
            })
        
        historial_grafica.append({
            "hora": "Predicción (+1h)",
            "temp": temp_predicha,
            "oxigeno": o2_predicho,
            "ph": ph_predicho
        })

        # ==========================================================
        # E. LÓGICA DE ALERTAS DINÁMICA (Basada en la BD)
        # ==========================================================
        estado = "Óptimo"
        accion = "Parámetros estables. Continuar rutina normal."
        color_sugerido = "verde"
        salud_porcentaje = 95
        alerta_twilio = False

        # Comparamos la predicción de la IA contra el límite biológico estricto del pez
        if o2_predicho <= limite_o2:
            estado = f"Alerta Roja: Riesgo letal para {especies_texto}"
            accion = f"El O2 ({o2_predicho}) está por debajo del mínimo vital ({limite_o2}). ¡Encender aireadores!"
            color_sugerido = "rojo"
            salud_porcentaje = 15
            alerta_twilio = True
            
        elif ph_predicho <= limite_ph_min or ph_predicho >= limite_ph_max:
            estado = "Alerta Roja: Choque de pH"
            accion = f"El pH se desviará a {ph_predicho}. Fuera del rango de {especies_texto}."
            color_sugerido = "rojo"
            salud_porcentaje = 25
            alerta_twilio = True
            
        elif temp_predicha <= limite_temp_min or temp_predicha >= limite_temp_max:
            estado = "Alerta Roja: Estrés Térmico"
            accion = f"La temperatura llegará a {temp_predicha}°C. Fuera del rango vital."
            color_sugerido = "rojo"
            salud_porcentaje = 30
            alerta_twilio = True
            
        # Si no es letal, pero está a menos de 1 mg/L del límite, es advertencia amarilla
        elif o2_predicho <= (limite_o2 + 1.0):
            estado = "Alerta Amarilla: O2 acercándose al límite"
            accion = "Monitorear de cerca. Preparar equipo de oxigenación de respaldo."
            color_sugerido = "amarillo"
            salud_porcentaje = 60

        return {
            "estanque_id": id_estanque,
            "especies": especies_texto,
            "historial_grafica": historial_grafica,
            "predicciones": {
                "oxigeno": o2_predicho,
                "temperatura": temp_predicha,
                "ph": ph_predicho,
                "dureza": dureza_predicha
            },
            "estado": estado,
            "recomendacion_ia": accion,
            "salud_porcentaje": salud_porcentaje,
            "color_grafica": color_sugerido,
            "disparar_whatsapp": alerta_twilio
        }

    except Exception as e:
        return {"error": f"Fallo al procesar la predicción: {e}"}
    finally:
        if conexion.is_connected():
            conexion.close()

# ==========================================
# PRUEBA INDEPENDIENTE
# ==========================================
if __name__ == "__main__":
    print("Iniciando evaluación de prueba integral para el Estanque 1...")
    resultado = evaluar_estanque_con_ia(1)
    import json
    print(json.dumps(resultado, indent=4, ensure_ascii=False))