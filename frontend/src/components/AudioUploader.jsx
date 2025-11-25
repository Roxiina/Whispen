/**
 * Composant AudioUploader
 * Permet d'uploader un fichier audio ou d'enregistrer depuis le micro
 */
import { useState, useRef } from 'react';
import { Upload, Mic, MicOff, Loader2 } from 'lucide-react';

const AudioUploader = ({ onTranscriptionComplete, isLoading }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [selectedFile, setSelectedFile] = useState(null);
  
  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);
  const timerRef = useRef(null);
  const fileInputRef = useRef(null);

  // Gestion de l'upload de fichier
  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
    }
  };

  const handleUpload = () => {
    if (selectedFile) {
      onTranscriptionComplete(selectedFile);
      setSelectedFile(null);
    }
  };

  // Gestion de l'enregistrement
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      
      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
        const file = new File([blob], `recording-${Date.now()}.webm`, { type: 'audio/webm' });
        onTranscriptionComplete(file);
        
        // Arrêter le stream
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
      setRecordingTime(0);

      // Timer
      timerRef.current = setInterval(() => {
        setRecordingTime((prev) => prev + 1);
      }, 1000);

    } catch (error) {
      console.error('Erreur accès micro:', error);
      alert('Impossible d\'accéder au microphone. Vérifiez les permissions.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      clearInterval(timerRef.current);
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="audio-uploader">
      {/* Upload de fichier */}
      <div className="upload-section">
        <input
          ref={fileInputRef}
          type="file"
          accept="audio/*"
          onChange={handleFileSelect}
          style={{ display: 'none' }}
          disabled={isLoading}
        />
        
        <button
          className="btn-upload"
          onClick={() => fileInputRef.current?.click()}
          disabled={isLoading || isRecording}
        >
          <Upload size={20} />
          Choisir un fichier audio
        </button>

        {selectedFile && (
          <div className="file-preview">
            <span className="file-name">📎 {selectedFile.name}</span>
            <button
              className="btn-primary"
              onClick={handleUpload}
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <Loader2 size={16} className="spin" />
                  Transcription...
                </>
              ) : (
                'Transcrire'
              )}
            </button>
          </div>
        )}
      </div>

      <div className="divider">
        <span>OU</span>
      </div>

      {/* Enregistrement micro */}
      <div className="recording-section">
        {!isRecording ? (
          <button
            className="btn-record"
            onClick={startRecording}
            disabled={isLoading}
          >
            <Mic size={20} />
            Enregistrer depuis le micro
          </button>
        ) : (
          <div className="recording-controls">
            <div className="recording-indicator">
              <span className="pulse-dot"></span>
              <span className="recording-text">
                Enregistrement... {formatTime(recordingTime)}
              </span>
            </div>
            <button className="btn-stop" onClick={stopRecording}>
              <MicOff size={20} />
              Arrêter
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default AudioUploader;
