from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ==========================================
# 1. INICIALIZACIÓN DE LA APLICACIÓN
# ==========================================
app = FastAPI(
    title="IctioMind API",
    description="Cerebro Predictivo Acuicola",
    version="1.0.0"
)

# ==========================================
# 2. CONFIGURACIÓN DE SEGURIDAD (CORS)
# ==========================================
# Esto permite que tu Frontend en React (que usualmente corre en localhost:5173) 
# pueda pedirle datos a este Backend (que correrá en localhost:8000) sin ser bloqueado.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # En producción, aquí pondremos la URL exacta de tu frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# 3. RUTAS BASE (ENDPOINTS)
# ==========================================
@app.get("/")
def health_check():
    """
    Ruta de comprobación. Sirve para verificar que el servidor está vivo.
    """
    return {
        "status": "online", 
        "sistema": "IctioMind Backend",
        "mensaje": "El Cerebro Predictivo está escuchando..."
    }

# 1. Importamos el nuevo router
from routers.dashboard import router as dashboard_router

# 2. Le decimos a FastAPI que use esas rutas
app.include_router(dashboard_router)