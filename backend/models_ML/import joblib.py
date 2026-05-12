import joblib
import os

# 1. Pon aquí la ruta exacta donde guardaste el archivo que te pasó tu compañero
RUTA_MODELO = r"C:\Users\k0nn0\OneDrive\Escritorio\Misc\Tec\8vo\IA\IctioMind\backend\models_ML\inova_predictive_rf.joblib"

def inspeccionar_modelo():
    print("🔍 Iniciando autopsia del modelo .joblib...\n")
    
    if not os.path.exists(RUTA_MODELO):
        print("❌ Error: No se encontró el archivo en la ruta especificada.")
        return

    try:
        # Cargar el modelo en memoria
        modelo = joblib.load(RUTA_MODELO)
        
        print("✅ Modelo cargado correctamente.")
        print(f"🧠 Algoritmo utilizado: {type(modelo).__name__}\n")

        # A. Intentar extraer los nombres de las columnas (Funciona si se entrenó con Pandas)
        if hasattr(modelo, 'feature_names_in_'):
            print("📊 NOMBRES DE LAS COLUMNAS ESPERADAS (En este orden exacto):")
            for i, columna in enumerate(modelo.feature_names_in_):
                print(f"   {i + 1}. {columna}")
        else:
            print("⚠️ El modelo NO guardó los nombres de las columnas (Fue entrenado con Numpy puro).")

        # B. Extraer la CANTIDAD de columnas esperadas (Esto casi siempre funciona)
        if hasattr(modelo, 'n_features_in_'):
            print(f"\n🔢 CANTIDAD DE VARIABLES ESPERADAS: {modelo.n_features_in_} columnas.")

        # C. Extraer las salidas posibles (Si es un modelo de Clasificación)
        if hasattr(modelo, 'classes_'):
            print(f"🏷️ SALIDAS POSIBLES (Las etiquetas que el modelo puede predecir): {modelo.classes_}")
            
        # D. Caso especial: Si es un Pipeline (Varias herramientas encadenadas)
        if type(modelo).__name__ == 'Pipeline':
            print("\n⚙️ PASOS DEL PIPELINE:")
            for nombre_paso, herramienta in modelo.steps:
                print(f"   - {nombre_paso}: {type(herramienta).__name__}")

    except Exception as e:
        print(f"❌ Error al leer el modelo: {e}")

if __name__ == "__main__":
    inspeccionar_modelo()