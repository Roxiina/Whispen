"""
Configuration centrale de l'application Whispen
Gère les variables d'environnement et les paramètres globaux
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Configuration de l'application chargée depuis .env"""
    
    # Azure OpenAI Configuration
    AZURE_OPENAI_ENDPOINT: str
    AZURE_OPENAI_API_KEY: str
    AZURE_OPENAI_API_VERSION: str = "2024-02-15-preview"
    AZURE_WHISPER_DEPLOYMENT_NAME: str = "whisper"
    AZURE_GPT4_DEPLOYMENT_NAME: str = "gpt-4"
    
    # Application Settings
    TEMP_FOLDER: str = "./temp"
    MAX_FILE_SIZE_MB: int = 200
    ALLOWED_AUDIO_EXTENSIONS: str = "mp3,wav,m4a,flac,ogg,webm"
    
    # Security
    SECRET_KEY: str
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    
    # RGPD Compliance
    AUTO_DELETE_FILES_AFTER_HOURS: int = 24
    ENABLE_FILE_ENCRYPTION: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    @property
    def allowed_extensions_list(self) -> List[str]:
        """Retourne la liste des extensions autorisées"""
        return [ext.strip() for ext in self.ALLOWED_AUDIO_EXTENSIONS.split(",")]
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Retourne la liste des origines CORS autorisées"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    @property
    def max_file_size_bytes(self) -> int:
        """Retourne la taille max en octets"""
        return self.MAX_FILE_SIZE_MB * 1024 * 1024


# Instance globale de configuration
settings = Settings()

# Créer le dossier temporaire s'il n'existe pas
os.makedirs(settings.TEMP_FOLDER, exist_ok=True)
