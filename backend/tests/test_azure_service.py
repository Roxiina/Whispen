"""
Tests unitaires pour azure_service.py
"""
import pytest
from unittest.mock import Mock, patch, MagicMock, mock_open
from app.services.azure_service import AzureOpenAIService
import time


@pytest.fixture
def mock_whisper_model():
    """Fixture pour mocker le modèle Whisper local"""
    mock_model = MagicMock()
    mock_segment = MagicMock()
    mock_segment.text = "Ceci est un test"
    
    mock_info = MagicMock()
    mock_info.duration = 10.5
    mock_info.language = "fr"
    
    mock_model.transcribe.return_value = ([mock_segment], mock_info)
    return mock_model


@pytest.mark.asyncio
async def test_transcribe_audio_local_success(mock_whisper_model):
    """Test de transcription locale réussie avec faster-whisper"""
    with patch('app.services.azure_service.FASTER_WHISPER_AVAILABLE', True):
        with patch('app.services.azure_service.WhisperModel', return_value=mock_whisper_model):
            service = AzureOpenAIService()
            service.whisper_model = mock_whisper_model
            
            # Mock du fichier audio
            with patch('builtins.open', mock_open(read_data=b'fake audio data')):
                result = await service.transcribe_audio("test.mp3", "fr")
    
    assert "text" in result
    assert result["language"] == "fr"
    assert result["duration"] == 10.5
    assert result["word_count"] > 0
    assert "processing_time" in result


@pytest.mark.asyncio
async def test_transcribe_audio_openai_api():
    """Test de transcription via OpenAI API"""
    mock_transcript = Mock()
    mock_transcript.text = "Ceci est un test de transcription via API."
    mock_transcript.language = "fr"
    mock_transcript.duration = 15.2
    
    with patch('app.services.azure_service.OpenAI') as mock_openai:
        mock_client = MagicMock()
        mock_client.audio.transcriptions.create.return_value = mock_transcript
        mock_openai.return_value = mock_client
        
        service = AzureOpenAIService()
        service.openai_client = mock_client
        
        with patch('builtins.open', mock_open(read_data=b'fake audio')):
            result = await service.transcribe_audio("test.mp3", "fr")
    
    assert result["text"] == "Ceci est un test de transcription via API."
    assert result["word_count"] == 8


@pytest.mark.asyncio
async def test_transcribe_audio_error_handling():
    """Test de gestion d'erreur lors de la transcription"""
    service = AzureOpenAIService()
    service.whisper_model = None
    service.openai_client = None
    
    with pytest.raises(Exception) as exc_info:
        await service.transcribe_audio("nonexistent.mp3", "fr")
    
    assert "transcription" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_generate_summary_structured():
    """Test de génération de résumé structuré"""
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = """## 📌 Résumé Général
Réunion de planification du projet Whispen.

## 🎯 Points Clés
- Intégration de Whisper local
- Configuration Azure OpenAI
- Tests unitaires à compléter

## ✅ Décisions Prises
- Utiliser faster-whisper pour la transcription
- GPT-4o-mini pour les résumés

## 📋 Actions à Mener
- Compléter les tests - Équipe Dev
- Documenter l'API - Tech Lead
"""
    
    with patch('app.services.azure_service.AzureOpenAI') as mock_azure:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_azure.return_value = mock_client
        
        service = AzureOpenAIService()
        service.azure_client = mock_client
        
        result = await service.generate_summary(
            "Transcription de la réunion...",
            summary_type="structured",
            language="fr"
        )
    
    assert "summary" in result
    assert "key_points" in result
    assert "decisions" in result
    assert "action_items" in result
    assert "processing_time" in result


@pytest.mark.asyncio
async def test_generate_summary_bullet_points():
    """Test de résumé en points clés"""
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = "- Point 1\n- Point 2\n- Point 3"
    
    with patch('app.services.azure_service.AzureOpenAI') as mock_azure:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_azure.return_value = mock_client
        
        service = AzureOpenAIService()
        service.azure_client = mock_client
        
        result = await service.generate_summary(
            "Texte court",
            summary_type="bullet_points",
            language="fr"
        )
    
    assert "summary" in result
    assert "Point 1" in result["summary"]


@pytest.mark.asyncio
async def test_generate_summary_short():
    """Test de résumé court"""
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = "Résumé très court en 2 phrases."
    
    with patch('app.services.azure_service.AzureOpenAI') as mock_azure:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_azure.return_value = mock_client
        
        service = AzureOpenAIService()
        service.azure_client = mock_client
        
        result = await service.generate_summary(
            "Texte à résumer",
            summary_type="short",
            language="en"
        )
    
    assert "summary" in result
    assert len(result["summary"]) < 200


@pytest.mark.asyncio
async def test_check_connection_success():
    """Test de vérification de connexion réussie"""
    mock_response = Mock()
    mock_response.choices = [Mock()]
    
    with patch('app.services.azure_service.AzureOpenAI') as mock_azure:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_azure.return_value = mock_client
        
        service = AzureOpenAIService()
        service.azure_client = mock_client
        
        result = await service.check_connection()
    
    assert result is True


@pytest.mark.asyncio
async def test_check_connection_failure():
    """Test de vérification de connexion échouée"""
    with patch('app.services.azure_service.AzureOpenAI') as mock_azure:
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("Connection failed")
        mock_azure.return_value = mock_client
        
        service = AzureOpenAIService()
        service.azure_client = mock_client
        
        result = await service.check_connection()
    
    assert result is False


def test_get_summary_prompt():
    """Test de génération des prompts système"""
    service = AzureOpenAIService()
    
    # Test prompt structuré
    prompt_structured = service._get_summary_prompt("structured", "fr")
    assert "Résumé Général" in prompt_structured
    assert "Points Clés" in prompt_structured
    
    # Test prompt bullet points
    prompt_bullets = service._get_summary_prompt("bullet_points", "en")
    assert "bullet" in prompt_bullets.lower() or "points" in prompt_bullets.lower()
    
    # Test prompt court
    prompt_short = service._get_summary_prompt("short", "fr")
    assert "court" in prompt_short.lower() or "sentences" in prompt_short.lower()


def test_parse_structured_summary():
    """Test du parsing de résumé structuré"""
    service = AzureOpenAIService()
    
    summary_text = """## 📌 Résumé Général
Réunion importante

## 🎯 Points Clés
- Premier point
- Deuxième point

## ✅ Décisions Prises
- Décision A
- Décision B

## 📋 Actions à Mener
- Action 1 - Responsable A
- Action 2 - Responsable B

## 👥 Participants
- Alice
- Bob
"""
    
    result = service._parse_structured_summary(summary_text)
    
    assert "summary" in result
    assert len(result["key_points"]) == 2
    assert len(result["decisions"]) == 2
    assert len(result["action_items"]) == 2
    assert len(result["participants"]) == 2
    assert "Premier point" in result["key_points"]
    assert "Décision A" in result["decisions"]

        result = await service.generate_summary("Texte à résumer", "structured", "fr")
    
    assert len(result["key_points"]) == 2
    assert len(result["decisions"]) == 1
    assert len(result["action_items"]) == 1


@pytest.mark.asyncio
async def test_check_connection_success():
    """Test de vérification de connexion"""
    service = AzureOpenAIService()
    
    mock_response = Mock()
    mock_response.choices = [Mock()]
    
    with patch.object(service.client.chat.completions, 'create', return_value=mock_response):
        is_connected = await service.check_connection()
    
    assert is_connected is True


@pytest.mark.asyncio
async def test_transcribe_audio_failure():
    """Test de transcription échouée"""
    service = AzureOpenAIService()
    
    with patch.object(service.client.audio.transcriptions, 'create', side_effect=Exception("API Error")):
        with patch('builtins.open', create=True):
            with pytest.raises(Exception, match="Erreur lors de la transcription"):
                await service.transcribe_audio("test.mp3", "fr")
