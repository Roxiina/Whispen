"""
Point d'entrée principal de l'application Whispen
FastAPI application avec configuration CORS, middleware et routes
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.routes import transcription, summary
from app.models.schemas import HealthResponse
from app.services.azure_service import azure_service
from app.utils.file_handler import file_handler
import logging
from datetime import datetime
import uvicorn

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Création de l'application FastAPI
app = FastAPI(
    title="Whispen API",
    description="""
    🎙️ **Whispen** - API de transcription et résumé de réunions
    
    Application propulsée par Azure OpenAI (Whisper + GPT-4).
    
    ## Fonctionnalités
    
    - 🎤 **Transcription audio** : Upload de fichiers audio (MP3, WAV, M4A, etc.)
    - 📝 **Résumé intelligent** : Génération de résumés structurés avec GPT-4
    - 🔒 **Sécurité** : Validation des fichiers, suppression automatique (RGPD)
    - ⚡ **Performance** : Traitement rapide et précis (>95% précision)
    
    ## Support
    
    - Langues : Français, Anglais, Espagnol, Allemand, etc.
    - Formats : MP3, WAV, M4A, FLAC, OGG, WEBM
    - Taille max : 200 MB par fichier
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    contact={
        "name": "Whispen Support",
        "email": "support@whispen.dev"
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    }
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware de logging des requêtes
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log toutes les requêtes entrantes"""
    start_time = datetime.utcnow()
    
    # Traitement de la requête
    response = await call_next(request)
    
    # Calcul du temps de traitement
    process_time = (datetime.utcnow() - start_time).total_seconds()
    
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.3f}s"
    )
    
    return response

# Inclusion des routes
app.include_router(transcription.router, prefix="/api/v1")
app.include_router(summary.router, prefix="/api/v1")

# Routes principales
@app.get(
    "/",
    summary="Page d'accueil de l'API",
    description="Retourne les informations de base de l'API"
)
async def root():
    """Page d'accueil"""
    return {
        "name": "Whispen API",
        "version": "1.0.0",
        "description": "API de transcription et résumé de réunions avec Azure OpenAI",
        "documentation": "/docs",
        "health": "/health",
        "endpoints": {
            "transcription": "/api/v1/transcription/upload",
            "summary": "/api/v1/summary/generate"
        }
    }

@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check global",
    description="Vérifie l'état de santé de l'API et des services externes"
)
async def health_check():
    """
    Health check complet de l'application
    
    Vérifie:
    - Disponibilité de l'API
    - Connexion à Azure OpenAI
    - État du système de fichiers
    """
    try:
        # Vérification de la connexion Azure OpenAI
        azure_connected = await azure_service.check_connection()
        
        return HealthResponse(
            status="healthy" if azure_connected else "degraded",
            version="1.0.0",
            azure_openai_connected=azure_connected,
            timestamp=datetime.utcnow()
        )
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "version": "1.0.0",
                "azure_openai_connected": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )

# Événements de démarrage et arrêt
@app.on_event("startup")
async def startup_event():
    """Actions au démarrage de l'application"""
    logger.info("🚀 Starting Whispen API...")
    logger.info(f"📁 Temp folder: {settings.TEMP_FOLDER}")
    logger.info(f"🌐 CORS origins: {settings.cors_origins_list}")
    logger.info(f"🤖 Azure OpenAI endpoint: {settings.AZURE_OPENAI_ENDPOINT}")
    
    # Nettoyage initial des vieux fichiers
    deleted = await file_handler.cleanup_old_files()
    if deleted > 0:
        logger.info(f"🧹 Cleaned up {deleted} old files on startup")
    
    # Test de connexion Azure
    try:
        is_connected = await azure_service.check_connection()
        if is_connected:
            logger.info("✅ Azure OpenAI connection: OK")
        else:
            logger.warning("⚠️ Azure OpenAI connection: FAILED")
    except Exception as e:
        logger.error(f"❌ Azure OpenAI connection error: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Actions à l'arrêt de l'application"""
    logger.info("🛑 Shutting down Whispen API...")
    
    # Nettoyage final (optionnel - peut être commenté en prod)
    # await file_handler.cleanup_old_files(hours=0)

# Gestion des erreurs globales
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Handler pour les routes non trouvées"""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Route non trouvée",
            "detail": f"L'endpoint {request.url.path} n'existe pas",
            "documentation": "/docs"
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """Handler pour les erreurs serveur"""
    logger.error(f"❌ Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Erreur interne du serveur",
            "detail": "Une erreur inattendue s'est produite",
            "timestamp": datetime.utcnow().isoformat()
        }
    )

# Point d'entrée pour exécution directe
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Hot reload en développement
        log_level="info"
    )
