/**
 * Composant TranscriptionResult
 * Affiche le résultat de la transcription avec options d'export
 */
import { useState } from 'react';
import { Copy, Download, FileText, Loader2 } from 'lucide-react';

const TranscriptionResult = ({ transcription, onGenerateSummary, summary, isLoadingSummary }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(transcription.text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const blob = new Blob([transcription.text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `transcription-${transcription.id}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="transcription-result">
      {/* Métadonnées */}
      <div className="result-header">
        <h2>📝 Transcription</h2>
        <div className="metadata">
          <span>🌍 Langue: {transcription.language.toUpperCase()}</span>
          <span>📊 Mots: {transcription.word_count}</span>
          <span>⏱️ Traité en {transcription.processing_time_seconds.toFixed(2)}s</span>
          {transcription.duration_seconds && (
            <span>🎙️ Durée: {Math.floor(transcription.duration_seconds)}s</span>
          )}
        </div>
      </div>

      {/* Texte transcrit */}
      <div className="transcription-text">
        <p>{transcription.text}</p>
      </div>

      {/* Actions */}
      <div className="result-actions">
        <button className="btn-secondary" onClick={handleCopy}>
          <Copy size={16} />
          {copied ? 'Copié !' : 'Copier'}
        </button>
        
        <button className="btn-secondary" onClick={handleDownload}>
          <Download size={16} />
          Télécharger
        </button>

        <button
          className="btn-primary"
          onClick={onGenerateSummary}
          disabled={isLoadingSummary}
        >
          {isLoadingSummary ? (
            <>
              <Loader2 size={16} className="spin" />
              Génération...
            </>
          ) : (
            <>
              <FileText size={16} />
              Générer un résumé
            </>
          )}
        </button>
      </div>

      {/* Résumé si disponible */}
      {summary && (
        <div className="summary-result">
          <h3>📋 Résumé Structuré</h3>
          
          <div className="summary-content">
            {/* Points clés */}
            {summary.key_points.length > 0 && (
              <div className="summary-section">
                <h4>🎯 Points Clés</h4>
                <ul>
                  {summary.key_points.map((point, idx) => (
                    <li key={idx}>{point}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Décisions */}
            {summary.decisions.length > 0 && (
              <div className="summary-section">
                <h4>✅ Décisions Prises</h4>
                <ul>
                  {summary.decisions.map((decision, idx) => (
                    <li key={idx}>{decision}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Actions */}
            {summary.action_items.length > 0 && (
              <div className="summary-section">
                <h4>📋 Actions à Mener</h4>
                <ul>
                  {summary.action_items.map((action, idx) => (
                    <li key={idx}>{action}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Participants */}
            {summary.participants.length > 0 && (
              <div className="summary-section">
                <h4>👥 Participants Mentionnés</h4>
                <div className="participants">
                  {summary.participants.map((participant, idx) => (
                    <span key={idx} className="participant-tag">{participant}</span>
                  ))}
                </div>
              </div>
            )}

            {/* Résumé complet */}
            <div className="summary-section">
              <h4>📄 Résumé Complet</h4>
              <div className="summary-full-text">
                {summary.summary}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TranscriptionResult;
