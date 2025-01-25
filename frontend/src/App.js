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
    <div className="app-container">
      <header className="app-header">
        <h1>ToraLens</h1>
      </header>
      <main className="app-main">
        <div className="input-section">
          <input
            type="text"
            value={passage}
            onChange={(e) => setPassage(e.target.value)}
            placeholder="Enter passage (e.g., Genesis 1:1)"
            className="input-field"
          />
          <button onClick={fetchPassage} disabled={loadingPassage} className="button-primary">
            {loadingPassage ? 'Loading...' : 'Get Passage'}
          </button>
        </div>

        <div className="perspective-section">
          <h3>AI Commentary Perspective</h3>
          {['Secular', 'Religious', 'Philosophical'].map((perspectiveOption) => (
            <label key={perspectiveOption} className="radio-label">
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
            className="button-secondary"
          >
            {loadingCommentary ? 'Generating...' : 'Get AI Commentary'}
          </button>
        </div>

        {error && <div className="error-message">{error}</div>}

        {english && (
          <div className="passage-section">
            <h2>Hebrew Text:</h2>
            <div className="hebrew-text">{hebrew}</div>
            <h2>English Translation:</h2>
            <div className="english-text">{english}</div>
          </div>
        )}

        {aiCommentary && (
          <div className="commentary-section">
            <h2>AI Commentary ({perspective} Perspective):</h2>
            <p>{aiCommentary}</p>
          </div>
        )}
      </main>
      <footer className="app-footer">
        <p>Made with love for Torah and technology.</p>
      </footer>
    </div>
  );
};

export default App;

/** CSS styles **/

const styles = `
body {
  font-family: 'Alef', sans-serif;
  margin: 0;
  background-color: #f5f5f5;
  color: #333;
}

.app-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
}

.app-header {
  background-color: #0038b8;
  color: white;
  width: 100%;
  text-align: center;
  padding: 15px 0;
  box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.1);
}

.app-main {
  max-width: 800px;
  width: 100%;
  background: white;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  margin: 20px 0;
}

.input-section, .perspective-section, .passage-section, .commentary-section {
  margin-bottom: 20px;
}

.input-field {
  padding: 10px;
  font-size: 16px;
  border: 1px solid #ccc;
  border-radius: 5px;
  width: 70%;
}

.button-primary, .button-secondary {
  padding: 10px 15px;
  font-size: 16px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.button-primary {
  background-color: #0056e6;
  color: white;
}

.button-secondary {
  background-color: #28a745;
  color: white;
}

.radio-label {
  margin-right: 15px;
  font-size: 14px;
  cursor: pointer;
}

.hebrew-text {
  direction: rtl;
  text-align: right;
  font-size: 18px;
  color: #0056e6;
}

.english-text {
  font-size: 18px;
}

.error-message {
  color: red;
  font-weight: bold;
  margin-top: 10px;
}

.app-footer {
  text-align: center;
  padding: 10px 0;
  background-color: #0038b8;
  color: white;
  width: 100%;
  position: fixed;
  bottom: 0;
}
`;

document.head.insertAdjacentHTML("beforeend", `<style>${styles}</style>`);

