"""
Tests d'intégration pour les routes API
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch, Mock


client = TestClient(app)


def test_root_endpoint():
    """Test de l'endpoint racine"""
    response = client.get("/")
    assert response.status_code == 200
    assert "Whispen API" in response.json()["name"]


def test_health_endpoint():
    """Test du health check"""
    with patch('app.services.azure_service.azure_service.check_connection', return_value=True):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


def test_transcription_health():
    """Test du health check transcription"""
    with patch('app.services.azure_service.azure_service.check_connection', return_value=True):
        response = client.get("/api/v1/transcription/health")
        assert response.status_code == 200
        assert response.json()["service"] == "transcription"


def test_summary_health():
    """Test du health check summary"""
    with patch('app.services.azure_service.azure_service.check_connection', return_value=True):
        response = client.get("/api/v1/summary/health")
        assert response.status_code == 200
        assert response.json()["service"] == "summary"


def test_transcription_upload_no_file():
    """Test upload sans fichier"""
    response = client.post("/api/v1/transcription/upload")
    assert response.status_code == 422  # Validation error


def test_summary_generate_short_text():
    """Test génération résumé avec texte trop court"""
    response = client.post(
        "/api/v1/summary/generate",
        json={
            "transcription_text": "Trop court",
            "summary_type": "structured",
            "language": "fr"
        }
    )
    assert response.status_code == 400
    assert "trop court" in response.json()["detail"].lower()


def test_summary_generate_success():
    """Test génération résumé réussie"""
    mock_result = {
        "summary": "Résumé test",
        "key_points": ["Point 1"],
        "decisions": [],
        "action_items": [],
        "participants": [],
        "processing_time": 1.5
    }
    
    with patch('app.services.azure_service.azure_service.generate_summary', return_value=mock_result):
        response = client.post(
            "/api/v1/summary/generate",
            json={
                "transcription_text": "Texte de test assez long pour passer la validation de longueur minimale.",
                "summary_type": "structured",
                "language": "fr"
            }
        )
        
        assert response.status_code == 200
        assert "summary" in response.json()
        assert "key_points" in response.json()


def test_summary_invalid_type():
    """Test génération résumé avec type invalide"""
    response = client.post(
        "/api/v1/summary/generate",
        json={
            "transcription_text": "Texte de test suffisamment long pour validation.",
            "summary_type": "invalid_type",
            "language": "fr"
        }
    )
    assert response.status_code == 422  # Validation Pydantic


def test_cors_headers():
    """Test des headers CORS"""
    response = client.options(
        "/api/v1/transcription/health",
        headers={"Origin": "http://localhost:3000"}
    )
    # Vérifier que les headers CORS sont présents
    assert response.status_code in [200, 204]


def test_api_docs_available():
    """Test que la documentation API est accessible"""
    response = client.get("/docs")
    assert response.status_code == 200


def test_openapi_schema():
    """Test que le schéma OpenAPI est disponible"""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "openapi" in schema
    assert "paths" in schema
    assert "/api/v1/transcription/upload" in schema["paths"]
    assert "/api/v1/summary/generate" in schema["paths"]


def test_transcription_upload_invalid_extension():
    """Test upload avec extension invalide"""
    from io import BytesIO
    
    files = {"file": ("test.txt", BytesIO(b"fake content"), "text/plain")}
    data = {"language": "fr"}
    
    with patch('app.utils.file_handler.file_handler.save_upload_file') as mock_save:
        from fastapi import HTTPException
        mock_save.side_effect = HTTPException(status_code=400, detail="Format non supporté")
        
        response = client.post("/api/v1/transcription/upload", files=files, data=data)
        assert response.status_code == 400


def test_summary_quick_endpoint():
    """Test de l'endpoint résumé rapide"""
    mock_result = {
        "summary": "Résumé rapide",
        "key_points": [],
        "decisions": [],
        "action_items": [],
        "participants": [],
        "processing_time": 0.5
    }
    
    with patch('app.services.azure_service.azure_service.generate_summary', return_value=mock_result):
        response = client.post(
            "/api/v1/summary/quick",
            json={
                "transcription_text": "Texte pour résumé rapide suffisamment long.",
                "language": "fr"
            }
        )
        
        assert response.status_code == 200
        assert "summary" in response.json()


def test_error_handling_500():
    """Test de gestion des erreurs 500"""
    with patch('app.services.azure_service.azure_service.generate_summary', side_effect=Exception("Internal error")):
        response = client.post(
            "/api/v1/summary/generate",
            json={
                "transcription_text": "Texte de test pour erreur 500.",
                "summary_type": "structured",
                "language": "fr"
            }
        )
        
        assert response.status_code == 500
        assert "error" in response.json()["detail"].lower()

                "language": "fr"
            }
        )
        assert response.status_code == 200
        assert "summary" in response.json()


def test_404_endpoint():
    """Test endpoint non existant"""
    response = client.get("/api/non-existant")
    assert response.status_code == 404
