"""
Tests unitaires pour file_handler.py
"""
import pytest
from pathlib import Path
from fastapi import UploadFile, HTTPException
from app.utils.file_handler import FileHandler
from io import BytesIO


@pytest.fixture
def file_handler():
    """Fixture pour FileHandler"""
    return FileHandler()


@pytest.mark.asyncio
async def test_save_upload_file_success(file_handler, tmp_path):
    """Test de sauvegarde réussie"""
    # Mock UploadFile
    file_content = b"fake audio content"
    mock_file = UploadFile(filename="test.mp3", file=BytesIO(file_content))
    
    file_handler.temp_folder = tmp_path
    
    file_path, file_id = await file_handler.save_upload_file(mock_file)
    
    assert Path(file_path).exists()
    assert file_id is not None
    assert Path(file_path).suffix == ".mp3"


@pytest.mark.asyncio
async def test_validate_file_too_large(file_handler):
    """Test validation : fichier trop volumineux"""
    # Créer un fichier fictif de 250 MB
    large_content = b"x" * (250 * 1024 * 1024)
    mock_file = UploadFile(filename="large.mp3", file=BytesIO(large_content))
    
    with pytest.raises(HTTPException) as exc_info:
        await file_handler._validate_file(mock_file)
    
    assert exc_info.value.status_code == 413


@pytest.mark.asyncio
async def test_validate_file_wrong_extension(file_handler):
    """Test validation : extension invalide"""
    file_content = b"fake content"
    mock_file = UploadFile(filename="test.exe", file=BytesIO(file_content))
    
    with pytest.raises(HTTPException) as exc_info:
        await file_handler._validate_file(mock_file)
    
    assert exc_info.value.status_code == 400
    assert "Format non supporté" in exc_info.value.detail


@pytest.mark.asyncio
async def test_delete_file(file_handler, tmp_path):
    """Test de suppression de fichier"""
    # Créer un fichier temporaire
    test_file = tmp_path / "test.mp3"
    test_file.write_bytes(b"test content")
    
    file_handler.temp_folder = tmp_path
    
    result = await file_handler.delete_file(str(test_file))
    
    assert result is True
    assert not test_file.exists()


@pytest.mark.asyncio
async def test_cleanup_old_files(file_handler, tmp_path):
    """Test de nettoyage des vieux fichiers"""
    from datetime import datetime, timedelta
    import os
    
    file_handler.temp_folder = tmp_path
    
    # Créer un vieux fichier
    old_file = tmp_path / "old.mp3"
    old_file.write_bytes(b"old content")
    
    # Modifier la date de modification (48h en arrière)
    old_time = (datetime.now() - timedelta(hours=48)).timestamp()
    os.utime(old_file, (old_time, old_time))
    
    deleted_count = await file_handler.cleanup_old_files(hours=24)
    
    assert deleted_count == 1
    assert not old_file.exists()


@pytest.mark.asyncio
async def test_validate_file_allowed_extensions(file_handler):
    """Test validation des extensions autorisées"""
    allowed_extensions = ["mp3", "wav", "m4a", "flac", "ogg", "webm"]
    
    for ext in allowed_extensions:
        file_content = b"audio content"
        mock_file = UploadFile(filename=f"test.{ext}", file=BytesIO(file_content))
        
        # Ne devrait pas lever d'exception
        try:
            await file_handler._validate_file(mock_file)
        except HTTPException as e:
            if e.status_code != 413:  # Ignorer erreur taille si présente
                pytest.fail(f"Extension .{ext} devrait être autorisée")


@pytest.mark.asyncio
async def test_delete_file_outside_temp_folder(file_handler, tmp_path):
    """Test de sécurité : impossible de supprimer en dehors de temp_folder"""
    file_handler.temp_folder = tmp_path
    
    # Tenter de supprimer un fichier en dehors du dossier temp
    external_file = "/etc/passwd"  # Fichier système (ou Windows équivalent)
    
    result = await file_handler.delete_file(external_file)
    
    assert result is False  # Devrait refuser


@pytest.mark.asyncio
async def test_save_multiple_files(file_handler, tmp_path):
    """Test de sauvegarde de plusieurs fichiers"""
    file_handler.temp_folder = tmp_path
    
    file_ids = []
    for i in range(3):
        file_content = f"audio content {i}".encode()
        mock_file = UploadFile(filename=f"test{i}.mp3", file=BytesIO(file_content))
        
        file_path, file_id = await file_handler.save_upload_file(mock_file)
        file_ids.append(file_id)
        
        assert Path(file_path).exists()
    
    # Vérifier que les IDs sont uniques
    assert len(set(file_ids)) == 3


@pytest.mark.asyncio
async def test_cleanup_recent_files_preserved(file_handler, tmp_path):
    """Test : les fichiers récents ne sont pas supprimés"""
    file_handler.temp_folder = tmp_path
    
    # Créer un fichier récent
    recent_file = tmp_path / "recent.mp3"
    recent_file.write_bytes(b"recent content")
    
    deleted_count = await file_handler.cleanup_old_files(hours=24)
    
    assert deleted_count == 0
    assert recent_file.exists()  # Le fichier récent doit être préservé
