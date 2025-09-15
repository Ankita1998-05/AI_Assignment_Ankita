import { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [transcript, setTranscript] = useState('');
  const [summary, setSummary] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const handleUpload = async () => {
    setTranscript('');
    setSummary('');
    setError('');

    if (!file) {
      setError('Please select an audio file first.');
      return;
    }

    setLoading(true);

    const formData = new FormData();
    formData.append('audio_file', file);
    try {
      const response = await axios.post('http://localhost:8000/summarize_audio/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      // Update state with the data from the backend
      setTranscript(response.data.transcript);
      setSummary(response.data.summary);

    } catch (err) {
      console.error('Error uploading file:', err);
      // Display a user-friendly error message
      setError('Failed to process the audio. Please try again.');

    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <header>
        <h1>AI Meeting Intelligence Platform: Post meeting Analysis</h1>
        <p>Upload an audio file (.mp3, .mp4, .wav) to get a summarized transcript.</p>
      </header>
      
      <div className="upload-section">
        <input type="file" onChange={handleFileChange} accept=".mp3,.mp4,.wav" />
        <button onClick={handleUpload} disabled={loading || !file}>
          {loading ? 'Processing...' : 'Summarize Speech'}
        </button>
      </div>

      {error && <p className="error-message">{error}</p>}
      
      {loading && <p>Processing your audio, this may take a moment...</p>}

      {transcript && (
        <section className="results-section">
          <h2>Full Transcript</h2>
          <pre className="transcript-box">{transcript}</pre>
        </section>
      )}

      {summary && (
        <section className="results-section">
          <h2>Summary</h2>
          <div className="summary-box">
            {summary.split('\n').map((point, index) => (
              <p key={index}>{point}</p>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}

export default App;
