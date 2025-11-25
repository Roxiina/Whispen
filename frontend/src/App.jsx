/**
 * Application principale Whispen
 */
import { useState, useEffect } from 'react';
import AudioUploader from './components/AudioUploader';
import TranscriptionResult from './components/TranscriptionResult';
import { transcribeAudio, generateSummary, checkHealth } from './services/api';
import { Mic2, AlertCircle } from 'lucide-react';
import './App.css';

function App() {
  const [transcription, setTranscription] = useState(null);
  const [summary, setSummary] = useState(null);
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [isSummarizing, setIsSummarizing] = useState(false);
  const [error, setError] = useState(null);
  const [apiStatus, setApiStatus] = useState(null);
  const [language, setLanguage] = useState('fr');

  // Vérification de la santé de l'API au chargement
  useEffect(() => {
    const verifyAPI = async () => {
      try {
        const status = await checkHealth();
        setApiStatus(status);
      } catch (err) {
        console.error('API non disponible:', err);
        setApiStatus({ status: 'unavailable' });
      }
    };
    verifyAPI();
  }, []);

  // Gestion de la transcription
  const handleTranscription = async (file) => {
    setIsTranscribing(true);
    setError(null);
    setTranscription(null);
    setSummary(null);

    try {
      const result = await transcribeAudio(file, language);
      setTranscription(result);
    } catch (err) {
      console.error('Erreur transcription:', err);
      setError(err.response?.data?.detail || 'Erreur lors de la transcription');
    } finally {
      setIsTranscribing(false);
    }
  };

  // Gestion de la génération de résumé
  const handleSummaryGeneration = async () => {
    if (!transcription) return;

    setIsSummarizing(true);
    setError(null);

    try {
      const result = await generateSummary(transcription.text, 'structured', language);
      setSummary(result);
    } catch (err) {
      console.error('Erreur résumé:', err);
      setError(err.response?.data?.detail || 'Erreur lors de la génération du résumé');
    } finally {
      setIsSummarizing(false);
    }
  };

  // Réinitialisation
  const handleReset = () => {
    setTranscription(null);
    setSummary(null);
    setError(null);
  };

  return (
    <div className="app">
      {/* Header */}
      <header className="app-header">
        <div className="header-content">
          <div className="logo">
            <Mic2 size={32} />
            <h1>Whispen</h1>
          </div>
          <p className="tagline">Transcription et résumé de réunions propulsé par IA</p>
        </div>

        {/* Sélecteur de langue */}
        <div className="language-selector">
          <label>Langue :</label>
          <select value={language} onChange={(e) => setLanguage(e.target.value)}>
            <option value="fr">🇫🇷 Français</option>
            <option value="en">🇬🇧 English</option>
            <option value="es">🇪🇸 Español</option>
            <option value="de">🇩🇪 Deutsch</option>
            <option value="it">🇮🇹 Italiano</option>
          </select>
        </div>

        {/* Status API */}
        {apiStatus && (
          <div className={`api-status ${apiStatus.status === 'healthy' ? 'healthy' : 'error'}`}>
            {apiStatus.status === 'healthy' ? '✅ API opérationnelle' : '❌ API indisponible'}
          </div>
        )}
      </header>

      {/* Contenu principal */}
      <main className="app-main">
        <div className="container">
          {/* Erreur */}
          {error && (
            <div className="error-banner">
              <AlertCircle size={20} />
              <span>{error}</span>
              <button onClick={() => setError(null)}>✕</button>
            </div>
          )}

          {/* Uploader ou Résultat */}
          {!transcription ? (
            <div className="upload-container">
              <h2>📤 Envoyer un fichier audio</h2>
              <p className="help-text">
                Formats supportés : MP3, WAV, M4A, FLAC, OGG, WEBM<br />
                Taille maximale : 200 MB
              </p>
              <AudioUploader
                onTranscriptionComplete={handleTranscription}
                isLoading={isTranscribing}
              />
            </div>
          ) : (
            <>
              <TranscriptionResult
                transcription={transcription}
                summary={summary}
                onGenerateSummary={handleSummaryGeneration}
                isLoadingSummary={isSummarizing}
              />
              
              <div className="reset-section">
                <button className="btn-secondary" onClick={handleReset}>
                  ← Nouvelle transcription
                </button>
              </div>
            </>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="app-footer">
        <p>
          Propulsé par <strong>Azure OpenAI</strong> (Whisper + GPT-4) |{' '}
          <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer">
            Documentation API
          </a>
        </p>
      </footer>
    </div>
  );
}

export default App;
