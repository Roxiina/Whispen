"""
Gestionnaire de fichiers audio
Validation, conversion et nettoyage sécurisés
"""

import os
import uuid
import aiofiles
from pathlib import Path
from typing import Optional, Tuple
from fastapi import UploadFile, HTTPException
from app.config import settings
import logging
import magic  # python-magic-bin for file type detection
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class FileHandler:
    """Gestion sécurisée des fichiers audio"""
    
    def __init__(self):
        self.temp_folder = Path(settings.TEMP_FOLDER)
        self.temp_folder.mkdir(parents=True, exist_ok=True)
    
    async def save_upload_file(self, upload_file: UploadFile) -> Tuple[str, str]:
        """
        Sauvegarde un fichier uploadé de manière sécurisée
        
        Args:
            upload_file: Fichier uploadé par l'utilisateur
        
        Returns:
            Tuple (file_path, file_id)
        
        Raises:
            HTTPException: Si validation échoue
        """
        try:
            # Validation du fichier
            await self._validate_file(upload_file)
            
            # Génération d'un ID unique
            file_id = str(uuid.uuid4())
            
            # Extraction de l'extension
            original_filename = upload_file.filename or "audio.mp3"
            file_extension = Path(original_filename).suffix.lower()
            
            # Chemin de sauvegarde sécurisé
            safe_filename = f"{file_id}{file_extension}"
            file_path = self.temp_folder / safe_filename
            
            # Sauvegarde asynchrone
            async with aiofiles.open(file_path, 'wb') as out_file:
                content = await upload_file.read()
                await out_file.write(content)
            
            logger.info(f"✅ File saved: {safe_filename} ({len(content)} bytes)")
            return str(file_path), file_id
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Failed to save file: {e}")
            raise HTTPException(status_code=500, detail=f"Erreur de sauvegarde: {str(e)}")
    
    async def _validate_file(self, upload_file: UploadFile) -> None:
        """
        Valide un fichier uploadé
        
        Vérifie:
        - Taille maximale
        - Extension autorisée
        - Type MIME
        """
        # Vérification de la taille
        content = await upload_file.read()
        file_size = len(content)
        await upload_file.seek(0)  # Reset pour lecture ultérieure
        
        if file_size > settings.max_file_size_bytes:
            raise HTTPException(
                status_code=413,
                detail=f"Fichier trop volumineux. Maximum: {settings.MAX_FILE_SIZE_MB} MB"
            )
        
        # Vérification de l'extension
        filename = upload_file.filename or ""
        file_extension = Path(filename).suffix.lower().replace(".", "")
        
        if file_extension not in settings.allowed_extensions_list:
            raise HTTPException(
                status_code=400,
                detail=f"Format non supporté. Formats acceptés: {', '.join(settings.allowed_extensions_list)}"
            )
        
        # Vérification du type MIME (sécurité supplémentaire)
        try:
            mime = magic.Magic(mime=True)
            file_type = mime.from_buffer(content[:2048])  # Lire les premiers octets
            
            # Types MIME audio acceptés
            accepted_mimes = [
                "audio/mpeg",      # MP3
                "audio/wav",       # WAV
                "audio/x-wav",     # WAV alternative
                "audio/mp4",       # M4A
                "audio/x-m4a",     # M4A alternative
                "audio/flac",      # FLAC
                "audio/ogg",       # OGG
                "audio/webm",      # WEBM
                "video/webm",      # WEBM peut être détecté comme vidéo
            ]
            
            if not any(accepted_mime in file_type for accepted_mime in accepted_mimes):
                logger.warning(f"⚠️ Suspicious MIME type: {file_type} for {filename}")
                # On permet quand même si l'extension est correcte (flexibilité)
        
        except Exception as e:
            logger.warning(f"⚠️ MIME type check failed: {e}")
            # Continue si la détection MIME échoue
    
    async def delete_file(self, file_path: str) -> bool:
        """
        Supprime un fichier de manière sécurisée
        
        Args:
            file_path: Chemin du fichier à supprimer
        
        Returns:
            True si succès, False sinon
        """
        try:
            path = Path(file_path)
            
            # Vérification de sécurité: le fichier doit être dans temp_folder
            if not path.is_relative_to(self.temp_folder):
                logger.error(f"❌ Attempted to delete file outside temp folder: {file_path}")
                return False
            
            if path.exists():
                path.unlink()
                logger.info(f"🗑️ File deleted: {path.name}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to delete file {file_path}: {e}")
            return False
    
    async def cleanup_old_files(self, hours: Optional[int] = None) -> int:
        """
        Nettoie les fichiers anciens (conformité RGPD)
        
        Args:
            hours: Nombre d'heures après lesquelles supprimer (défaut: settings)
        
        Returns:
            Nombre de fichiers supprimés
        """
        if hours is None:
            hours = settings.AUTO_DELETE_FILES_AFTER_HOURS
        
        deleted_count = 0
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        try:
            for file_path in self.temp_folder.iterdir():
                if file_path.is_file():
                    # Vérification de la date de modification
                    file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    
                    if file_mtime < cutoff_time:
                        await self.delete_file(str(file_path))
                        deleted_count += 1
            
            if deleted_count > 0:
                logger.info(f"🧹 Cleanup: {deleted_count} old files deleted")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"❌ Cleanup failed: {e}")
            return deleted_count
    
    def get_file_info(self, file_path: str) -> dict:
        """Retourne les informations d'un fichier"""
        try:
            path = Path(file_path)
            if not path.exists():
                return {}
            
            stat = path.stat()
            return {
                "filename": path.name,
                "size_bytes": stat.st_size,
                "size_mb": round(stat.st_size / (1024 * 1024), 2),
                "created_at": datetime.fromtimestamp(stat.st_ctime),
                "modified_at": datetime.fromtimestamp(stat.st_mtime)
            }
        except Exception as e:
            logger.error(f"❌ Failed to get file info: {e}")
            return {}


# Instance globale
file_handler = FileHandler()
