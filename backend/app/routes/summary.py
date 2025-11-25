"""
Routes de génération de résumés
Endpoints pour créer des résumés structurés de transcriptions
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from app.models.schemas import SummaryRequest, SummaryResponse, ErrorResponse
from app.services.azure_service import azure_service
import uuid
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/summary", tags=["Summary"])


@router.post(
    "/generate",
    response_model=SummaryResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    summary="Génère un résumé structuré d'une transcription",
    description="""
    Génère un résumé intelligent d'une transcription via Azure OpenAI GPT-4.
    
    **Types de résumé disponibles:**
    - `structured`: Résumé complet avec sections (points clés, décisions, actions)
    - `bullet_points`: Liste de points clés (5-10 items)
    - `short`: Résumé ultra-court (2-3 phrases)
    
    **Langues supportées:** FR, EN
    """
)
async def generate_summary(request: SummaryRequest) -> SummaryResponse:
    """
    Génère un résumé structuré
    
    Args:
        request: SummaryRequest avec le texte et les options
    
    Returns:
        SummaryResponse avec résumé structuré et éléments extraits
    """
    try:
        logger.info(f"📝 Generating summary (type: {request.summary_type}, lang: {request.language})")
        
        # Validation du texte
        if len(request.transcription_text.strip()) < 50:
            raise HTTPException(
                status_code=400,
                detail="Le texte est trop court pour générer un résumé (minimum 50 caractères)"
            )
        
        # Génération du résumé via GPT-4
        result = await azure_service.generate_summary(
            transcription_text=request.transcription_text,
            summary_type=request.summary_type,
            language=request.language
        )
        
        # Construction de la réponse
        response = SummaryResponse(
            id=str(uuid.uuid4()),
            summary=result["summary"],
            key_points=result.get("key_points", []),
            decisions=result.get("decisions", []),
            action_items=result.get("action_items", []),
            participants=result.get("participants", []),
            processing_time_seconds=result["processing_time"],
            created_at=datetime.utcnow()
        )
        
        logger.info(f"✅ Summary generated successfully")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Summary generation failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la génération du résumé: {str(e)}"
        )


@router.post(
    "/quick",
    summary="Génère un résumé rapide en 2-3 phrases",
    description="Version simplifiée pour obtenir un résumé court rapidement"
)
async def quick_summary(transcription_text: str, language: str = "fr"):
    """Résumé rapide (shortcut endpoint)"""
    try:
        request = SummaryRequest(
            transcription_text=transcription_text,
            summary_type="short",
            language=language
        )
        return await generate_summary(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/health",
    summary="Vérifie la disponibilité du service de résumé",
    description="Teste la connexion à Azure OpenAI GPT-4"
)
async def summary_health():
    """Health check du service de résumé"""
    try:
        is_connected = await azure_service.check_connection()
        
        return JSONResponse(
            status_code=200 if is_connected else 503,
            content={
                "service": "summary",
                "status": "operational" if is_connected else "unavailable",
                "azure_gpt4": is_connected,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "service": "summary",
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )
