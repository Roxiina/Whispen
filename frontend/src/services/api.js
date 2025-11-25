/**
 * Service API pour communiquer avec le backend Whispen
 */
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000, // 2 minutes pour les transcriptions longues
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Transcrit un fichier audio
 * @param {File} file - Fichier audio
 * @param {string} language - Code langue (fr, en, etc.)
 * @returns {Promise} Réponse avec transcription
 */
export const transcribeAudio = async (file, language = 'fr') => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('language', language);

  const response = await api.post('/api/v1/transcription/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};

/**
 * Génère un résumé structuré
 * @param {string} text - Texte à résumer
 * @param {string} summaryType - Type de résumé (structured, bullet_points, short)
 * @param {string} language - Langue du résumé
 * @returns {Promise} Réponse avec résumé
 */
export const generateSummary = async (text, summaryType = 'structured', language = 'fr') => {
  const response = await api.post('/api/v1/summary/generate', {
    transcription_text: text,
    summary_type: summaryType,
    language: language,
  });

  return response.data;
};

/**
 * Vérifie la santé de l'API
 * @returns {Promise} Status de l'API
 */
export const checkHealth = async () => {
  const response = await api.get('/health');
  return response.data;
};

export default api;
