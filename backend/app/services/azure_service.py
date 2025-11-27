"""
Service Azure OpenAI pour transcription et résumé
Gère les appels à Whisper (local ou OpenAI) et GPT-4 (Azure)
"""

from openai import AzureOpenAI, OpenAI
from app.config import settings
import logging
import time
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# Import conditionnel de faster-whisper
try:
    from faster_whisper import WhisperModel
    FASTER_WHISPER_AVAILABLE = True
except ImportError:
    FASTER_WHISPER_AVAILABLE = False
    logger.warning("⚠️ faster-whisper not installed, local transcription unavailable")


class AzureOpenAIService:
    """Service pour interagir avec Azure OpenAI et Whisper local"""
    
    def __init__(self):
        """Initialise les clients Azure OpenAI, OpenAI et Whisper local"""
        try:
            # Client Azure OpenAI pour GPT-4 (résumé)
            self.azure_client = AzureOpenAI(
                api_key=settings.AZURE_OPENAI_API_KEY,
                api_version=settings.AZURE_OPENAI_API_VERSION,
                azure_endpoint=settings.AZURE_OPENAI_ENDPOINT
            )
            logger.info("✅ Azure OpenAI client initialized successfully")
            
            # Client OpenAI standard pour Whisper (transcription)
            if settings.USE_OPENAI_WHISPER:
                self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
                logger.info("✅ OpenAI client initialized for Whisper")
            else:
                self.openai_client = None
            
            # Modèle Whisper local avec faster-whisper
            if settings.USE_LOCAL_WHISPER:
                if not FASTER_WHISPER_AVAILABLE:
                    error_msg = "faster-whisper is not installed. Install it with: pip install faster-whisper==1.1.0"
                    logger.error(f"❌ {error_msg}")
                    raise ImportError(error_msg)
                    
                logger.info(f"🔄 Loading Whisper model '{settings.WHISPER_MODEL_SIZE}'...")
                try:
                    self.whisper_model = WhisperModel(
                        settings.WHISPER_MODEL_SIZE,
                        device="cpu",  # Utilise CPU (changez en "cuda" si GPU disponible)
                        compute_type="int8"  # Optimisation pour CPU
                    )
                    logger.info("✅ Local Whisper model loaded successfully")
                except Exception as model_error:
                    logger.error(f"❌ Failed to load Whisper model: {model_error}")
                    raise
            else:
                self.whisper_model = None
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize clients: {e}")
            raise
    
    async def transcribe_audio(
        self, 
        audio_file_path: str, 
        language: Optional[str] = "fr"
    ) -> Dict[str, Any]:
        """
        Transcrit un fichier audio avec Whisper (local ou OpenAI)
        
        Args:
            audio_file_path: Chemin vers le fichier audio
            language: Code langue (fr, en, etc.)
        
        Returns:
            Dict contenant le texte transcrit et les métadonnées
        """
        start_time = time.time()
        
        try:
            logger.info(f"🎤 Starting transcription for: {audio_file_path}")
            
            # Option 1: Whisper local avec faster-whisper
            if settings.USE_LOCAL_WHISPER and self.whisper_model:
                segments, info = self.whisper_model.transcribe(
                    audio_file_path,
                    language=language,
                    beam_size=5,
                    vad_filter=True  # Voice Activity Detection pour meilleure qualité
                )
                
                # Reconstruction du texte complet
                text = " ".join([segment.text for segment in segments])
                duration = info.duration
                detected_language = info.language
                
                processing_time = time.time() - start_time
                
                result = {
                    "text": text,
                    "language": detected_language,
                    "duration": duration,
                    "processing_time": processing_time,
                    "word_count": len(text.split())
                }
                
                logger.info(f"✅ Local transcription completed in {processing_time:.2f}s - {result['word_count']} words")
                return result
            
            # Option 2: OpenAI API Whisper
            elif settings.USE_OPENAI_WHISPER and self.openai_client:
                with open(audio_file_path, "rb") as audio_file:
                    transcript = self.openai_client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        language=language,
                        response_format="verbose_json"
                    )
                
                processing_time = time.time() - start_time
                
                result = {
                    "text": transcript.text,
                    "language": transcript.language if hasattr(transcript, 'language') else language,
                    "duration": transcript.duration if hasattr(transcript, 'duration') else None,
                    "processing_time": processing_time,
                    "word_count": len(transcript.text.split())
                }
                
                logger.info(f"✅ OpenAI transcription completed in {processing_time:.2f}s - {result['word_count']} words")
                return result
            
            else:
                error_msg = (
                    "No transcription method available. "
                    f"USE_LOCAL_WHISPER={settings.USE_LOCAL_WHISPER}, "
                    f"USE_OPENAI_WHISPER={settings.USE_OPENAI_WHISPER}, "
                    f"whisper_model={'Loaded' if self.whisper_model else 'None'}, "
                    f"openai_client={'Loaded' if self.openai_client else 'None'}"
                )
                logger.error(f"❌ {error_msg}")
                raise Exception(error_msg)
            
        except Exception as e:
            logger.error(f"❌ Transcription failed: {str(e)}")
            raise Exception(f"Erreur lors de la transcription: {str(e)}")
    
    async def generate_summary(
        self, 
        transcription_text: str, 
        summary_type: str = "structured",
        language: str = "fr"
    ) -> Dict[str, Any]:
        """
        Génère un résumé structuré avec GPT-4
        
        Args:
            transcription_text: Texte à résumer
            summary_type: Type de résumé (structured, bullet_points, short)
            language: Langue du résumé
        
        Returns:
            Dict contenant le résumé et les éléments structurés
        """
        start_time = time.time()
        
        try:
            logger.info(f"📝 Starting summarization (type: {summary_type})")
            
            # Prompt adapté selon le type de résumé
            system_prompt = self._get_summary_prompt(summary_type, language)
            
            # Appel à GPT-4 via Azure
            response = self.azure_client.chat.completions.create(
                model=settings.AZURE_GPT4_DEPLOYMENT_NAME,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": transcription_text}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            summary_text = response.choices[0].message.content
            processing_time = time.time() - start_time
            
            # Parse du résumé structuré
            parsed_summary = self._parse_structured_summary(summary_text)
            parsed_summary["processing_time"] = processing_time
            
            logger.info(f"✅ Summary generated in {processing_time:.2f}s")
            return parsed_summary
            
        except Exception as e:
            logger.error(f"❌ Summarization failed: {str(e)}")
            raise Exception(f"Erreur lors de la génération du résumé: {str(e)}")
    
    def _get_summary_prompt(self, summary_type: str, language: str) -> str:
        """Retourne le prompt système selon le type de résumé"""
        
        prompts = {
            "structured": {
                "fr": """Tu es un assistant expert en résumé de réunions. 
Analyse la transcription suivante et génère un résumé structuré en français avec :

## 📌 Résumé Général
[Un paragraphe de synthèse]

## 🎯 Points Clés
- [Point 1]
- [Point 2]
- [Point 3]

## ✅ Décisions Prises
- [Décision 1]
- [Décision 2]

## 📋 Actions à Mener
- [Action 1 - Responsable si mentionné]
- [Action 2]

## 👥 Participants Mentionnés
- [Nom 1]
- [Nom 2]

Sois précis, concis et professionnel.""",
                "en": """You are an expert meeting summarizer.
Analyze the following transcription and generate a structured summary in English with:

## 📌 General Summary
[One paragraph synthesis]

## 🎯 Key Points
- [Point 1]
- [Point 2]

## ✅ Decisions Made
- [Decision 1]

## 📋 Action Items
- [Action 1 - Owner if mentioned]

## 👥 Participants Mentioned
- [Name 1]

Be precise, concise and professional."""
            },
            "bullet_points": {
                "fr": "Tu es un assistant de prise de notes. Résume cette transcription en 5-10 points clés sous forme de liste à puces. Sois concis et va à l'essentiel.",
                "en": "You are a note-taking assistant. Summarize this transcription in 5-10 key bullet points. Be concise and to the point."
            },
            "short": {
                "fr": "Résume cette transcription en 2-3 phrases maximum. Capture l'essentiel uniquement.",
                "en": "Summarize this transcription in 2-3 sentences maximum. Capture only the essence."
            }
        }
        
        return prompts.get(summary_type, prompts["structured"]).get(language, prompts["structured"]["fr"])
    
    def _parse_structured_summary(self, summary_text: str) -> Dict[str, Any]:
        """Parse le résumé structuré pour extraire les sections"""
        
        result = {
            "summary": summary_text,
            "key_points": [],
            "decisions": [],
            "action_items": [],
            "participants": []
        }
        
        try:
            lines = summary_text.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                
                # Détection des sections
                if "Points Clés" in line or "Key Points" in line:
                    current_section = "key_points"
                elif "Décisions" in line or "Decisions" in line:
                    current_section = "decisions"
                elif "Actions" in line or "Action Items" in line:
                    current_section = "action_items"
                elif "Participants" in line:
                    current_section = "participants"
                elif line.startswith("##"):
                    current_section = None
                # Extraction des items (lignes commençant par - ou •)
                elif line.startswith(("- ", "• ", "* ")) and current_section:
                    item = line[2:].strip()
                    if item:
                        result[current_section].append(item)
            
        except Exception as e:
            logger.warning(f"⚠️ Could not fully parse structured summary: {e}")
        
        return result
    
    async def check_connection(self) -> bool:
        """Vérifie la connexion à Azure OpenAI"""
        try:
            # Test simple avec un appel minimal
            response = self.azure_client.chat.completions.create(
                model=settings.AZURE_GPT4_DEPLOYMENT_NAME,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            return True
        except Exception as e:
            logger.error(f"❌ Azure OpenAI connection check failed: {e}")
            return False


# Instance globale du service
azure_service = AzureOpenAIService()
