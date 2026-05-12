import os
import sys
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from dotenv import load_dotenv

# Asegurar la resolución de rutas si se corre directamente para pruebas
ruta_actual = os.path.abspath(__file__)
ruta_backend = os.path.dirname(os.path.dirname(ruta_actual))
if ruta_backend not in sys.path:
    sys.path.append(ruta_backend)

# Cargar las credenciales seguras
load_dotenv()

ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
NUMERO_ORIGEN = os.getenv("TWILIO_PHONE_FROM")
NUMERO_DESTINO = os.getenv("TWILIO_PHONE_TO")

def enviar_alerta_whatsapp(mensaje_alerta: str) -> dict:
    """
    Se conecta a la API de Twilio y envía un mensaje de WhatsApp
    al número registrado en el .env
    """
    if not ACCOUNT_SID or not AUTH_TOKEN:
        return {"status": "error", "mensaje": "Faltan credenciales de Twilio en el .env"}

    try:
        # 1. Inicializamos el cliente de Twilio con nuestras llaves seguras
        cliente = Client(ACCOUNT_SID, AUTH_TOKEN)
        
        # 2. Formateamos y enviamos el mensaje dinámico
        mensaje = cliente.messages.create(
            body=f"🚨 *ALERTA ICTIOMIND* 🚨\n\n{mensaje_alerta}\n\nRevisa el panel de control inmediatamente.",
            from_=NUMERO_ORIGEN,
            to=NUMERO_DESTINO
        )
        
        return {
            "status": "success", 
            "sid": mensaje.sid, 
            "mensaje": "WhatsApp entregado correctamente al dispositivo."
        }
    
    except TwilioRestException as e:
        return {"status": "error", "mensaje": f"Error interno de Twilio: {e}"}
    except Exception as e:
        return {"status": "error", "mensaje": f"Error inesperado de red: {e}"}

# ==========================================
# BLOQUE DE PRUEBA INDEPENDIENTE
# ==========================================
if __name__ == "__main__":
    print(f"📱 Preparando envío de WhatsApp a {NUMERO_DESTINO}...")
    
    # Simulamos una alerta generada por la IA
    alerta_simulada = "El nivel de Oxígeno Disuelto en el 'Estanque 1' ha caído a 4.5 mg/L. Nivel crítico detectado basado en la tendencia de los últimos 30 minutos."
    
    resultado = enviar_alerta_whatsapp(alerta_simulada)
    
    if resultado["status"] == "success":
        print(f"✅ ¡Éxito! El mensaje está en camino. (SID: {resultado['sid']})")
    else:
        print(f"❌ Fallo al enviar: {resultado['mensaje']}")