import React, { useState } from 'react';

const App = () => {
  const [passage, setPassage] = useState('');
  const [hebrew, setHebrew] = useState('');
  const [english, setEnglish] = useState('');
  const [aiCommentary, setAiCommentary] = useState('');
  const [perspective, setPerspective] = useState('Secular');
  const [loadingPassage, setLoadingPassage] = useState(false);
  const [loadingCommentary, setLoadingCommentary] = useState(false);
  const [error, setError] = useState('');

  const backendUrl = ''; // Leave empty for relative path to the backend.

  const fetchPassage = async () => {
    setLoadingPassage(true);
    setError('');
    try {
      const response = await fetch(`${backendUrl}/api/get_passage?passage=${encodeURIComponent(passage.trim())}`);
      const data = await response.json();
      if (data.error) {
        setError(data.error);
      } else {
        setHebrew(data.hebrew);
        setEnglish(data.english);
      }
    } catch (err) {
      setError('Error fetching passage. Please try again.');
      console.error(err);
    } finally {
      setLoadingPassage(false);
    }
  };

  const fetchAiCommentary = async () => {
    setLoadingCommentary(true);
    setError('');
    try {
      const response = await fetch(
        `${backendUrl}/api/get_ai_commentary?passage=${encodeURIComponent(passage.trim())}&perspective=${perspective}`
      );
      const data = await response.json();
      if (data.error) {
        setError(data.error);
      } else {
        setAiCommentary(data.commentary);
      }
    } catch (err) {
      setError('Error fetching AI commentary. Please try again.');
      console.error(err);
    } finally {
      setLoadingCommentary(false);
    }
  };

  return (
    <div className="App" style={{ padding: '20px', maxWidth: '800px', margin: 'auto' }}>
      <h1>TorahLens</h1>
      <div>
        <input
          type="text"
          value={passage}
          onChange={(e) => setPassage(e.target.value)}
          placeholder="Enter passage (e.g., Genesis 1:1)"
          style={{ marginRight: '10px', padding: '5px', width: '250px' }}
        />
        <button onClick={fetchPassage} disabled={loadingPassage} style={{ marginRight: '10px' }}>
          {loadingPassage ? 'Loading...' : 'Get Passage'}
        </button>
      </div>

      <div style={{ marginTop: '20px' }}>
        <h3>AI Commentary Perspective</h3>
        {['Secular', 'Religious', 'Philosophical'].map((perspectiveOption) => (
          <label key={perspectiveOption} style={{ marginRight: '10px' }}>
            <input
              type="radio"
              value={perspectiveOption}
              checked={perspective === perspectiveOption}
              onChange={() => setPerspective(perspectiveOption)}
            />
            {perspectiveOption}
          </label>
        ))}
        <button 
          onClick={fetchAiCommentary} 
          disabled={!english || loadingCommentary}
          style={{ marginLeft: '10px' }}
        >
          {loadingCommentary ? 'Generating...' : 'Get AI Commentary'}
        </button>
      </div>

      {error && <div style={{ color: 'red', margin: '10px 0' }}>{error}</div>}

      {english && (
        <div style={{ margin: '20px 0' }}>
          <h2>Hebrew Text:</h2>
          <div style={{ direction: 'rtl', textAlign: 'right' }}>{hebrew}</div>
          <h2>English Translation:</h2>
          <div>{english}</div>
        </div>
      )}

      {aiCommentary && (
        <div style={{ margin: '20px 0', border: '1px solid #ddd', padding: '15px', borderRadius: '5px' }}>
          <h2>AI Commentary ({perspective} Perspective):</h2>
          <p>{aiCommentary}</p>
        </div>
      )}
    </div>
  );
};

export default App;

