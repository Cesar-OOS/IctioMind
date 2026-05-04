import pandas as pd

class IngestaIctioMind:
    def __init__(self):
        # Ahora la IA ignora el JSON y solo espera los nombres exactos de tu tabla MySQL/MariaDB
        self.columnas_esperadas = [
            'fecha_hora', 
            'id_estanque', 
            'temperatura', 
            'oxigeno_disuelto', 
            'ph', 
            'dureza'
        ]

    def procesar_datos_bd(self, registros_bd):
        """
        Recibe los últimos N registros de la base de datos (por ejemplo, pasados por el backend 
        como una lista de diccionarios) y los prepara para el modelo predictivo.
        """
        try:
            # 1. Convertir la consulta de la BD a un DataFrame (Tabla matemática)
            df = pd.DataFrame(registros_bd)

            # 2. Validar que la consulta traiga las columnas correctas de lecturas_telemetria
            for col in self.columnas_esperadas:
                if col not in df.columns:
                    raise ValueError(f"Falta la columna crítica de la BD: {col}")

            # 3. Formateo de Fechas (Vital para series de tiempo)
            df['fecha_hora'] = pd.to_datetime(df['fecha_hora'])
            
            # 4. Ordenamos cronológicamente: Del dato más viejo al más reciente por estanque
            df = df.sort_values(by=['id_estanque', 'fecha_hora'])

            return self._limpiar_y_suavizar_datos(df)

        except Exception as e:
            print(f"Error en la ingesta desde BD: {e}")
            return None

    def _limpiar_y_suavizar_datos(self, df):
        """
        Aplica limpieza de ruido y maneja posibles lecturas nulas del sensor en la BD.
        """
        # Interpolación por si el backend guardó algún NULL en la BD
        columnas_medicion = ['temperatura', 'oxigeno_disuelto', 'ph', 'dureza']
        for col in columnas_medicion:
            df[col] = df[col].interpolate(method='linear')

        # SUAVIZADO DE RUIDO (Rolling Average de 3 periodos)
        for col in columnas_medicion:
            df[f'{col}_suavizado'] = df.groupby('id_estanque')[col].transform(
                lambda x: x.rolling(window=3, min_periods=1).mean()
            )

        # Retornamos solo las columnas listas para que el Módulo 2 haga la regresión
        columnas_finales = ['fecha_hora', 'id_estanque', 'temperatura_suavizado', 
                            'oxigeno_disuelto_suavizado', 'ph_suavizado', 'dureza_suavizado']
        
        return df[columnas_finales]

# ==========================================
# PRUEBA DEL MÓDULO CON FLUJO DE BASE DE DATOS
# ==========================================
if __name__ == "__main__":
    # Simulamos lo que el Backend leería de la tabla lecturas_telemetria mediante un SELECT
    datos_desde_bd = [
        {"id_lectura": 1, "fecha_hora": "2026-05-03 08:00:00", "id_sensor": 101, "id_estanque": 1, "temperatura": 25.3, "oxigeno_disuelto": 7.27, "ph": 7.21, "dureza": 127.39},
        {"id_lectura": 2, "fecha_hora": "2026-05-03 08:05:00", "id_sensor": 101, "id_estanque": 1, "temperatura": 25.4, "oxigeno_disuelto": 7.15, "ph": 7.20, "dureza": 127.40},
        {"id_lectura": 3, "fecha_hora": "2026-05-03 08:10:00", "id_sensor": 101, "id_estanque": 1, "temperatura": 25.5, "oxigeno_disuelto": 6.90, "ph": 7.18, "dureza": 127.40}
    ]

    motor_ingesta = IngestaIctioMind()
    df_procesado = motor_ingesta.procesar_datos_bd(datos_desde_bd)
    
    print("Datos históricos extraídos de la BD, limpiados y listos para ML:")
    print(df_procesado)