import os
import sys
import joblib
import numpy as np

# Configuración de rutas
ruta_actual = os.path.abspath(__file__)
ruta_backend = os.path.dirname(os.path.dirname(ruta_actual))
if ruta_backend not in sys.path:
    sys.path.append(ruta_backend)

# Ruta absoluta al archivo .joblib
RUTA_MODELO = os.path.join(ruta_backend, "models_ml", "modelo_ictiomind.joblib")

# 1. CARGA DEL MODELO EN MEMORIA
modelo_ia = None
try:
    print("🧠 Cargando Cerebro Predictivo de IctioMind...")
    modelo_ia = joblib.load(RUTA_MODELO)
    print("✅ Modelo IA cargado exitosamente.")
except Exception as e:
    print(f"⚠️ Advertencia: No se encontró el modelo o falló la carga. Detalles: {e}")

# 2. DICCIONARIO DE RECOMENDACIONES (Lógica de Negocio)
# Asumimos que tu modelo arroja un código de predicción (0, 1, 2, 3...)
# Aquí traducimos ese número a acciones reales para el Frontend
DICCIONARIO_RECOMENDACIONES = {
    0: {
        "estado": "Óptimo",
        "salud_porcentaje": 95,
        "accion": "Parámetros estables. Continuar monitoreo normal."
    },
    1: {
        "estado": "Peligro: Hipoxia (Falta de Oxígeno)",
        "salud_porcentaje": 40,
        "accion": "Encender aireadores por 15 minutos, y 5 minutos después de apagarlo consultar nuevamente el panel de control."
    },
    2: {
        "estado": "Peligro: Hipotermia",
        "salud_porcentaje": 30,
        "accion": "Activar calentadores de inmersión. Revisar aislamiento térmico del estanque."
    },
    3: {
        "estado": "Peligro: Pico de Amoníaco / pH Crítico",
        "salud_porcentaje": 20,
        "accion": "Realizar recambio de agua del 20% de forma inmediata. Suspender alimentación."
    }
}

# 3. FUNCIÓN DE PREDICCIÓN
def analizar_estado_con_ia(datos_telemetria: list) -> dict:
    """
    Recibe los deltas y datos actuales, se los pasa al modelo .joblib
    y devuelve la recomendación traducida.
    """
    if modelo_ia is None:
        return {"error": "El modelo de IA no está disponible en el servidor."}

    try:
        # A. Preparar los datos para Scikit-Learn
        # El modelo espera un array 2D de NumPy con las variables EXACTAS con las que fue entrenado.
        # Ejemplo: [Temp_Actual, Delta_Temp_10m, Oxigeno_Actual, Delta_Oxigeno_10m, pH, Dureza]
        features = np.array([datos_telemetria])

        # B. Ejecutar la predicción
        prediccion_cruda = modelo_ia.predict(features)[0] # Obtiene el número (ej. 1)

        # C. Buscar la recomendación correspondiente
        resultado_traducido = DICCIONARIO_RECOMENDACIONES.get(
            int(prediccion_cruda), 
            {"estado": "Desconocido", "salud_porcentaje": 50, "accion": "Revisar estanque manualmente."}
        )

        return resultado_traducido

    except Exception as e:
        return {"error": f"Fallo al procesar la predicción: {e}"}

# ==========================================
# BLOQUE DE PRUEBA INDEPENDIENTE
# ==========================================
if __name__ == "__main__":
    # IMPORTANTE: Estos números DEBEN coincidir con la cantidad de columnas que tu equipo usó para entrenar la IA.
    # Supongamos que entrenaron con 6 variables: Temp, Delta_Temp, Oxigeno, Delta_O2, pH, Dureza
    datos_simulados_para_ia = [24.5, -1.2, 4.2, -0.8, 7.1, 120] 
    
    print("\nSimulando envío de datos a la IA:", datos_simulados_para_ia)
    respuesta = analizar_estado_con_ia(datos_simulados_para_ia)
    print("\n--- DIAGNÓSTICO DE LA IA ---")
    print(respuesta)