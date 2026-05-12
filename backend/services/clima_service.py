import os
import sys
import requests
from datetime import datetime
from dotenv import load_dotenv

# Asegurar la resolución de rutas si se corre directamente
ruta_actual = os.path.abspath(__file__)
ruta_backend = os.path.dirname(os.path.dirname(ruta_actual))
if ruta_backend not in sys.path:
    sys.path.append(ruta_backend)

# Cargar variables de entorno
load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")
UBICACION = os.getenv("UBICACION_CLIMA", "Zacatepec,MX")

def obtener_pronostico_evaluado() -> dict:
    """
    Se conecta a OpenWeather (Pronóstico de 5 días / 3 horas),
    agrupa los datos por día y evalúa amenazas biológicas para los peces.
    """
    if not API_KEY:
        return {"status": "error", "mensaje": "Falta OPENWEATHER_API_KEY en el .env"}

    url = "https://api.openweathermap.org/data/2.5/forecast"
    parametros = {
        "q": UBICACION,
        "appid": API_KEY,
        "units": "metric", # Grados Celsius
        "lang": "es"       # Descripciones en español
    }

    try:
        respuesta = requests.get(url, params=parametros)
        if respuesta.status_code != 200:
            return {"status": "error", "mensaje": f"Error de OpenWeather: {respuesta.json()}"}

        datos = respuesta.json()
        pronosticos_lista = datos.get("list", [])
        
        # 1. Agrupar los datos por día (vienen cada 3 horas)
        dias_agrupados = {}
        hoy = datetime.now().date()

        for item in pronosticos_lista:
            fecha_texto = item["dt_txt"] # Ej. "2026-05-12 15:00:00"
            fecha_obj = datetime.strptime(fecha_texto, "%Y-%m-%d %H:%M:%S").date()
            
            dias_distancia = (fecha_obj - hoy).days
            if dias_distancia < 0:
                continue # Ignorar datos pasados

            if dias_distancia not in dias_agrupados:
                dias_agrupados[dias_distancia] = {
                    "fecha": str(fecha_obj),
                    "temp_min": 100.0,
                    "temp_max": -100.0,
                    "descripciones": set(),
                    "lluvia_detectada": False
                }

            # Actualizar mínimos y máximos del día
            temp = float(item["main"]["temp"])
            if temp < dias_agrupados[dias_distancia]["temp_min"]:
                dias_agrupados[dias_distancia]["temp_min"] = temp
            if temp > dias_agrupados[dias_distancia]["temp_max"]:
                dias_agrupados[dias_distancia]["temp_max"] = temp

            # Guardar descripciones y detectar lluvia
            clima_desc = item["weather"][0]["description"].lower()
            dias_agrupados[dias_distancia]["descripciones"].add(clima_desc)
            if "lluvia" in clima_desc or "tormenta" in clima_desc:
                dias_agrupados[dias_distancia]["lluvia_detectada"] = True

        # 2. Evaluar el riesgo con base en las reglas de IctioMind
        dias_analizados = []
        alerta_global = False

        for dias_faltantes, info in sorted(dias_agrupados.items()):
            nivel_alerta = "Ninguna"
            motivo = []

            # Reglas de negocio biológicas (Ajustables)
            if info["temp_min"] < 20.0:
                motivo.append("Baja temperatura crítica")
            if info["temp_max"] > 35.0:
                motivo.append("Temperaturas Elevadas")
            if info["lluvia_detectada"]:
                motivo.append("Probabilidad de lluvia/tormenta")

            # Asignación de Prioridad (Según requerimientos: Bajo > 3 días, Medio 2-3 días, Alto < 1 día)
            if motivo:
                alerta_global = True
                if dias_faltantes <= 1:
                    nivel_alerta = "ALTA"
                elif 2 <= dias_faltantes <= 3:
                    nivel_alerta = "MEDIA"
                else:
                    nivel_alerta = "BAJA"

            dias_analizados.append({
                "dias_faltantes": dias_faltantes,
                "fecha": info["fecha"],
                "temp_min": round(info["temp_min"], 1),
                "temp_max": round(info["temp_max"], 1),
                "condiciones": list(info["descripciones"]),
                "alerta_nivel": nivel_alerta,
                "motivos_riesgo": motivo if motivo else ["Día estable"]
            })

        return {
            "status": "success",
            "ubicacion": UBICACION,
            "alerta_activa": alerta_global,
            "pronostico_5_dias": dias_analizados
        }

    except Exception as e:
        return {"status": "error", "mensaje": str(e)}

# ==========================================
# BLOQUE DE PRUEBA INDEPENDIENTE
# ==========================================
if __name__ == "__main__":
    import json
    print(f"🌍 Consultando el clima para: {UBICACION}...")
    resultado = obtener_pronostico_evaluado()
    print("\n--- REPORTE CLIMÁTICO ICTIOMIND ---")
    print(json.dumps(resultado, indent=4, ensure_ascii=False))