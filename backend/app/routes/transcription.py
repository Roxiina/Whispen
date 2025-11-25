"""
Routes de transcription audio
Endpoints pour upload et transcription de fichiers audio
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from app.models.schemas import TranscriptionResponse, ErrorResponse
from app.services.azure_service import azure_service
from app.utils.file_handler import file_handler
import uuid
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/transcription", tags=["Transcription"])


@router.post(
    "/upload",
    response_model=TranscriptionResponse,
    responses={
        400: {"model": ErrorResponse},
        413: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    summary="Transcrit un fichier audio uploadé",
    description="""
    Upload un fichier audio et le transcrit automatiquement via Azure OpenAI Whisper.
    
    **Formats supportés:** MP3, WAV, M4A, FLAC, OGG, WEBM
    
    **Taille maximale:** 200 MB
    
    **Langues supportées:** FR, EN, ES, DE, IT, PT, etc.
    """
)
async def transcribe_upload(
    file: UploadFile = File(..., description="Fichier audio à transcrire"),
    language: str = Form(default="fr", description="Code langue (fr, en, es, etc.)")
) -> TranscriptionResponse:
    """
    Transcrit un fichier audio uploadé
    
    Args:
        file: Fichier audio
        language: Code langue ISO 639-1
    
    Returns:
        TranscriptionResponse avec le texte transcrit et métadonnées
    """
    file_path = None
    
    try:
        logger.info(f"📤 Received transcription request: {file.filename} (lang: {language})")
        
        # 1. Sauvegarde sécurisée du fichier
        file_path, file_id = await file_handler.save_upload_file(file)
        
        # 2. Transcription via Azure OpenAI Whisper
        result = await azure_service.transcribe_audio(file_path, language)
        
        # 3. Construction de la réponse
        response = TranscriptionResponse(
            id=file_id,
            text=result["text"],
            language=result["language"],
            duration_seconds=result.get("duration"),
            word_count=result["word_count"],
            processing_time_seconds=result["processing_time"],
            created_at=datetime.utcnow()
        )
        
        logger.info(f"✅ Transcription completed: {file_id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Transcription failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la transcription: {str(e)}"
        )
    finally:
        # 4. Nettoyage du fichier temporaire (RGPD compliance)
        if file_path:
            await file_handler.delete_file(file_path)


@router.get(
    "/health",
    summary="Vérifie la disponibilité du service de transcription",
    description="Teste la connexion à Azure OpenAI Whisper"
)
async def transcription_health():
    """Health check du service de transcription"""
    try:
        is_connected = await azure_service.check_connection()
        
        return JSONResponse(
            status_code=200 if is_connected else 503,
            content={
                "service": "transcription",
                "status": "operational" if is_connected else "unavailable",
                "azure_whisper": is_connected,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "service": "transcription",
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )
