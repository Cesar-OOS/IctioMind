import os
from mysql.connector import pooling
from mysql.connector import Error
from dotenv import load_dotenv

# 1. Cargar las variables de entorno del archivo .env
load_dotenv()

# 2. Extraer las credenciales
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "root")
DB_NAME = os.getenv("DB_NAME", "ictiomind_db")
DB_PORT = int(os.getenv("DB_PORT", 3306))

# Variable global que sostendrá nuestro grupo de conexiones
connection_pool = None

# 3. Inicializar el Pool al cargar el archivo
try:
    print(f"⏳ Inicializando Pool de Conexiones a MySQL ({DB_HOST})...")
    connection_pool = pooling.MySQLConnectionPool(
        pool_name="ictiomind_pool",
        pool_size=5,  # Mantiene 5 conexiones abiertas listas para usarse
        pool_reset_session=True,
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=DB_PORT
    )
    print("✅ Base de Datos: Pool de conexiones creado exitosamente.")
except Error as e:
    print(f"❌ Base de Datos: Error crítico al crear el pool: {e}")

# 4. La función maestra que usarán los demás archivos
def get_db_connection():
    """
    Entrega una conexión activa desde el pool.
    Los demás archivos importarán esta función para hablar con MySQL.
    """
    try:
        if connection_pool:
            conexion = connection_pool.get_connection()
            if conexion.is_connected():
                return conexion
        print("⚠️ No se pudo obtener una conexión libre del pool.")
        return None
    except Error as e:
        print(f"❌ Error al solicitar conexión al pool: {e}")
        return None