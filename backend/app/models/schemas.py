"""
Schémas Pydantic pour validation des données
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class TranscriptionStatus(str, Enum):
    """Statuts possibles d'une transcription"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class TranscriptionRequest(BaseModel):
    """Requête de transcription"""
    language: Optional[str] = Field(default="fr", description="Code langue (fr, en, etc.)")
    include_timestamps: bool = Field(default=False, description="Inclure les timestamps")


class TranscriptionResponse(BaseModel):
    """Réponse de transcription"""
    id: str = Field(description="ID unique de la transcription")
    text: str = Field(description="Texte transcrit")
    language: str = Field(description="Langue détectée")
    duration_seconds: Optional[float] = Field(description="Durée de l'audio en secondes")
    word_count: int = Field(description="Nombre de mots")
    confidence: Optional[float] = Field(description="Score de confiance (0-1)", default=None)
    processing_time_seconds: float = Field(description="Temps de traitement")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SummaryRequest(BaseModel):
    """Requête de résumé"""
    transcription_text: str = Field(description="Texte à résumer")
    summary_type: str = Field(default="structured", description="Type de résumé: structured, bullet_points, short")
    language: str = Field(default="fr", description="Langue du résumé")


class SummaryResponse(BaseModel):
    """Réponse de résumé structuré"""
    id: str = Field(description="ID unique du résumé")
    summary: str = Field(description="Résumé complet")
    key_points: List[str] = Field(default_factory=list, description="Points clés")
    decisions: List[str] = Field(default_factory=list, description="Décisions prises")
    action_items: List[str] = Field(default_factory=list, description="Actions à mener")
    participants: List[str] = Field(default_factory=list, description="Participants mentionnés")
    processing_time_seconds: float = Field(description="Temps de traitement")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class HealthResponse(BaseModel):
    """Réponse du health check"""
    status: str = Field(description="Status de l'API")
    version: str = Field(description="Version de l'application")
    azure_openai_connected: bool = Field(description="Connexion Azure OpenAI OK")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ErrorResponse(BaseModel):
    """Réponse d'erreur standardisée"""
    error: str = Field(description="Message d'erreur")
    detail: Optional[str] = Field(description="Détails supplémentaires")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
